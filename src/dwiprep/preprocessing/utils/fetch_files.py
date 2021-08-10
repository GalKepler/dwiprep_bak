from pathlib import Path

from dwiprep.preprocessing import messages


def fetch_additional_files(nii: Path, parameter: str):
    """
    Searches for json, .bvec and .bval files corresponding to a list of NIfTI
    files' paths.

    Parameters
    ----------
    inputs : list
        A list of NIfTI files' paths

    Returns
    -------
    Union[List[PathLike], PathLike]
        Either a single or multiple PathLike objects representing existing
        .json/.bvec/.bval files

    Raises
    ------
    FileNotFoundError
        If a corresponding .json/.bvec/.bval file does not exist under the
        same directory as the NIfTI, notify the user
    """
    nii = Path(nii)
    fname = nii.parent / nii.name.split(".")[0]
    additional_file = fname.with_suffix(f".{parameter}")
    if not additional_file.exists():
        message = messages.ADDITIONAL_NOT_FOUND.format(
            parameter=parameter, fname=nii, dname=nii.parent
        )
        raise FileNotFoundError(message)
    return additional_file
