"""
Command line interface execution management.
"""
import argparse
from pathlib import Path
import importlib

# import sys

# BASE_DIR = Path(__file__).absolute().parent
# importlib.import_module(str(BASE_DIR))
# sys.path.append(str(BASE_DIR))

from configuration import PARSER_CONFIGRATION

parser = argparse.ArgumentParser(**PARSER_CONFIGRATION)
parser.add_argument("-input", type=str, required=False)
args = parser.parse_args()
print(args.input)
