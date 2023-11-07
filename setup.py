"""e7h4n 的 beancount 记账工程，包含了账本已经一些常用的工具"""

from setuptools import setup, find_packages

setup(
    python_requires=">=3.6, <4",
    packages=find_packages(),
    install_requires=[
        "gitpython==3.1.40",
    ],
    extras_require={
        "dev": [],
        "test": [
            "black",
            "coverage",
            "pylint",
            "flake8",
            "pytest",
        ],
    },
)
