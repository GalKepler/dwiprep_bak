import os

from setuptools import find_packages, setup

from dwiprep.cli.configuration import DESCRIPTION

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as fh:
    requirements = fh.read().splitlines()
    install_requires = [
        requirement
        for requirement in requirements
        if not requirement.startswith("git+")
    ]
    dependency_links = [
        requirement
        for requirement in requirements
        if requirement.startswith("git+")
    ]

with open("requirements-dev.txt") as fh:
    dev_requirements = fh.read().splitlines()


setup(
    name="dwiprep",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    license="AGPLv3",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GalBenZvi/dwiprep",
    author="Gal Ben Zvi",
    author_email="hershkovitz1@mail.tau.ac.il",
    keywords="mri dwi python neuroimaging",
    python_requires=">=3.6",
    install_requires=install_requires,
    dependency_links=dependency_links,
    extras_require={"dev": dev_requirements},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    # package_dir={"": "dwiprep"},
    # packages=find_packages(where="dwiprep"),
)
