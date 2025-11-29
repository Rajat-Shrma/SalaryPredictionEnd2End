import os
import joblib
from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

MODEL_PATH = (
    r"C:\Users\hp\OneDrive\Desktop\MY\GitHubRS\SalaryPrediction\Assets\estimator.h5"
)
model = None
if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
    except Exception:
        model = None

# conservative fallback features (adjust as needed)
FALLBACK_FEATURES = [
    "Rating",
    "Age of Company",
    "python",
    "R",
    "spark",
    "aws",
    "excel",
    "desc_len",
    "No. of Competitors",
    "job_simp",
    "seniority",
]


def get_model_features():
    if model is None:
        return FALLBACK_FEATURES
    if hasattr(model, "feature_names_in_"):
        return list(model.feature_names_in_)
    if hasattr(model, "feature_names"):
        return list(model.feature_names)
    return FALLBACK_FEATURES


@app.route("/", methods=["GET"])
def home():
    features = get_model_features()
    skill_flags = {"python", "R", "spark", "aws", "excel"}
    # Build a sample input to pre-fill the form with sensible defaults
    sample_input = {}
    for f in features:
        if f in skill_flags:
            # assume sample candidate knows these skills
            sample_input[f] = 1
        else:
            key = f.lower()
            if key == "rating":
                sample_input[f] = 4
            elif "age" in key or "founded" in key:
                sample_input[f] = 10
            elif key == "desc_len":
                sample_input[f] = 300
            elif "competitor" in key:
                sample_input[f] = 3
            elif key == "job_simp":
                sample_input[f] = "data scientist"
            elif key == "seniority":
                sample_input[f] = "na"
            else:
                # default numeric fallback
                try:
                    sample_input[f] = 0
                except Exception:
                    sample_input[f] = ""

    return render_template(
        "index.html",
        features=features,
        skill_flags=skill_flags,
        prediction=None,
        input_data=sample_input,
    )


@app.route("/predict", methods=["POST"])
def predict():
    features = get_model_features()
    skill_flags = {"python", "R", "spark", "aws", "excel"}

    input_data = {f: 0 for f in features}
    for f in features:
        if f in skill_flags:
            input_data[f] = 1 if request.form.get(f) == "on" else 0
        else:
            val = request.form.get(f)
            if val is None or val == "":
                continue
            # sanitize common number formats
            if isinstance(val, str):
                val_clean = val.replace("$", "").replace(",", "").strip()
            else:
                val_clean = val
            try:
                if isinstance(val_clean, str) and "." in val_clean:
                    input_data[f] = float(val_clean)
                else:
                    input_data[f] = int(val_clean)
            except Exception:
                input_data[f] = val

    X = pd.DataFrame([input_data], columns=features)
    prediction = None
    if model is not None:
        try:
            pred = model.predict(X)
            prediction = float(pred[0])
        except Exception as e:
            prediction = f"Prediction error: {e}"
    else:
        prediction = "Model file not found or failed to load."

    return render_template(
        "index.html",
        features=features,
        skill_flags=skill_flags,
        prediction=prediction,
        input_data=input_data,
    )


if __name__ == "__main__":
    app.run(debug=True)
