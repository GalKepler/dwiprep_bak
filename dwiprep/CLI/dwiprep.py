import argparse

# from dwiprep.CLI.utils import messages

parser = argparse.ArgumentParser(
    prog="dwiprep",
    description="DWIprep is a robust and easy-to-use preprocessing pipeline for diffusion-weighted imaging of various acquisitions.",
    usage="%(prog)s [options] -i <bids_dir> -o <derivatives_dir>",
)
parser.add_argument("-input", type=str, required=False)
args = parser.parse_args()
print(args.input)