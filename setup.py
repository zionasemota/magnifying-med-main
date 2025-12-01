from setuptools import setup, find_packages

setup(
    name="magnifying-med",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.31.0",
        "matplotlib>=3.7.0",
        "numpy>=1.24.0",
    ],
)

