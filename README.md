# _DWIPrep_: A Robust Preprocessing Pipeline for dMRI Data

This pipeline is being developed and maintaing [Yaniv Assaf's lab at Tel Aviv University](https://www.yalab.sites.tau.ac.il/), as an open-source tool for preprocessing of dMRI data.

_DWIPrep_ is a diffusion magnetic resonance image (dMRI) data preprocessing pipeline that is designed to provide and easily accessible, robust and dynamic interface, allowing basic preprocessing for both within-subject (plasticity) and between-subjects datasets, envolving a wide variety of dMRI scan acquisitions. <br />
The _dMRIPrep_ pipeline uses a combination of tools from well-known software packages, including [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/), [MRtrix3](https://mrtrix.readthedocs.io/en/latest/), [SPM](https://www.fil.ion.ucl.ac.uk/spm/) and [CAT12](http://www.neuro.uni-jena.de/cat/). This pipeline was designed to provide a potentially best preprocessing pipeline for a wide range of dMRI data acquisition parameters, and will be updated as new neuroimaging software become available.

This tool allows you to easily do the following:

- Preprocess a wide variety of dMRI data, from raw to fully preprocessed form.
- Account for specific preprocessing procedures that are crucial of analyzing plasticity (i.e, within-subjects) datasets.
- Automate processing steps.
