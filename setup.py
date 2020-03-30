from distutils.core import setup
from setuptools import find_packages

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name='shamo',
    version='v1.0.0',
    license="GPLv3",
    description='Forward modelling and sensitivity analysis.',
    long_description=long_description,
    author='Martin Grignard',
    author_email='mar.grignard@uliege.be',
    packages=find_packages(),
    install_requires=["numpy", "nibabel", "scipy", "scikit-learn"]
)
