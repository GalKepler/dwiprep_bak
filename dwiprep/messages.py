import os

### ERRORS ###

BAD_INPUT = "Invalid key: {key}. Keys must be one of {keys}"
OUTPUT_NOT_EXIST = (
    "Output directory doesn't exist. Initiating at {output_dir}."
)
BAD_VALUE_TYPES = "Invalid value type(s): {value_types}. Values must be uniform and either lists or PathLike objects."

### Warning ###

JSON_NOT_FOUND = "Couldn't find corresponding json file for {fname} NIfTI. Please make sure that a corresponding json file exists at under the same directory: ({dname})."
ADDITIONAL_NOT_FOUND = "Couldn't find corresponding {parameter} file for {fname} NIfTI. Please make sure that a corresponding {parameter} file exists at under the same directory: ({dname})."
FILE_EXISTS = "Tried to create an existing file: {fname}. To avoid unneccesary computations, This procedure is skipped. To re-create the file, please delete the existing one."

### Messages ###

CONVERT_TO_MIF = """Converting file to MRTrix3's .mif format for better compatability with used functions...
Input file: {in_file}
Output file: {out_file}
Command: {command}
"""
AVERAGE_B0 = """Calculating DWI series' mean B0 image...
Input file: {in_file}
Output files: 
    1. B0 series: {out_b0s}
    Command: {command_1}
    2. Mean B0 image: {out_file}
    Command: {command_2}
"""
MERGE_PHASEDIFF = """Concatenating opposite phase-encoded B0 images...
Inputs files:
    1. AP-encoded B0: {ap}
    2. PA-encoded B0: {pa}
Output file: {merged}
Command: {command}
"""


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, "").count(os.sep)
        indent = " " * 4 * (level)
        print("{}{}/".format(indent, os.path.basename(root)))
        subindent = " " * 4 * (level + 1)
        for f in files:
            print("{}{}".format(subindent, f))
