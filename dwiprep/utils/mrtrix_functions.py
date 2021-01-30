from nipype.interfaces import mrtrix3 as mrt
from pathlib import Path


def extract_b0(in_file: Path, out_b0s: Path, out_file: Path):
    """
    Extracts B0 volumes from DWI series and then averaging them across the 4th dimension.
    Parameters
    ----------
    in_file : Path
        [Path to input DWI series' image.]
    out_b0s : Path
        [Path to output DWI's B0s volumes.]
    out_file : Path
        [Path to output DWI's mean B0 volume]

    Returns
    -------
    [type]
        [description]
    """
    dwiextract = mrt.DWIExtract()
    dwiextract.inputs.in_file = in_file
    dwiextract.inputs.bzero = True
    dwiextract.inputs.out_file = out_b0s
    dwiextract.inputs.args = "-quiet -force"
    dwiextract.run()
    mrmath = mrt.MRMath()
    mrmath.inputs.in_file = out_b0s
    mrmath.inputs.operation = "mean"
    mrmath.inputs.axis = 3
    mrmath.inputs.out_file = out_file
    return dwiextract, mrmath
