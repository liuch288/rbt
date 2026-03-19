from setuptools import setup, find_packages

setup(
    name="rbt",
    version="0.9",
    packages=find_packages(),
    description="RBT framework is a Python library for quantitative trading research, providing functionalities for market data processing, strategy execution, and performance evaluation.",
    author="Your Name",
    author_email="your@email.com",
    url="Your project URL",
    install_requires=[
        # List the dependencies of the RBT framework
        "pandas",  # For data processing
        "numpy",  # For numerical computations
        "cvxpy",  # For optimization problem solving
    ],
    entry_points={},
)
