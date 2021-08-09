"""
Command line interface execution management.
"""
import argparse
from pathlib import Path
from dwiprep.cli.utils.parse_subject import parse_subject

#
from configuration import PARSER_CONFIGRATION

parser = argparse.ArgumentParser(**PARSER_CONFIGRATION)
parser.add_argument("-input", type=Path, required=True)
parser.add_argument("-output", type=Path, required=True)
parser.add_argument("-subj_id", type=str, required=False)
parser.add_argument("-parcellation_file", type=Path, required=False)
parser.add_argument("-parcellation_name", type=str, required=False)
args = vars(parser.parse_args())

(input_dir, output_dir, subj_id, atlas_file, atlas_name) = [
    args.get(key)
    for key in [
        "input",
        "output",
        "subj_id",
        "parcellation_file",
        "parcellation_name",
    ]
]
if not subj_id:
    subj_ids = sorted(input_dir.glob("sub-*"))
else:
    subj_ids = [subj_id]
for subj_dir in subj_ids:
    if not subj_dir.is_dir():
        continue
    subj_id = subj_dir.name
    preprocess_pipe = parse_subject(input_dir, output_dir, subj_id)
    if not preprocess_pipe:
        continue
    preprocess_pipe.run_corrections()
    if atlas_file and atlas_name:
        preprocess_pipe.run_registrations(
            atlas={"path": Path(atlas_file), "name": atlas_name}
        )
    else:
        preprocess_pipe.run_registrations()