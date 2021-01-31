from pathlib import Path
import nipype.interfaces.fsl as fsl


def calculate_transforms(
    ses_1_b0: Path, ses_2_b0: Path, reg_dir: Path
) -> dict:
    registered_files = {}
    for in_file, ref_file, aff_title in zip(
        [ses_1_b0, ses_2_b0], [ses_2_b0, ses_1_b0], ["pre2post", "post2pre"]
    ):
        registered_files[aff_title] = {}
        out_initial_aff = reg_dir / f"{aff_title}.mat"
        out_aff = reg_dir / f"{aff_title}_half.mat"
        out_file = reg_dir / f"{aff_title}.nii.gz"
        registered_files[aff_title]["Transform_matrix"] = out_aff
        registered_files[aff_title]["Transformed_file"] = out_file
        if not out_file.exists():
            print(
                "Calculating transformation from post intervention image to pre intervention image"
            )
            cmd_1 = f"flirt -in {in_file} -ref {ref_file} -omat {out_initial_aff} -cost mutualinfo"
            cmd_2 = f"avscale {out_initial_aff} | grep -A 4 Forward | tail -n 4 > {out_aff}"
            cmd_3 = f"flirt -in {in_file} -ref {ses_1_b0} -out {out_file} -applyxfm -init {out_aff} -cost mutualinfo"
            cmd_4 = f"rm {out_initial_aff}"
            for cmd in [cmd_1, cmd_2, cmd_3, cmd_4]:
                print(cmd)
                os.system(cmd)
    return registered_files


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