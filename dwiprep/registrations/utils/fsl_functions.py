from pathlib import Path
import nipype.interfaces.fsl as fsl
from dwiprep.preprocessing.utils.conversions import mrtrix_conversion


def register_between_sessions(
    ses_1: Path, ses_2: Path, img_type: str, target_dir: Path
) -> dict:
    """
    Perform a series of manipulations on both sessions' images to register them to midway space.
    Parameters
    ----------
    ses_1 : Path
        Path to first session's image
    ses_2 : Path
        Path to second session's image
    img_type : str
        Either "mean_b0" or "anatomical"
    target_dir : Path
        Path to output directory

    Returns
    -------
    dict
        Dןictionary containing path to output files.
    """
    registered_files = {}
    cmds = []
    for in_file, ref_file, aff_title in zip(
        [ses_1, ses_2], [ses_2, ses_1], ["pre2post", "post2pre"]
    ):
        registered_files[aff_title] = {}
        out_initial_aff = target_dir / f"{img_type}_{aff_title}.mat"
        out_aff = target_dir / f"{img_type}_{aff_title}_half.mat"
        out_file = target_dir / f"{img_type}_{aff_title}.nii.gz"
        registered_files[aff_title]["Transform_matrix"] = out_aff
        registered_files[aff_title]["Transformed_file"] = out_file
        cmds.append(
            f"flirt -in {in_file} -ref {ref_file} -omat {out_initial_aff} -cost mutualinfo"
        )
        cmds.append(
            f"avscale {out_initial_aff} | grep -A 4 Forward | tail -n 4 > {out_aff}"
        )
        cmds.append(
            f"flirt -in {in_file} -ref {ses_1} -out {out_file} -applyxfm -init {out_aff} -cost mutualinfo"
        )
        cmds.append(f"rm {out_initial_aff}")
    return registered_files, cmds


def average_images(in_files: list, out_file: Path):
    """
    Average multiple images
    Parameters
    ----------
    in_files : list
        a list of paths to files to average
    out_file : Path
        Path to output mean image
    """
    cmd = f"fsladd {out_file} -m"
    for in_file in in_files:
        cmd += f" {in_file}"
    return cmd


def apply_xfm_to_mifs(
    in_file: Path,
    aff: Path,
    ref: Path,
    target_dir: Path,
):
    """
    Apply pre-calculated transformation matrix to numerous image files.
    Parameters
    ----------
    in_files : list
        A list of paths to images to be registered
    aff : Path
        Path to pre-calculated transformation matrix
    target_dir : Path
        Path to output directory
    keep_tmps : bool, optional
        Whether to keep intermidiate files, by default False
    """
    out_nii = target_dir / f"{in_file.name.split('.')[0]}_tmp.nii.gz"
    out_registered = target_dir / f"{in_file.name.split('.')[0]}.nii.gz"
    if not out_registered.exists():
        mrconvert = mrtrix_conversion({"nii": in_file}, out_nii)
        mrconvert.run()
        executer = apply_xfm(out_nii, ref, aff, out_registered)
    else:
        executer = None

    return executer, out_nii, out_registered


def apply_xfm(in_file: Path, ref: Path, aff: Path, out_file: Path):
    """
    Apply pre-calculated transformation matrix to file
    Parameters
    ----------
    in_file : Path
        Path to file to be registered
    ref : Path
        Path to reference image
    aff : Path
        Path to pre-calculated transformation matrix
    out_file : Path
        Path to output file
    """
    applyxfm = fsl.FLIRT()
    applyxfm.inputs.in_file = in_file
    applyxfm.inputs.in_matrix_file = aff
    applyxfm.inputs.out_file = out_file
    applyxfm.inputs.cost = "mutualinfo"
    applyxfm.inputs.out_matrix_file = "tmp"
    applyxfm.inputs.reference = ref
    applyxfm.inputs.apply_xfm = True
    return applyxfm


def linear_registration(
    in_file: Path,
    ref: Path,
    out_file: Path,
    out_mat: Path = None,
    coregister: bool = False,
):
    """
    Wrap inputs into FSL's FLIRT interface for linear registraions
    Parameters
    ----------
    in_file : Path
        Path to "moving" file
    ref : Path
        Path to reference file
    out_file : Path
        Path to output registered file
    coregister : bool, optional
        Indicating whether it's a within-subject registration, by default False
    """
    if not out_mat:
        out_mat = (
            out_file.parent
            / f"{in_file.name.split('.')[0]}-{ref.name.split('.')[0]}_affine.mat"
        )
    flt = fsl.FLIRT()
    flt.inputs.in_file = in_file
    flt.inputs.reference = ref
    flt.inputs.out_file = out_file
    if coregister:
        flt.inputs.cost = "mutualinfo"
    flt.inputs.out_matrix_file = out_mat
    return flt