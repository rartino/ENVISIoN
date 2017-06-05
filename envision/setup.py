#!/usr/bin/env python3

from os import path

from setuptools import setup, find_packages

# Get the long description from the README file.
readme_path =  path.join(path.abspath(path.dirname(__file__)), "README.rst")
with open(readme_path, encoding='utf-8') as readme_file:
    long_description = readme_file.read()

description = "A Python library for parsing and visualizing electron structure data."

setup(
        name="envision",
        version="0.1.0",
        description=description,
        long_description=long_description,
        keywords="inviwo vasp",

        install_requires=['h5py','regex'],

        #author="",
        #author_email="",
        #url="",
        license="BSD-2-Clause",

        packages=find_packages(),
    )

