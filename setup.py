from setuptools import setup, find_packages

# Load long description
long_description = open("README.md", "r").read()

# Define classifiers
CLASSIFIERS = [
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Scientific/Engineering :: Physics",
    "Topic :: Scientific/Engineering :: Visualization",
    "Topic :: Scientific/Engineering :: Medical Science Apps."
]

# Define setup settings
setup(
    name="shamo",
    version="0.1.0",
    license="GPLv3",
    description="A tool for electromagnetic modelling of the head and sensitivity analysis.",
    long_description=long_description,
    author="Martin Grignard",
    author_email="mar.grignard@uliege.be",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "numpy", "nibabel", "scipy", "scikit-learn", "chaospy",
        "pygalmesh==0.4.0", "gmsh"
    ],
    zip_safe=False,
    classifiers=CLASSIFIERS
)
