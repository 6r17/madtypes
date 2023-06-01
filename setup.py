from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="madtypes",
    version="0.0.7",
    author="6r17",
    author_email="patrick.borowy@proton.me",
    description="Python typing that raise TypeError at runtime",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/6r17/madtypes",
    packages=find_packages(include=["madtypes"]),
    keywords=["typing", "json", "json-schema"],
    python_requires=">=3.10",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
