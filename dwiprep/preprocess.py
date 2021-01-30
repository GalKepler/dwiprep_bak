from dwiprep import messages
from dwiprep.utils.fetch_files import fetch_additional_files
from dwiprep.utils import conversions, mrtrix_functions
from pathlib import Path
from termcolor import colored
import warnings


class PreprocessPipeline:
    INPUT_KEYS = "anatomical", "ap", "pa"

    def __init__(self, input_dict: dict, output_dir: Path):
        self.validate_input(input_dict)
        self.input_dict = input_dict
        self.rearange_inputs()
        self.longitudinal = False
        self.infer_longitudinal()
        self.expand_input_dict()

        self.validate_output(output_dir)
        self.output_dir = Path(output_dir)

    def validate_input(self, input_dict: dict):
        """
        Validates that the keys passed to the class correspond with the ones expected.
        Raises
        ------
        ValueError
            [Informs the user about the mismatch between given key and expected keys]
        """
        for key in input_dict:
            if key.lower() not in self.INPUT_KEYS:
                message = messages.BAD_INPUT.format(
                    key=key, keys=self.INPUT_KEYS
                )
                message = colored(message, "red")
                raise ValueError(message)

    def validate_output(self, output_dir: Path):
        """
        Checks whether the output directory for subject's preprocessing derivatives exists.
        Initiates it otherwise.
        Parameters
        ----------
        output_dir : Path
            [Path to output directory]
        """
        self.output_dict = {}
        for session in self.input_dict:
            self.output_dict[session] = {}
            session_derivatives = output_dir / session
            self.output_dict[session]["directory"] = session_derivatives
            if not session_derivatives.exists():
                message = messages.OUTPUT_NOT_EXIST.format(
                    output_dir=output_dir
                )
                warnings.warn(message)
                session_derivatives.mkdir()

    def infer_longitudinal(self):
        """
        Defines whether the preprocessing pipeline will include between-sessions registrations (i.e longitudinal preprocessing)
        Raises
        ------
        ValueError
            [Informs the user about various types of values in given input_dict.
            All values must be either lists (longitudinal) or PathLike objects (single)]
        """
        value_type = set([type(value) for value in self.input_dict.values()])
        if len(value_type) > 1:
            message = messages.BAD_VALUE_TYPS.format(value_types=value_type)
            message = colored(message, "red")
            raise ValueError(message)
        else:
            value_type = value_type.pop()
        if value_type == list:
            self.longitudinal = True

    def rearange_inputs(self):
        """
        Rearanges inputs dictionary to match corresponding sessions for ease of use
        """
        num_sessions = len(self.input_dict.get("ap"))
        updated_dict = {}
        for session in range(num_sessions):
            session_label = f"ses-{session+1}"
            updated_dict[session_label] = {}
            for key, vals in self.input_dict.items():
                updated_dict[session_label][f"{key}"] = {}
                updated_dict[session_label][f"{key}"]["nii"] = vals[session]
        self.input_dict = updated_dict

    def expand_input_dict(self):
        """
        updates additional .json/.bvec/.bval files corresponding to given input NIfTI files
        """
        expended_dict = self.input_dict.copy()
        for session, session_dict in self.input_dict.items():
            for key in session_dict:
                nii = self.input_dict.get(session).get(key).get("nii")
                expended_dict[session][f"{key}"][
                    "json"
                ] = fetch_additional_files(nii, parameter="json")
            for parameter in ["bvec", "bval"]:
                expended_dict[session]["ap"][
                    parameter
                ] = fetch_additional_files(
                    self.input_dict.get(session).get("ap").get("nii"),
                    parameter=parameter,
                )
        self.input_dict = expended_dict

    def convert_format(
        self,
        session: str,
        session_dict: dict,
        target_dir: Path,
    ):
        """
        Convert NIfTI files to .mif format for compatability with MRTrix3's commands.
        Parameters
        ----------
        session : str
            [key representing a session within the dataset.]
        session_dict : dict
            [Dictionary containing paths to session-relevant files.]
        target_dir : Path
            [Path to user-defined session's output directory.]
        """
        for modality, vals in session_dict.items():
            target_file = target_dir / f"{modality}.mif"
            if target_file.exists():
                message = messages.FILE_EXISTS.format(fname=target_file)
                message = colored(message, "yellow")
                warnings.warn(message)
            else:
                converter = conversions.mrtrix_conversion(vals, target_file)
                message = messages.CONVERT_TO_MIF.format(
                    in_file=vals.get("nii"),
                    out_file=target_file,
                    command=converter.cmdline,
                )
                message = colored(message, "green")
                print(message)
                converter.run()

            self.output_dict[session][f"{modality}_mif"] = target_file

    def average_b0(
        self,
        session: str,
        target_dir: Path,
    ):
        """
        Calculate DWI series' mean B0 image for later registrations
        Parameters
        ----------
        session : str
            [key representing a session within the dataset.]
        target_dir : Path
            [Path to user-defined session's output directory.]
        """
        in_file = self.output_dict.get(session).get("ap_mif")
        out_b0s = target_dir / "b0s.mif"
        out_file = target_dir / "mean_b0.mif"
        if out_file.exists():
            message = messages.FILE_EXISTS.format(fname=target_file)
            message = colored(message, "yellow")
            warnings.warn(message)
        else:
            b0s_extracter, b0s_averager = mrtrix_functions.extract_b0(
                in_file, out_b0s, out_file
            )
            message = messages.AVERAGE_B0.format(
                in_file=in_file,
                out_b0s=out_b0s,
                command_1=b0s_extracter.cmdline,
                out_file=out_file,
                command_2=b0s_averager.cmdline,
            )
            message = colored(message, "green")
            print(message)
            b0s_averager.run()
        self.output_dict[session]["mean_b0"] = out_file

    def run_pipeline(self):
        for session, session_dict in self.input_dict.items():
            target_dir = self.output_dict.get(session).get("directory")
            self.convert_format(session, session_dict, target_dir)
            self.average_b0(session, target_dir)
