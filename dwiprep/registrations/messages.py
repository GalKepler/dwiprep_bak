# ERRORS
MISSING_KEYS_LONGITUDIANL = """There are not enough sessions ({num_sessions}) to refer to the pipeline as longitudinal."""

# WARNINGS
MULTIPLE_SESSIONS_WARNING = """There are multiple sessions ({num_sessions}) found, but the pipeline is not about to perform longitudinal registrations, and will register each session seperately.
"""
FILE_EXISTS = "Tried to create an existing file\s: {fname}. To avoid unneccesary computations, This procedure is skipped. To re-create the file\s, please delete the existing one."


# MESSAGES
CONVERT_TO_NII = """Converting file to NIfTI (.nii.gz) format for compatability with used functions...
Input file: {in_file}
Output file: {out_file}
Command: {command}
"""
COREGISTER = """Registering between-session {img_type} images.
This procedure includes:
(1) Linear registration of images to each other (bidirectional)
Commands:
{cmd_1_a}
{cmd_1_b}
(2) Calculation of halfway transformation matrices (to register for a midway space)
Commands:
{cmd_2_a}
{cmd_2_b}
(3) Linear registration of original images to halfway space, using calculated transforms:
Commands:
{cmd_3_a}
{cmd_3_b}
"""
AVERAGE_IMAGES = """Averaging coregistered {img_type} images.
Inputs:
    1. pre2post image: {ses_1}
    1. post2pre image: {ses_2}
Output:
    Averaged file: {out_file}
Command:
    {cmd}
"""
APPLY_XFM = """Applying pre-calculated transformation matrix on tensor-derived parameter.
Input:
    {in_file}
Affine matrix:
    {aff}
Reference:
    {ref}
Output:
    {out_file}
Command:
    {command}
"""
SKULL_STRIP = """Performing skull stripping using FSL's BET function.
Input:
    {in_file}
Output:
    {out_file}
Command:
    {command}
"""
EPI_REG = """Performing registration between low-res EPI image and high-res anatomical one.
Inputs:
    1. EPI image: {epi}
    2. Whole-brain anatomical image: {anat}
    3. Skull-stripped anatomical image: {anat_brain}
Outputs:
    1. Registered image: {out_file}
    2. Transformation matrix: {out_mat}
Command:
    {command}
"""
CONCAT_AFFINES = """Combining pre-calculated affine matrices into one across-modalities,across-session affine matrix.
Inputs:
    1. Across-sessions affine matrix: {between_sessions}
    2. Across-modalities affine matrix: {epi2t1w}
Output:
    Combined affine matrix: {out_file}
Command:
    {command}
"""
PREPROCESS_ANAT = """Preprocessing anatomical image for optimal estimation of normalization's warp fields.
Input:
    Raw anatomical image: {in_file}
Output:
    Preprocessing directory: {out_dir}
Command:
    {command}
"""
APPLY_WARP = """Applying pre-calculated warp field to normalize tensor-derived metrices.
Inputs:
    1. Tensor-derived parameter image: {in_file}
    2. Pre-calculated warp field: {warp}
    3. Reference image: {ref}
Output:
    Normalized tensor-derived parameter image: {out_file}
Command:
    {command}
"""
REGISTER_ATLAS = """Applying pre-calculated warp field to register parcellation atlas from standard (MNI) to native space.
Inputs:
    1. Original parcellation atlas (at standard space): {atlas}
    2. Pre-calculated warp field: {warp}
    3. Reference image: {target}
    4. Interpolation method: Nearest Neighbour
Output:
    Native-space brain parcellation: {out_file}
Command:
    {command}
"""
REGISTER_ATLAS_CAT = """Applying pre-calculated warp field to register parcellation atlas from standard (MNI) to native space.
Inputs:
    1. Original parcellation atlas (at standard space): {atlas}
    2. Pre-calculated warp field: {warp}
    3. Interpolation method: Nearest Neighbour
Output:
    Native-space brain parcellation: {out_file}
"""
GUNZIP = """Unzipping .gz image for compatability with SPM functions...
Input:
    {anat_file}
Output:
    {anat_nii}
"""
PREPROCESS_CAT = """Preprocessing anatomical image for optimal estimation of normalization's warp fields.
Input:
    Raw anatomical image: {in_file}
Output:
    Preprocessing directory: {out_dir}
For full description of the anatomical preprocessing pipeline and properties, see report under output directory.
"""
REGISTER_TENSORS_CAT = """Applying pre-calculated deformation field no normalize tensor-derived parameter image.
Inputs:
    1. Tensor-derived parameter image: {in_file}
    2. Pre-calculated deformation field: {warp}
Output:
    Normalized tensor-derived parameter image: {out_file}
"""

# flake8: noqa: E501
