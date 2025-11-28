from setuptools import find_packages
from typing import List
def get_requirements(filename: str)->List[str]:

    with open(filename, 'r') as f:

        return [line.strip() for line in f.readlines() if line.strip()!='-e .']


setup(
    name='salary_prediction',
    version='0.0.1',
    author='rajat',
    author_email='rajattsharma87077@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
)