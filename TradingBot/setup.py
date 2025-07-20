from setuptools import setup, find_packages

from setuptools import setup, find_packages

setup(
    name="tradingbot",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        line.strip() for line in open("requirement.txt") 
        if line.strip() and not line.startswith('#')
    ],
)