import gzip
import shutil
from pathlib import Path

ADD_PATH = Path(__file__).parent.absolute()
CAT_TEMPLATE = ADD_PATH / "run_default_cat.m"


def check_matlab():
    try:
        import ssl

        import matlab.engine

        return True
    except ModuleNotFoundError:
        return False


def run_default_cat(anat_file: Path):
    import ssl

    import matlab.engine

    eng = matlab.engine.start_matlab()
    eng.addpath(str(ADD_PATH))
    eng.run_default_cat(str(anat_file), nargout=0)


def apply_deformations(
    warp_file: Path, in_file: Path, interp: int, out_file: Path
):
    import ssl

    import matlab.engine

    tmp = in_file.parent / f"{in_file.name.split('.')[0]}.nii"
    if not tmp.exists():
        with gzip.open(in_file, "rb") as f_in:
            with open(tmp, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        in_file = tmp
    else:
        in_file = tmp
    flag = in_file.parent / f"w{in_file.name}"
    eng = matlab.engine.start_matlab()
    eng.addpath(str(ADD_PATH))
    eng.cat_apply_deformation(str(warp_file), str(tmp), interp, nargout=0)
    tmp.unlink()
    with open(flag, "rb") as f_in:
        with gzip.open(out_file, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    flag.unlink()


# flake8: noqa: F401
