from pathlib import Path
import warnings
from dwiprep.preprocessing.preprocess import PreprocessPipeline


def parse_subject(input_dir: Path, output_dir: Path, subj_id: str):
    print(subj_id)
    try:
        anats = sorted(
            input_dir.glob(f"{subj_id}/ses*/anat/*acq-corrected*.nii*")
        )[0]
    except IndexError:
        anats = sorted(input_dir.glob(f"{subj_id}/ses*/anat/*T1w*.nii*"))[0]
    subj_output = output_dir / subj_id
    try:
        aps = sorted(
            [f for f in input_dir.glob(f"{subj_id}/ses*/dwi/*dir-AP*.nii*")]
        )[0]
        pas = [
            f
            for f in sorted(
                input_dir.glob(f"{subj_id}/ses*/fmap/*dir-PA*.nii*")
            )
            if "func" not in f.name
        ][0]
    except IndexError:
        warnings.warn(
            f"Could not found opposite-directed EPI images for {subj_id}!"
        )
        return None

    input_dict = {"anatomical": anats, "ap": aps, "pa": pas}
    preprocess_pipe = PreprocessPipeline(input_dict, subj_output)
    return preprocess_pipe
