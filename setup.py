from setuptools import setup, find_packages

setup(
    name="madtypes",
    version="0.0.1",
    author="6r17",
    author_email="patrick.borowy@proton.me",
    description="Python typing that will actually tell you to <censored>",
    packages=find_packages(include=["madtypes"]),
    install_requires=[],
    extras_require={"dev": ["pytest", "pytest-cov"]},
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
