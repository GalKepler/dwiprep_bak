"""
General configuration constants for the :mod:`~dwiprep.cli` module.
"""

PROGRAM = "dwiprep"
DESCRIPTION = "DWIprep is a robust and easy-to-use preprocessing pipeline for diffusion-weighted imaging of various acquisitions."  # noqa: E501
USAGE = "%(prog)s [options] -i <bids_dir> -o <derivatives_dir>"
PARSER_CONFIGRATION = {
    "prog": PROGRAM,
    "description": DESCRIPTION,
    "usage": USAGE,
}
