from setuptools import setup, find_packages

setup(
    name="rbt",
    version="0.26",
    packages=find_packages(),
    description="RBT framework is a Python library for quantitative trading research, providing functionalities for market data processing, strategy execution, and performance evaluation.",
    author="Your Name",
    author_email="your@email.com",
    url="Your project URL",
    install_requires=[
        "pandas",
        "numpy",
        "cvxpy",
        "scipy",
        "scikit-learn",
        "progressbar2",
        "market-specs",
    ],
    entry_points={},
)
