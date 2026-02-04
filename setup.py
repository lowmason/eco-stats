"""
Setup script for eco-stats package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="eco-stats",
    version="0.1.0",
    author="Lowell Mason",
    description="A Python library for pulling statistical series from BEA, BLS, Census, and FRED APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lowmason/eco-stats",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "pandas": ["pandas>=1.3.0"],
        "dev": ["pytest>=7.0.0", "pytest-cov>=3.0.0", "black>=22.0.0", "flake8>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "eco-stats=eco_stats.__main__:main",
        ],
    },
)
