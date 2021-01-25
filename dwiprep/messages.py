import os

BAD_INPUT = "Invalid key: {key}. Keys must be one of {keys}"
OUTPUT_NOT_EXIST = (
    "Output directory doesn't exist. Initiating at {output_dir}."
)
BAD_VALUE_TYPES = "Invalid value type(s): {value_types}. Values must be uniform and either lists or PathLike objects."
JSON_NOT_FOUND = "Couldn't find corresponding json file for {fname} NIfTI. Please make sure that a corresponding json file exists at under the same directory: ({dname})."
ADDITIONAL_NOT_FOUND = "Couldn't find corresponding {parameter} file for {fname} NIfTI. Please make sure that a corresponding {parameter} file exists at under the same directory: ({dname})."
FILE_EXISTS = "Tried to create an existing file: {fname}. To avoid unneccesary computations, This procedure is skipped. To re-create the file, please delete the existing one."


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, "").count(os.sep)
        indent = " " * 4 * (level)
        print("{}{}/".format(indent, os.path.basename(root)))
        subindent = " " * 4 * (level + 1)
        for f in files:
            print("{}{}".format(subindent, f))
