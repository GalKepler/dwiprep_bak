import argparse

from dwiprep.CLI.configuration import PARSER_CONFIGRATION

parser = argparse.ArgumentParser(**PARSER_CONFIGRATION)
parser.add_argument("-input", type=str, required=False)
args = parser.parse_args()
print(args.input)
