import subprocess
from pathlib import Path

from nipype.interfaces import mrtrix3 as mrt

COMMAND = "dwifslpreproc {ap} {out_file} -pe_dir {pe_dir} -align_seepi -rpe_pair -eddy_options ' --slm=linear' -se_epi {merged} -nthreads 12"  # noqa: E501


def extract_b0(in_file: Path, out_b0s: Path, out_file: Path):
    """
    Extracts B0 volumes from DWI series and then averaging them across the 4th
    dimension.

    Parameters
    ----------
    in_file : Path
        Path to input DWI series' image.
    out_b0s : Path
        Path to output DWI's B0s volumes.
    out_file : Path
        Path to output DWI's mean B0 volume

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
    Concatenates phase-opposites (AP-PA) across the 4th dimension.

    Parameters
    ----------
    ap : Path
        Path to DWI series AP's mean B0 image
    pa : Path
        Path to DWI series PA image
    out_file : Path
        Path to concatenated phase-opposite B0 image

    Returns
    -------
    [type]
        [description]
    """
    cmd = f"mrcat {ap} {pa} {out_file} -axis 3"
    return cmd


def correct_sdc(ap: Path, merged: Path, out_file: Path):
    """
    Use MRTrix3's dwifslpreproc function to perform susceptabillity distortion
    correction on DWI series.

    Parameters
    ----------
    ap : Path
        Path to original DWI series
    merged : Path
        Path to concatenated phase-opposite B0 image
    out_file : Path
        Path to output susceptabillity corrected DWI series
    """
    pe_dir = subprocess.check_output(
        ["mrinfo", str(ap), "-property", "PhaseEncodingDirection"]
    )
    pe_dir = pe_dir.decode("utf-8").replace("\n", "")
    return COMMAND.format(
        ap=ap, out_file=out_file, pe_dir=pe_dir, merged=merged
    )


def correct_bias_field(in_file: Path, out_file: Path):
    """
    Perform DWI B1 field inhomogenity correction.

    Parameters
    ----------
    in_file : Path
        Path to SD-corrected DWI series
    out_file : Path
        Path to output B1 bias-field corrected DWI series
    """
    ants_flag = (
        subprocess.check_output(["N4BiasFieldCorrection", "--version"])
        .decode("utf-8")
        .lower()[:12]
    ) == "ants version"
    bias_correct = mrt.DWIBiasCorrect()
    if ants_flag:
        algorithm = "ANTs"
        bias_correct.inputs.use_ants = True
    else:
        algorithm = "FSL"
        bias_correct.inputs.use_fsl = True
    bias_correct.inputs.in_file = in_file
    bias_correct.inputs.out_file = out_file
    return bias_correct, algorithm


def calculate_metrics(in_file: Path, out_files: dict):
    """
    Calculate various DWI metrics based on Diffusion's kurtosis tensor
    estimation.

    Parameters
    ----------
    in_file : Path
        Path to preprocessed DWI series
    out_files : dict
        A dictionary containing paths to various metrics to be calculated
    """
    tensor = out_files.pop("tensor")
    tsr = mrt.FitTensor()
    tsr.inputs.in_file = in_file
    tsr.inputs.out_file = tensor
    tsr.inputs.args = "-quiet"
    if not tensor.exists():
        tsr.run()
    comp = mrt.TensorMetrics()
    comp.inputs.in_file = tensor
    comp_args = ""
    for key, val in out_files.items():
        comp_args += f"-{key} {val} "
    comp.inputs.args = comp_args
    return tsr, comp
