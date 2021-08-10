import os
import warnings
from pathlib import Path

from dwiprep.preprocessing import messages
from dwiprep.preprocessing.utils import conversions, mrtrix_functions
from dwiprep.preprocessing.utils.fetch_files import fetch_additional_files
from dwiprep.registrations.registrations import RegistrationsPipeline
from termcolor import colored


class PreprocessPipeline:
    INPUT_KEYS = "anatomical", "ap", "pa"

    def __init__(self, input_dict: dict, output_dir: Path):
        """
        Initiate the PreprocessPipeline instance.

        Parameters
        ----------
        input_dict : dict
            Input dictionary containing "anatomical", "ap" and "pa" keys
        output_dir : Path
            Path to subject's output derivatives directory
        """
        self.longitudinal = False
        self.infer_longitudinal(input_dict)
        self.validate_input(input_dict)
        self.input_dict = input_dict
        # print(self.input_dict)
        self.rearrange_inputs()
        self.expand_input_dict()

        self.validate_output(output_dir)
        self.output_dir = Path(output_dir)

    def validate_input(self, input_dict: dict):
        """
        Validates that the keys passed to the class correspond with the ones
        expected.

        Raises
        ------
        ValueError
            Informs the user about the mismatch between given key and
            expected keys
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
        Checks whether the output directory for subject's preprocessing
        derivatives exists, otherwise, initiates it.

        Parameters
        ----------
        output_dir : Path
            Path to output directory
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
                session_derivatives.mkdir(parents=True)

    def infer_longitudinal(self, input_dict: dict):
        """
        Defines whether the preprocessing pipeline will include
        between-sessions registrations (i.e longitudinal preprocessing).

        Raises
        ------
        ValueError
            Informs the user about various types of values in given
            input_dict. All values must be either lists (longitudinal) or
            PathLike objects (single)
        """
        value_type = set([type(value) for value in input_dict.values()])
        if len(value_type) > 1:
            message = messages.BAD_VALUE_TYPES.format(value_types=value_type)
            message = colored(message, "red")
            raise ValueError(message)
        else:
            value_type = value_type.pop()
        if value_type == list:
            self.longitudinal = True

    def rearrange_inputs(self):
        """
        Rearanges inputs dictionary to match corresponding sessions for ease
        of use.
        """
        num_sessions = len(
            self.input_dict.get("ap")
            if isinstance(self.input_dict.get("ap"), list)
            else [self.input_dict.get("ap")]
        )
        print(num_sessions)
        updated_dict = {}
        for session in range(num_sessions):
            print(session)
            session_label = f"ses-{session+1}"
            updated_dict[session_label] = {}
            for key, vals in self.input_dict.items():
                vals = vals if isinstance(vals, list) else [vals]
                updated_dict[session_label][f"{key}"] = {}
                updated_dict[session_label][f"{key}"]["nii"] = vals[session]
        self.input_dict = updated_dict

    def expand_input_dict(self):
        """
        updates additional .json/.bvec/.bval files corresponding to given
        input NIfTI files.
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
        Convert NIfTI files to .mif format for compatability with MRTrix3's
        commands.

        Parameters
        ----------
        session : str
            Key representing a session within the dataset
        session_dict : dict
            Dictionary containing paths to session-relevant files
        target_dir : Path
            Path to user-defined session's output directory
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
        in_file: Path,
        out_suffix: str,
        target_dir: Path,
        corrected: bool = False,
    ):
        """
        Calculate DWI series' mean B0 image for later registrations.

        Parameters
        ----------
        session : str
            Key representing a session within the dataset
        target_dir : Path
            Path to user-defined session's output directory
        """
        # in_file = self.output_dict.get(session).get("ap_mif")
        out_b0s = target_dir / f"b0s.{out_suffix}"
        out_file = target_dir / f"mean_b0.{out_suffix}"
        if out_file.exists():
            message = messages.FILE_EXISTS.format(fname=out_file)
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

    def merge_phase_opposites(
        self, session: str, session_dict: dict, target_dir: Path
    ):
        """
        Merge phase opposites (AP-PA) images across the 4th dimension for
        compatibillity with dwifslpreproc function.

        Parameters
        ----------
        session : str
            Key representing a session within the dataset
        session_dict : dict
            Dictionary containing paths to session-relevant files
        target_dir : Path
            Path to user-defined session's output directory
        """
        ap, pa = [
            self.output_dict.get(session).get(key)
            for key in ["mean_b0", "pa_mif"]
        ]
        out_file = target_dir / "merged_phasediff.mif"
        if out_file.exists():
            message = messages.FILE_EXISTS.format(fname=out_file)
            message = colored(message, "yellow")
            warnings.warn(message)
        else:
            cmd = mrtrix_functions.merge_phasediff(ap, pa, out_file)
            message = messages.MERGE_PHASEDIFF.format(
                ap=ap, pa=pa, merged=out_file, command=cmd
            )
            message = colored(message, "green")
            print(message)
            os.system(cmd)
        self.output_dict[session]["merged_phasediff"] = out_file

    def correct_sdc(self, session: str, target_dir: Path):
        """
        Use MRTrix3's dwifslpreproc function to perform susceptabillity
        distortion correction on DWI series.

        Parameters
        ----------
        session : str
            Key representing a session within the dataset
        target_dir : Path
            Path to user-defined session's output directory
        """
        in_file, merged_phasediff = [
            self.output_dict.get(session).get(key)
            for key in ["ap_mif", "merged_phasediff"]
        ]
        out_file = target_dir / "SDC_corrected.mif"
        if out_file.exists():
            message = messages.FILE_EXISTS.format(fname=out_file)
            message = colored(message, "yellow")
            warnings.warn(message)
        else:
            cmd = mrtrix_functions.correct_sdc(
                in_file, merged_phasediff, out_file
            )
            message = messages.CORRECT_SDC.format(
                ap=in_file,
                merged=merged_phasediff,
                out_file=out_file,
                command=cmd,
            )
            message = colored(message, "green")
            print(message)
            os.system(cmd)
        self.output_dict[session]["sdc_corrected"] = out_file

    def correct_bias_field(self, session: str, target_dir: Path):
        """
        Perform DWI B1 field inhomogenity correction.

        Parameters
        ----------
        session : str
            Key representing a session within the dataset
        target_dir : Path
            Path to user-defined session's output directory
        """
        in_file = self.output_dict.get(session).get("sdc_corrected")
        out_file = target_dir / "bias_corrected.mif"
        if out_file.exists():
            message = messages.FILE_EXISTS.format(fname=out_file)
            message = colored(message, "yellow")
            warnings.warn(message)
        else:
            executer, algorithm = mrtrix_functions.correct_bias_field(
                in_file, out_file
            )
            if algorithm.lower() == "fsl":
                message = messages.ANTS_NOT_FOUND.format(
                    antspath=os.environ.get("ANTSPATH")
                )
                message = colored(message, "yellow")
                warnings.warn(message)
            message = messages.CORRECT_BIAS.format(
                algorithm=algorithm,
                in_file=in_file,
                out_file=out_file,
                command=executer.cmdline,
            )
            message = colored(message, "green")
            print(message)
            executer.run()
        self.output_dict[session]["preprocessed"] = out_file

    def calculate_metrics(self, session: Path, target_dir: Path):
        """
        Calculate various metrics of DWI series (MD, FA, etc.).

        Parameters
        ----------
        session : str
            Key representing a session within the dataset
        target_dir : Path
            Path to user-defined session's output directory
        """
        in_file = self.output_dict.get(session).get("preprocessed")
        tensor_dir = target_dir / "tensors_parameters" / "native"
        if not tensor_dir.exists():
            message = messages.OUTPUT_NOT_EXIST.format(output_dir=tensor_dir)
            message = colored(message, "yellow")
            warnings.warn(message)
            tensor_dir.mkdir(parents=True)

        out_files = {
            key: tensor_dir / f"{value}.mif"
            for key, value in zip(
                [
                    "tensor",
                    "adc",
                    "fa",
                    "ad",
                    "rd",
                    "cl",
                    "cp",
                    "cs",
                    "value",
                    "vector",
                ],
                [
                    "tensor",
                    "MD",
                    "FA",
                    "AD",
                    "RD",
                    "CL",
                    "CP",
                    "CS",
                    "EigenValue",
                    "EigenVector",
                ],
            )
        }
        flags = [val.exists() for val in out_files.values()]
        if all(flags):
            fname = ""
            for val in out_files.values():
                fname += f"\n{val}"
            message = messages.FILE_EXISTS.format(fname=fname)
            message = colored(message, "yellow")
            warnings.warn(message)
        else:
            tensor_exec, metrics_exec = mrtrix_functions.calculate_metrics(
                in_file, out_files.copy()
            )
            tensor, md, fa, ad, rd, cl, cp, cs, val, vec = out_files.values()
            message = messages.CALCULATE_TENSOR.format(
                in_file=in_file,
                tensor=tensor,
                command_1=tensor_exec.cmdline,
                md=md,
                fa=fa,
                ad=ad,
                rd=rd,
                cl=cl,
                cp=cp,
                cs=cs,
                val=val,
                vec=vec,
                command_2=metrics_exec.cmdline,
            )
            message = colored(message, "green")
            print(message)
            metrics_exec.run()
        out_files["directory"] = tensor_dir
        self.output_dict[session]["tensors"] = out_files

    def run_corrections(self):
        """
        Peform the "correction" part of the pipeline, i.e cleaning the data
        in native-space.
        """
        for session, session_dict in self.input_dict.items():
            print(session)
            target_dir = self.output_dict.get(session).get("directory")
            self.convert_format(session, session_dict, target_dir)
            self.average_b0(
                session,
                self.output_dict.get(session).get("ap_mif"),
                "mif",
                target_dir,
            )
            self.merge_phase_opposites(session, session_dict, target_dir)
            self.correct_sdc(session, target_dir)
            self.correct_bias_field(session, target_dir)
            self.calculate_metrics(session, target_dir)

    def run_registrations(self, atlas: dict = None, use_matlab: bool = True):
        """
        Apply the registration pipeline via the RegisterationPipeline instance.

        Parameters
        ----------
        atlas : dict, optional
            Dictionary with "path" and "name" of a parcellation atlas in MNI
            space, by default None
        use_matlab : bool, optional
            If True, use SPM's CAT12 anatomical preprocessing pipeline, otherwise
            use fsl_anat script, by default True
        """
        registrations_dir = self.output_dir / "registrations"
        if not registrations_dir.exists():
            message = messages.OUTPUT_NOT_EXIST.format(
                output_dir=registrations_dir
            )
            message = colored(message, "yellow")
            warnings.warn(message)
            registrations_dir.mkdir()
        self.registrations = RegistrationsPipeline(
            self.output_dict,
            registrations_dir,
            self.longitudinal,
            atlas,
            use_matlab=use_matlab,
        )
        self.registrations.run()
