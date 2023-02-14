from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="blendgen",
    version="0.0.1",
    author="Mattias Johnson, Anton Eriksson",
    author_email="",
    description="A program that generates machine learning training image data using Blender.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mattiasJohnson/BlendGen",
    project_urls={
        "Source Code": "https://github.com/mattiasJohnson/BlendGen",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3",
    entry_points={
        "console_scripts": ["blendgen=main:main"],
    },
)
