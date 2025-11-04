from setuptools import setup, find_packages
import codecs
import os

# Read the README file for long description
here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="shoreline-s-wrapper",
    version="0.1.0",
    description="Python wrapper for ShorelineS MATLAB model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8,<3.9",
    
    # Package discovery
    packages=find_packages(where="."),
    package_dir={"": "."},
    
    # Dependencies
    install_requires=[
        "numpy>=1.21,<1.25",
        "pandas>=1.3,<2.0", 
        "PyYAML>=5.3.1,<7.0",
        "scipy>=1.6,<1.8",
        "matlabengine==9.10.1" # NOTE: for R2020b, py3.8. Depends on matlab version
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest",
            "black", 
            "mypy",
            "types-PyYAML"
        ],
        "test": [
            "pytest",
            "pytest-cov"
        ]
    },
    
    # Metadata
    author="Henrique Faria Cordeiro",
    author_email="hcordeiro.loc@gmail.com",
    url="https://github.com/hcordeiroAtLoc/shoreline-s-wrapper",
    #classifiers=[
    #    "Development Status :: 3 - Alpha",
    #    "Intended Audience :: Science/Research",
    #    "License :: OSI Approved :: MIT License",
    #    "Programming Language :: Python :: 3.8",
    #    "Topic :: Scientific/Engineering"
    #],
    keywords="shoreline, modeling, matlab, coastal",
    
    # Include package data if needed
    include_package_data=True,
    zip_safe=False,
)