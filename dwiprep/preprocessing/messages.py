import os

#
# Errors
#
BAD_INPUT = "Invalid key: {key}. Keys must be one of {keys}"
OUTPUT_NOT_EXIST = (
    "Output directory doesn't exist. Initiating at {output_dir}."
)
BAD_VALUE_TYPES = "Invalid value type(s): {value_types}. Values must be uniform and either lists or PathLike objects."
MORE_THAN_TWO_SESSIONS = (
    "Registration of more than 2 sessions is not implemented yet."
)
#
# Warnings
#
JSON_NOT_FOUND = """
Couldn't find corresponding json file for {fname} NIfTI.
Please make sure that a corresponding json file exists at under the same directory: ({dname}).
"""
ADDITIONAL_NOT_FOUND = """
Couldn't find corresponding {parameter} file for {fname} NIfTI.
Please make sure that a corresponding {parameter} file exists at under the same directory: ({dname}).
"""
FILE_EXISTS = """
Tried to create an existing file: {fname}.
To avoid unneccesary computations, This procedure is skipped. To re-create the file, please delete the existing one.
"""
ANTS_NOT_FOUND = """
Tried to use ANTs N4 algorithm for B1 inhomogenity correction, but couldn't find it under the environment variable "ANTSPATH": {antspath}.
Please note that it is much preferable to use ANTs N$ algorithm for this kind of corrections, and we encourage you to make sure it's properly installed.
Proceeding with FSL's "fast" command, which is sub-optimal.
"""
#
# Messages
#
CONVERT_TO_MIF = """
Converting file to MRTrix3's .mif format for better compatability with used functions...
Input file: {in_file}
Output file: {out_file}
Command: {command}
"""
CONVERT_TO_NII = """
Converting file to NIfTI (.nii.gz) format for compatability with used functions...
Input file: {in_file}
Output file: {out_file}
Command: {command}
"""
AVERAGE_B0 = """
Calculating DWI series' mean B0 image...
Input file: {in_file}
Output files:
    1. B0 series: {out_b0s}
    Command: {command_1}
    2. Mean B0 image: {out_file}
    Command: {command_2}
"""
MERGE_PHASEDIFF = """
Concatenating opposite phase-encoded B0 images...
Inputs files:
    1. AP-encoded B0: {ap}
    2. PA-encoded B0: {pa}
Output file: {merged}
Command: {command}
"""
CORRECT_SDC = """
Correcting for susceptabillity distortion artifects...
Input files:
    1. DWI series: {ap}
    2. Concatenated phase-opposite B0s: {merged}
Output file: {out_file}
Command: {command}
"""
CORRECT_BIAS = """
Correcting for B1 field inhomogenity using {algorithm}'s algorithm.
Input file: {in_file}
Output file: {out_file}
Command: {command}
"""
CALCULATE_TENSOR = """
Generating maps of tensor-derived parameters...
Input file: {in_file}
Output files:
    1. Tensor image: {tensor}
    Command: {command_1}
    2. Mean Diffusivity image: {md}
    3. Fractional Anisotropy image: {fa}
    4. Axial Diffusivity image: {ad}
    5. Radial Diffusivity image: {rd}
    6. Linearity metric image: {cl}
    7. Planarity metric image: {cp}
    8. Sphericity metric image: {cs}
    9. Eigen value(s) image: {val}
    10. Eigen vector(s) image: {vec}
    Command: {command_2}
"""


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, "").count(os.sep)
        indent = " " * 4 * (level)
        print("{}{}/".format(indent, os.path.basename(root)))
        subindent = " " * 4 * (level + 1)
        for f in files:
            print("{}{}".format(subindent, f))


# flake8: noqa: E501
