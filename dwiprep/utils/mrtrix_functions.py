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


def merge_phasediff(ap: Path, pa: Path, out_file: Path):
    """
    Concatenates phase-opposites (AP-PA) across the 4th dimension
    Parameters
    ----------
    ap : Path
        [Path to DWI series AP's mean B0 image]
    pa : Path
        [Path to DWI series PA image]
    out_file : Path
        [description]

    Returns
    -------
    [type]
        [description]
    """
    cmd = f"mrcat {ap} {pa} {out_file} -axis 3"
    return cmd