with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dwiprep-Gal_Ben-Zvi",
    version="0.0.1",
    author="Gal Ben-Zvi",
    author_email="hershkovitz1@mail.tau.ac.il",
    description="DWIPrep is a robust and easy-to-use pipeline for preprocessing of diverse dMRI data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)