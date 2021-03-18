# _DWIPrep_: A Robust Preprocessing Pipeline for dMRI Data

This pipeline is being developed and maintaing [Yaniv Assaf's lab at Tel Aviv University](https://www.yalab.sites.tau.ac.il/), as an open-source tool for preprocessing of dMRI data.

_DWIPrep_ is a diffusion magnetic resonance image (dMRI) data preprocessing pipeline that is designed to provide an easily accessible, robust and dynamic interface, allowing basic pre-processing for both within-subject (plasticity) and between-subjects datasets, envolving a wide variety of dMRI scan acquisitions. <br />
The _dMRIPrep_ pipeline uses a combination of tools from well-known software packages, including [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/), [MRtrix3](https://mrtrix.readthedocs.io/en/latest/), [SPM](https://www.fil.ion.ucl.ac.uk/spm/) and [CAT12](http://www.neuro.uni-jena.de/cat/). This pipeline was designed to provide a potentially best preprocessing pipeline for a wide range of dMRI data acquisition parameters, and will be updated as new neuroimaging software become available.

This tool allows you to easily do the following:

- Preprocess a wide variety of dMRI data, from raw NIfTI (structured to follow the [BIDS format](https://bids-specification.readthedocs.io/en/stable/)) to fully preprocessed form.
- Account for specific preprocessing procedures that are crucial of analyzing plasticity (i.e, within-subjects) datasets.
- Automate processing steps.

____
# **Preprocessing (including demonstrations):**

1. Extraction of opposite phase-encoding DWI's **B<sub>0</sub> volumes** for later Susceptability Distortions Correction (SDC).


2. **Motion & Susceptability Distortions Correction (SDC)** using FSL's [*topup*](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup)<sup>1</sup> and [*Eddy*](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy)<sup>2</sup>, as implemented via MRTrix3's [*dwifslpreproc*](https://mrtrix.readthedocs.io/en/latest/reference/commands/dwifslpreproc.html)<sup>3</sup>. Note that the pipeline assumes **opposite** phase encoding directions, as it was found to be optimal for SDC<sup>4</sup>.

   <p align="center"> 
   <img width="500" src="images/preprocessing/SDC.gif" > 
   </p>
   <p align="center"> 

    *Figure 1:* AP and PA represent the opposite, uncorrected, B0 volumes - extracted from opposite phase-encoded DWIs, "corrected" stands for post-SDC implementation of *dwifslpreproc*.
3. B1 field inhomogeneity correction for a DWI volume series, using the N4 algorithm as provided in ANTs* ([*N4BiasFieldCorrection*](https://simpleitk.readthedocs.io/en/master/link_N4BiasFieldCorrection_docs.html))<sup>5</sup>, as implemented in MRTtrix3's [*dwibiascorrect*](https://mrtrix.readthedocs.io/en/latest/reference/commands/dwibiascorrect.html#dwibiascorrect-ants)<sup>3</sup>.

\* In case ANTs is not installed in user's computer, the pipeline will use FSL's  *fast* algorithm<sup>6,7</sup>, which is discouraged due to its dependency on DWI's brain masking.

___
# **Estimation of diffusion (kurtosis) tensor & tensor-derived parameters**
Following the preprocessing of DWI data, the pipeline automatically estimates several, widely used, tensor-derived parameters:
1. **Estimation of diffusion tensor** using MRTrix3 *tensor2metric* implementation of the Weighted Linear Least Squares estimation of diffusion MRI parameters<sup>8</sup>.
2. **Generation of tensor-derived parameters maps**<sup>9,10</sup>
<p align="center"> 
   <img width="400" src="images/tensors/tensor_parameters.png" > 
</p>

___
# **Registration pipeline**
## **Longitudinal (Multi-sessions)**
To account for registration-induced biases, we've implemented a within-subject (i.e, between-sessions) registration pipeline, before normalizing subject's data into standard space. This implementation includes the following steps:
1. Registration of subject’s first session ("pre") b<sub>0</sub> to it’s second one (“post”) b<sub>0</sub> and vice versa (post's b<sub>0</sub> to pre's b<sub>0</sub>), using FSL’s [*flirt*](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT)<sup>11,12</sup>, with a *mutual information* cost function.
2. Calculation of forward and backward *halfway transformation matrices* (pre to post and post to pre, accordingly) using FSL’s [*avscle*](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT/UserGuide#avscale). 
3. Applying halfway transformation to both sessions’ b<sub>0</sub> (forward to pre, backward to post), registrating them into subject's "middle" space.
4. Calculating subject’s average (between sessions) b<sub>0</sub>, as the average of both coregistered b<sub>0</sub>s.
<p align="center"> 
   <img width="500" src="images/registrations/coreg_within.gif" > 
</p>
5. Same procedure is applied to register (between-sessions) subjects’ anatomical (T1) images.
<p align="center"> 
   <img width="500" src="images/registrations/coreg_t1_within.gif" > 
</p>

## **Co-registrations and Normalization**
Note that all registerations procedures denoted below, when performed on a longitudinal dataset, do so for the within-subject (between-sessions) registered images.
## **Coregistration (DWI to T<sub>1</sub>)**
Coregistration, in this case, refers to the registration of images of different modalities (i.e DWI, T<sub>1</sub>, etc.) of the same subject.
Coregisteration is performed using FSL's [*epi_reg*](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT/UserGuide#epi_reg) script, performing appropriate linear registration between subject's B<sub>0</sub> and T<sub>1</sub> images.
<p align="center"> 
   <img width="500" src="images/registrations/coreg_modalities.gif" > 
</p>

## **Normalization**
By default, the *normalization* procedure conducted as part of this pipeline makes use of the [Computational Anatomy Toolbox (CAT)](http://www.neuro.uni-jena.de/cat/) for SPM. Since it requires MATLAB and SPM to be installed, the pipeline will resort to using FSL's [*fsl_anat*](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/fsl_anat) script.
### **CAT12**
CAT12 is a structural preprocessing tool offered as an addition to the Statistical Parametric Mapping (SPM) toolbox. It offers robust spatial normalization algorithms, as well as a Quality Assurance (QA) score regarding the structural image being processed, for example:
<p align="center"> 
   <img width="500" src="images/registrations/cat_example.jpg" > 
</p>
<p align="center"> 
   <img width="500" src="images/registrations/cat12_preproc.gif" > 
</p>

### **fsl_anat**
In case the user doesn't have MATLAB/SPM/CAT12 installed, the pipeline will resort to performing the spatial normalization using FSL's *fsl_anat*, which includes the following:
1. Reorientation to standard (MNI) orientation using fslreorient2std.
2. Automatically cropping the image using robustfov.
3. Bias-field correction (RF/B1-inhomogeneity-correction) using FAST.
4. Registration to standard space (linear and nonlinear) using FLIRT and FNIRT.
5. Brain extraction (FNIRT-based)
6. Tissue-type segmentation using FAST.
7. Subcortical structure segmentation using FIRST.
A summarized presentation of the anatomical preprocessing conducted via *fsl_anat*:
<p align="center"> 
   <img width="500" src="images/registrations/anat_preproc.gif" > 
</p>


## **Inverse registration**
Following the "forward" registration (i.e, from subject to average space), and only if a parcellation atlas in MNI space is given as input for the pipeline, a "backward" registration (i.e from MNI to native space) is performed to transform the parcellation atlas into subject's space.
Note that this behaviour is promoted due to our agenda to promote region-based analyses (RBA), as described in our paper<sup>13</sup> (under review).
For example, a reverse registration performed on the Brainnetome parcellation atlas<sup>14</sup>:
<p align="center"> 
   <img width="500" src="images/registrations/atlas2native.gif"> 
</p>

___

## References
1. Andersson, J. L., Skare, S., & Ashburner, J. (2003). How to correct susceptibility distortions in spin-echo echo-planar images: application to diffusion tensor imaging. Neuroimage, 20(2), 870-888.
2. Andersson, J. L., & Sotiropoulos, S. N. (2016). An integrated approach to correction for off-resonance effects and subject movement in diffusion MR imaging. Neuroimage, 125, 1063-1078.
3. Tournier, J. D., Smith, R., Raffelt, D., Tabbara, R., Dhollander, T., Pietsch, M., ... & Connelly, A. (2019). MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 202, 116137.
4. Gu, X., & Eklund, A. (2019). Evaluation of six phase encoding based susceptibility distortion correction methods for diffusion MRI. Frontiers in neuroinformatics, 13, 76.
5. Tustison, N. J., Avants, B. B., Cook, P. A., Zheng, Y., Egan, A., Yushkevich, P. A., & Gee, J. C. (2010). N4ITK: improved N3 bias correction. IEEE transactions on medical imaging, 29(6), 1310-1320.
6. Zhang, Y.; Brady, M. & Smith, S. Segmentation of brain MR images through a hidden Markov random field model and the expectation-maximization algorithm. IEEE Transactions on Medical Imaging, 2001, 20, 45-57
7. Smith, S. M.; Jenkinson, M.; Woolrich, M. W.; Beckmann, C. F.; Behrens, T. E.; Johansen-Berg, H.; Bannister, P. R.; De Luca, M.; Drobnjak, I.; Flitney, D. E.; Niazy, R. K.; Saunders, J.; Vickers, J.; Zhang, Y.; De Stefano, N.; Brady, J. M. & Matthews, P. M. Advances in functional and structural MR image analysis and implementation as FSL. NeuroImage, 2004, 23, S208-S219
8. Veraart, J.; Sijbers, J.; Sunaert, S.; Leemans, A. & Jeurissen, B. Weighted linear least squares estimation of diffusion MRI parameters: strengths, limitations, and pitfalls. NeuroImage, 2013, 81, 335-346
9. Basser, P. J.; Mattiello, J. & Lebihan, D. MR diffusion tensor spectroscopy and imaging. Biophysical Journal, 1994, 66, 259-267
10. Westin, C. F.; Peled, S.; Gudbjartsson, H.; Kikinis, R. & Jolesz, F. A. Geometrical diffusion measures for MRI from tensor basis analysis. Proc Intl Soc Mag Reson Med, 1997, 5, 1742
11. Jenkinson, M., Bannister, P., Brady, M., Smith, S., 2002. Improved optimization for the
robust and accurate linear registration and motion correction of brain images. Neuroimage 17, 825-841.
12. Jenkinson, M., Smith, S., 2001. A global optimisation method for robust affine registration of brain images. Med Image Anal 5, 143-156.
13. Ben-Zvi, G., Hofstetter, S., Tavor, I. \& Assaf, Y. (2021). Measuring neuroplasticity with diffusion MRI: experimental considerations. (under review)
14. Fan, L., Li, H., Zhuo, J., Zhang, Y., Wang, J., Chen, L., ... & Jiang, T. (2016). The human brainnetome atlas: a new brain atlas based on connectional architecture. Cerebral cortex, 26(8), 3508-3526.
