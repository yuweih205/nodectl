from setuptools import setup, find_packages

setup(
    name="nodectl",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "nodectl = nodectl.main:main",
        ]
    },
)
