"""Package setup for bitwatch."""

from setuptools import find_packages, setup

setup(
    name="bitwatch",
    version="0.1.0",
    description="A lightweight CLI tool to monitor file and directory changes with configurable webhook alerts.",
    author="bitwatch contributors",
    python_requires=">=3.11",
    packages=find_packages(exclude=["bitwatch/tests*"]),
    install_requires=[
        "requests>=2.28",
    ],
    extras_require={
        "dev": [
            "pytest>=7",
            "pytest-cov",
            "responses",
        ]
    },
    entry_points={
        "console_scripts": [
            "bitwatch=bitwatch.cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: System :: Monitoring",
    ],
)
