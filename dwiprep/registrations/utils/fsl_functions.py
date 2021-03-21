from pathlib import Path

import nipype.interfaces.fsl as fsl
from dwiprep.preprocessing.utils.conversions import mrtrix_conversion


def register_between_sessions(
    ses_1: Path, ses_2: Path, img_type: str, target_dir: Path
) -> dict:
    """
    Perform a series of manipulations on both sessions' images to register
    them to midway space.

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
        Dןictionary containing path to output files
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
            f"flirt -in {in_file} -ref {ref_file} \
            -omat {out_initial_aff} -cost mutualinfo"
        )
        cmds.append(
            f"avscale {out_initial_aff} | grep -A 4 Forward | \
            tail -n 4 > {out_aff}"
        )
        cmds.append(
            f"flirt -in {in_file} -ref {ses_1} -out {out_file} -applyxfm -init\
             {out_aff} -cost mutualinfo"
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
    Apply pre-calculated transformation matrix to file.

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
    Wrap inputs into FSL's FLIRT interface for linear registraions.

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
        in_name = in_file.name.split(".")[0]
        ref_name = ref.name.split(".")[0]
        out_mat = out_file.parent / f"{in_name}-{ref_name}_affine.mat"
    flt = fsl.FLIRT()
    flt.inputs.in_file = in_file
    flt.inputs.reference = ref
    flt.inputs.out_file = out_file
    if coregister:
        flt.inputs.cost = "mutualinfo"
    flt.inputs.out_matrix_file = out_mat
    return flt


def skull_strip(in_file: Path, out_file: Path):
    """
    Use FSL's BET for skull removal
    Parameters
    ----------
    in_file : Path
        Path to whole-head image
    out_file : Path
        Path to output brain image
    """
    bet = fsl.BET()
    bet.inputs.in_file = in_file
    bet.inputs.out_file = out_file
    bet.inputs.robust = True
    return bet


def epi_reg(epi: Path, anat: Path, anat_brain: Path, out_prefix: Path):
    """
    Apply coregistration using a wrapper for FSL's epi_reg script
    Parameters
    ----------
    epi : Path
        Path to EPI (DWI) image
    anat : Path
        Path to whole-head anatomical image
    anat_brain : Path
        Path to skull-stipped anatomical image
    out_prefix : Path
        Path to output coregistered image
    """
    cmd = f"epi_reg --epi={epi} --t1={anat} --t1brain={anat_brain} \
    --out={out_prefix}"

    return cmd


def concat_affines(affine_1: Path, affine_2: Path, out_file: Path):
    """
    Concatenate multiple affine transformations into one.

    Parameters
    ----------
    affine_1 : Path
        Path to first affine matrix
    affine_2 : Path
        Path to second affine matrix
    out_file : Path
        Path to output combined matrix
    """
    cmd = f"convert_xfm -omat {out_file} -concat {affine_2} {affine_1}"
    return cmd


def preprocess_anatomical(in_file: Path, out_dir: Path):
    """
    Wrapper for fsl_anat function for anatomical preprocessing.

    Parameters
    ----------
    in_file : Path
        Path to raw T1 image
    out_dir : Path
        Path to output preprocessing directory
    """
    cmd = f"fsl_anat -i {in_file} -o {out_dir}"
    return cmd


def apply_warp(
    in_file: Path, ref: Path, warp: Path, out_file: Path, interp: str = None
):
    """
    Apply pre-calculated warp field coefficients to normalize an image.

    Parameters
    ----------
    in_file : Path
        Path to image to be normalized
    ref : Path
        Path to reference image
    warp : Path
        Path to pre-calculated warp field
    out_file : Path
        Path to output warped image
    """
    aw = fsl.ApplyWarp()
    aw.inputs.in_file = in_file
    aw.inputs.ref_file = ref
    aw.inputs.field_file = warp
    aw.inputs.out_file = out_file
    if interp:
        aw.inputs.interp = interp
    return aw
