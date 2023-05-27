from setuptools import setup, find_packages

setup(
    name="madtypes",
    version="0.0.1",
    author="6r17",
    author_email="patrick.borowy@proton.me",
    description="Python typing that will raise TypeError at runtime",
    long_description="""
    # https://github.com/6r17/madtypes
    - 💢 Python class typing that will raise TypeError at runtime
    - 📖 Render to dict or json
    - 🌐 [Json-Schema](https://json-schema.org/)
    """,
    packages=find_packages(include=["madtypes"]),
    keywords="typing",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
