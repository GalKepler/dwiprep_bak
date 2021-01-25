from dwiprep import messages
from dwiprep.utils.fetch_files import fetch_additional_files
from dwiprep.utils import conversions
from pathlib import Path
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

        self.convert_format()

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
                warnings.warn(messages)
                output_dir.mkdir()

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

    def convert_format(self, session: str):
        """
        Convert NIfTI files to .mif format for compatability with MRTrix3's commands.
        """
        target_dir = self.output_dict.get(session).get("directory")
        session_dict = self.input_dict.get(session)
        for modality, vals in session_dict.items():
            target_file = target_dir / f"{modality}.mif"
            if target_file.exists():
                message = messages.FILE_EXISTS.format(fname=target_file)
                warnings.warn(message)
            else:
                conversions.mrtrix_conversion(vals, target_file)
            self.output_dict[session][f"{modality}_mif"] = target_file