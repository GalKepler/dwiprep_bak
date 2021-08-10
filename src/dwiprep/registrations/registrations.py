import gzip
import os
import shutil
import warnings
from pathlib import Path

from dwiprep.preprocessing import messages as preproc_messages
from dwiprep.preprocessing.utils import conversions, mrtrix_functions
from dwiprep.registrations import messages
from dwiprep.registrations.utils import fsl_functions, matlab_functions
from termcolor import colored


class RegistrationsPipeline:
    def __init__(
        self,
        preprocess_dict: dict,
        target_dir: Path,
        longitudinal: bool,
        atlas: dict = None,
        use_matlab: bool = False,
    ):
        """
        Initiate the RegistrationPipeline instance.

        Parameters
        ----------
        preprocess_dict : dict
            A dictionary containing keys and values of subject's "corrected"
            data
        target_dir : Path
            Path to subject's output derivatives directory
        longitudinal : bool
            Whether to perform within-subject, cross-sessions registration
        atlas : dict, optional
            Dictionary with "path" and "name" of a parcellation atlas in MNI
            space, by default None
        use_matlab : bool, optional
            If True, use SPM's CAT12 anatomical preprocessing pipeline,
            otherwise use fsl_anat script, by default True
        """
        self.registrations_dict, self.sessions = self.initiate_registrations(
            preprocess_dict, target_dir
        )
        self.longitudinal = longitudinal
        self.atlas = atlas
        self.infer_longitudinal()
        if use_matlab:
            self.use_matlab = matlab_functions.check_matlab()

    def infer_longitudinal(self):
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
        num_sessions = len(self.registrations_dict.keys()) - 1
        if self.longitudinal and (num_sessions < 2):
            message = messages.MISSING_KEYS_LONGITUDIANL.format(
                num_sessions=num_sessions
            )
            message = colored(message, "red")
            raise ValueError(message)
        elif (not self.longitudinal) and num_sessions > 1:
            message = messages.MULTIPLE_SESSIONS_WARNING.format(
                num_sessions=num_sessions
            )
            message = colored(message, "yellow")
            warnings.warn(message)

    def initiate_registrations(
        self, preprocess_dict: dict, target_dir: Path
    ) -> dict:
        """
        Extracts relevant files from the subject's "corrected" dictionary.

        Parameters
        ----------
        preprocess_dict : dict
            Subject's "corrected" dictionary (i.e result of the
            PreprocessPipeline run)
        target_dir : Path
            Path to subject's output derivatives directory

        Returns
        -------
        dict
            Dictionary defining subject's derivatives' paths
        list
            List defining session found in subject's data
        """
        registration_dict = {"directory": target_dir}
        sessions = []
        for session, session_dict in preprocess_dict.items():
            sessions.append(session)
            preprocessed = session_dict.get("preprocessed")
            anatomical = session_dict.get("anatomical_mif")
            tensors = session_dict.get("tensors")
            registration_dict[session] = {
                "initial": {
                    "anatomical": anatomical,
                    "dwi": preprocessed,
                    "tensors": tensors,
                }
            }
        return registration_dict, sessions

    def convert_to_nii(self, in_files: list, target_dir: Path):
        """
        Convert MRTrix's .mif format to NIfTI for compatability with FSL's
        functions.

        Parameters
        ----------
        in_files : list
            List of files to convert
        target_dir : Path
            Path of directory of converted files
        """
        target_dir = target_dir / "anatomical"
        target_dir.mkdir(exist_ok=True)
        out_files = []
        for in_file, session in zip(in_files, self.sessions):
            out_fname = f"{in_file.name.split('.')[0]}_{session}.nii.gz"
            out_file = target_dir / out_fname
            if out_file.exists():
                message = messages.FILE_EXISTS.format(fname=out_file)
                message = colored(message, "yellow")
                warnings.warn(message)
            else:
                executer = conversions.mrtrix_conversion(
                    {"nii": in_file}, out_file
                )
                message = messages.CONVERT_TO_NII.format(
                    in_file=in_file,
                    out_file=out_file,
                    command=executer.cmdline,
                )
                message = colored(message, "green")
                print(message)
                executer.run()
            out_files.append(out_file)
            self.registrations_dict[session]["anatomical"] = out_file

    def average_b0(self, target_dir: Path):
        """
        Average preprocessed B0 volumes.

        Parameters
        ----------
        target_dir : Path
            Path to subject's output directory
        """
        target_dir = target_dir / "mean_b0"
        target_dir.mkdir(exist_ok=True)
        for session in self.sessions:
            in_file = (
                self.registrations_dict.get(session).get("initial").get("dwi")
            )
            out_b0s = in_file.with_name("preprocessed_b0s.nii.gz")
            out_file = target_dir / f"mean_b0_{session}.nii.gz"
            if out_file.exists():
                message = messages.FILE_EXISTS.format(fname=out_file)
                message = colored(message, "yellow")
                warnings.warn(message)
            else:
                b0s_extracter, b0s_averager = mrtrix_functions.extract_b0(
                    in_file, out_b0s, out_file
                )
                message = preproc_messages.AVERAGE_B0.format(
                    in_file=in_file,
                    out_b0s=out_b0s,
                    command_1=b0s_extracter.cmdline,
                    out_file=out_file,
                    command_2=b0s_averager.cmdline,
                )
                message = colored(message, "green")
                print(message)
                b0s_averager.run()
            self.registrations_dict[session]["mean_b0"] = out_file

    def coregister(self, img_type: str, target_dir: Path):
        """
        Co-register between-sessions images of the same type.

        Parameters
        ----------
        img_type : str
            One of the keys in self.registrations_dict[session]
        target_dir : Path
            Path to output directory
        """
        pre, post = [
            self.registrations_dict.get(session).get(img_type)
            for session in self.sessions
        ]
        target_dir = target_dir / img_type
        target_dir.mkdir(exist_ok=True)
        registered_files, cmds = fsl_functions.register_between_sessions(
            pre, post, img_type, target_dir
        )
        out_files = [
            Path(
                registered_files.get(aff_title).get("Transformed_file")
            ).exists()
            for aff_title in ["pre2post", "post2pre"]
        ]
        if all(out_files):
            for fname in out_files:
                message = messages.FILE_EXISTS.format(fname=fname)
                message = colored(message, "yellow")
                warnings.warn(message)
        else:
            print(len(cmds))
            cmd_1_a, cmd_2_a, cmd_3_a, cmd_1_b, cmd_2_b, cmd_3_b, _, _ = cmds
            message = messages.COREGISTER.format(
                img_type=img_type,
                cmd_1_a=cmd_1_a,
                cmd_1_b=cmd_1_b,
                cmd_2_a=cmd_2_a,
                cmd_2_b=cmd_2_b,
                cmd_3_a=cmd_3_a,
                cmd_3_b=cmd_3_b,
            )
            message = colored(message, "green")
            print(message)
            for cmd in cmds:
                os.system(cmd)
        for session, aff_title in zip(self.sessions, registered_files.keys()):
            self.registrations_dict[session][
                f"coreg_affine_{img_type}"
            ] = registered_files.get(aff_title).get("Transform_matrix")
            self.registrations_dict[session][
                f"coreg_{img_type}"
            ] = registered_files.get(aff_title).get("Transformed_file")

    def average_coregistered(self, img_type: str, target_dir: Path):
        """
        Averages multiple images.

        Parameters
        ----------
        img_type : str
            String that is a key within session's dictionary
        target_dir : Path
            Path to output directory
        """
        target_dir = target_dir / img_type
        target_dir.mkdir(exist_ok=True)
        in_files = [
            self.registrations_dict.get(session).get(f"coreg_{img_type}")
            for session in self.sessions
        ]
        out_file = target_dir / f"mean_coregistered_{img_type}.nii.gz"
        if out_file.exists():
            message = messages.FILE_EXISTS.format(fname=out_file)
            message = colored(message, "yellow")
            warnings.warn(message)
        else:
            cmd = fsl_functions.average_images(in_files, out_file)
            message = messages.AVERAGE_IMAGES.format(
                img_type=img_type,
                ses_1=in_files[0],
                ses_2=in_files[1],
                out_file=out_file,
                cmd=cmd,
            )
            message = colored(message, "green")
            print(message)
            os.system(cmd)
        self.registrations_dict[img_type] = out_file

    def register_tensors(
        self,
        ref: Path,
        keep_tmps: bool = False,
    ):
        """
        Apply calculated transformation matrices to tensors-derived parameters
        images.

        Parameters
        ----------
        ref : Path
            Path to "reference" file (i.e the file to which the tensors
            parameters will be registered to)
        keep_tmps : bool, optional
            Whether to keep intermidiate files, by default False
        """
        for session in self.sessions:
            coreg_tensors = {}
            if self.longitudinal:
                aff = self.registrations_dict.get(session).get("epi2t1w")
            else:
                aff = self.registrations_dict.get("epi2anatomical").get(
                    "affine"
                )
            tensors = (
                self.registrations_dict.get(session)
                .get("initial")
                .get("tensors")
            )
            tensors_dir = tensors.pop("directory").parent / "coregistered"
            tensors_dir.mkdir(exist_ok=True)
            for key, val in tensors.items():
                executer, tmp, flag = fsl_functions.apply_xfm_to_mifs(
                    val, aff, ref, tensors_dir
                )
                if flag.exists():
                    message = messages.FILE_EXISTS.format(fname=flag)
                    message = colored(message, "yellow")
                    warnings.warn(message)
                else:
                    message = messages.APPLY_XFM.format(
                        in_file=val,
                        aff=aff,
                        ref=ref,
                        out_file=flag,
                        command=executer.cmdline,
                    )
                    message = colored(message, "green")
                    print(message)
                    executer.run()
                    Path(executer.inputs.out_matrix_file).unlink()
                    if not keep_tmps:
                        tmp.unlink()
                coreg_tensors[key] = flag
            self.registrations_dict[session]["coreg_tensors"] = coreg_tensors

    def skull_strip(self, in_file: Path):
        """
        Use FSL's BET to remove skull.

        Parameters
        ----------
        in_file : Path
            Path to whole-head image
        """
        out_file = (
            in_file.parent / f"{in_file.name.split('.')[0]}_brain.nii.gz"
        )
        if out_file.exists():
            message = messages.FILE_EXISTS.format(fname=out_file)
            message = colored(message, "yellow")
            warnings.warn(message)
        else:
            bet = fsl_functions.skull_strip(in_file, out_file)
            message = messages.SKULL_STRIP.format(
                in_file=in_file, out_file=out_file, command=bet.cmdline
            )
            message = colored(message, "green")
            print(message)
            bet.run()
        return out_file

    def register_epi_to_anatomical(self, target_dir: Path):
        """
        Apply coregistration using a wrapper for FSL's epi_reg script.

        Parameters
        ----------
        target_dir : Path
            Path to output directory
        """
        in_file, ref = [
            self.registrations_dict.get(img_type)
            for img_type in ["mean_b0", "anatomical"]
        ]
        ref_brain = self.skull_strip(ref)
        out_prefix = target_dir / "epi2anatomical"
        out_file = out_prefix.with_suffix(".nii.gz")
        out_mat = out_prefix.with_suffix(".mat")
        if out_mat.exists():
            message = messages.FILE_EXISTS.format(fname=out_mat)
            message = colored(message, "yellow")
            warnings.warn(message)
        else:
            cmd = fsl_functions.epi_reg(in_file, ref, ref_brain, out_prefix)
            message = messages.EPI_REG.format(
                epi=in_file,
                anat=ref,
                anat_brain=ref_brain,
                out_file=out_file,
                out_mat=out_mat,
                command=cmd,
            )
            message = colored(message, "green")
            print(message)
            os.system(cmd)
        self.registrations_dict["epi2anatomical"] = {
            "image": out_file,
            "affine": out_mat,
        }

    def combine_between_session_affines(self, target_dir: Path):
        """
        Combine the within-subjects and between-modalities affines.

        Parameters
        ----------
        target_dir : Path
            Path to output directory
        """
        epi2t1w = self.registrations_dict.get("epi2anatomical").get("affine")
        for session in self.sessions:
            between_sessions = self.registrations_dict.get(session).get(
                "coreg_affine_mean_b0"
            )
            out_file = target_dir / f"{session}_epi2anatomical.mat"
            if out_file.exists():
                message = messages.FILE_EXISTS.format(fname=out_file)
                message = colored(message, "yellow")
                warnings.warn(message)
            else:
                cmd = fsl_functions.concat_affines(
                    between_sessions, epi2t1w, out_file
                )
                message = messages.CONCAT_AFFINES.format(
                    between_sessions=between_sessions,
                    epi2t1w=epi2t1w,
                    out_file=out_file,
                    command=cmd,
                )
                message = colored(message, "green")
                print(message)
                os.system(cmd)
            self.registrations_dict[session]["epi2t1w"] = out_file

    def preprocess_anat(self, target_dir: Path):
        """
        Wrapper for fsl_anat function for anatomical preprocessing.

        Parameters
        ----------
        target_dir : Path
            Path to output preprocessing directory
        """
        anat_file = self.registrations_dict.get("anatomical")
        out_dir = target_dir / "preprocessed_FSL"
        if out_dir.with_suffix(".anat").exists():
            message = messages.FILE_EXISTS.format(
                fname=out_dir.with_suffix(".anat")
            )
            message = colored(message, "yellow")
            warnings.warn(message)
        else:
            cmd = fsl_functions.preprocess_anatomical(anat_file, out_dir)
            message = messages.PREPROCESS_ANAT.format(
                in_file=anat_file,
                out_dir=out_dir.with_suffix(".anat"),
                command=cmd,
            )
            message = colored(message, "green")
            print(message)
            os.system(cmd)
        self.registrations_dict["preprocessed_t1w"] = out_dir.with_suffix(
            ".anat"
        )

    def cat_preproc_anat(self, target_dir: Path):
        """
        Perform SPM's CAT12 anatomical preprocessing and normalization.

        Parameters
        ----------
        target_dir : Path
            Path to output directory
        """
        anat_file = self.registrations_dict.get("anatomical")
        out_dir = target_dir / "preprocessed_CAT"
        nii_name = anat_file.name.split(".")[0] + ".nii"
        anat_nii = out_dir / nii_name
        if anat_nii.exists():
            message = messages.FILE_EXISTS.format(fname=anat_nii)
            message = colored(message, "yellow")
            warnings.warn(message)
        else:
            message = messages.GUNZIP.format(
                anat_file=anat_file, anat_nii=anat_nii
            )
            message = colored(message, "green")
            print(message)
            out_dir.mkdir(exist_ok=True)
            with gzip.open(anat_file, "rb") as f_in:
                with open(anat_nii, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

        if Path(out_dir / "report").exists():
            flag = [
                f for f in Path(out_dir / "report").glob("catreport*.pdf")
            ][0]
            if flag:
                message = messages.FILE_EXISTS.format(fname=flag)
                message = colored(message, "yellow")
                warnings.warn(message)
        else:
            message = messages.PREPROCESS_CAT.format(
                in_file=anat_nii, out_dir=out_dir
            )
            message = colored(message, "green")
            print(message)
            matlab_functions.run_default_cat(anat_nii)
        self.registrations_dict["preprocessed_t1w"] = out_dir

    def normalize_tensors_fsl(self):
        """
        Apply pre-calculated transforms to tensor-derived parameters to
        normalize them into standard space.
        """
        warp = (
            self.registrations_dict.get("preprocessed_t1w")
            / "T1_to_MNI_nonlin_field.nii.gz"
        )
        ref = (
            Path(os.getenv("FSLDIR"))
            / "data"
            / "standard"
            / "MNI152_T1_2mm.nii.gz"
        )
        for session in self.sessions:
            norm_tensors = {}
            tensors = self.registrations_dict.get(session).get("coreg_tensors")
            tensors_dir = tensors.get("tensor").parents[1] / "normalized_FSL"
            tensors_dir.mkdir(exist_ok=True)
            for key, val in tensors.items():
                out_file = tensors_dir / val.name
                if out_file.exists():
                    message = messages.FILE_EXISTS.format(fname=out_file)
                    message = colored(message, "yellow")
                    warnings.warn(message)
                else:
                    executer = fsl_functions.apply_warp(
                        val, ref, warp, out_file
                    )
                    message = messages.APPLY_WARP.format(
                        in_file=val,
                        warp=warp,
                        ref=ref,
                        out_file=out_file,
                        command=executer.cmdline,
                    )
                    message = colored(message, "green")
                    print(message)
                    executer.run()
                norm_tensors[key] = out_file
            self.registrations_dict[session][
                "normalized_tensors"
            ] = norm_tensors

    def normalize_tensors_cat(self):
        """
        Apply pre-calculated transforms to tensor-derived parameters to
        normalize them into standard space.
        """
        warp = [
            f
            for f in self.registrations_dict.get("preprocessed_t1w").glob(
                "mri/y_*.nii"
            )
        ][0]
        for session in self.sessions:
            norm_tensors = {}
            tensors = self.registrations_dict.get(session).get("coreg_tensors")
            tensors_dir = tensors.get("tensor").parents[1] / "normalized_CAT"
            tensors_dir.mkdir(exist_ok=True)
            for key, val in tensors.items():
                out_file = tensors_dir / val.name
                if out_file.exists():
                    message = messages.FILE_EXISTS.format(fname=out_file)
                    message = colored(message, "yellow")
                    warnings.warn(message)
                else:
                    matlab_functions.apply_deformations(warp, val, 1, out_file)
                    message = messages.REGISTER_TENSORS_CAT.format(
                        in_file=val, warp=warp, out_file=out_file
                    )
                    message = colored(message, "green")
                    print(message)
                norm_tensors[key] = out_file
            self.registrations_dict[session][
                "normalized_tensors"
            ] = norm_tensors

    def register_parcellation_fsl(self):
        """
        Register parcellation from standard to subject's native space.
        """
        warp = (
            self.registrations_dict.get("preprocessed_t1w")
            / "MNI_to_T1_nonlin_field.nii.gz"
        )
        target = (
            self.registrations_dict.get("preprocessed_t1w")
            / "T1_biascorr_brain.nii.gz"
        )
        source = Path(self.atlas.get("path"))
        name = self.atlas.get("name")
        if not name:
            name = source.name.split(".")[0]
        name += "_native.nii.gz"
        out_file = self.registrations_dict.get("preprocessed_t1w") / name
        if out_file.exists():
            message = messages.FILE_EXISTS.format(fname=out_file)
            message = colored(message, "yellow")
            warnings.warn(message)
        else:
            executer = fsl_functions.apply_warp(
                source, target, warp, out_file, "nn"
            )
            message = messages.REGISTER_ATLAS.format(
                atlas=source,
                warp=warp,
                target=target,
                out_file=out_file,
                command=executer.cmdline,
            )
            message = colored(message, "green")
            print(message)
            executer.run()
        self.registrations_dict["native_atlas"] = out_file

    def register_parcellation_cat(self):
        """
        Register parcellation from standard to subject's native space.
        """
        warp = [
            f
            for f in self.registrations_dict.get("preprocessed_t1w").glob(
                "mri/iy_*.nii"
            )
        ][0]
        source = Path(self.atlas.get("path"))
        name = self.atlas.get("name")
        if not name:
            name = source.name.split(".")[0]
        name += "_native.nii.gz"
        out_file = self.registrations_dict.get("preprocessed_t1w") / name
        if out_file.exists():
            message = messages.FILE_EXISTS.format(fname=out_file)
            message = colored(message, "yellow")
            warnings.warn(message)
        else:
            matlab_functions.apply_deformations(warp, source, 0, out_file)
            message = messages.REGISTER_ATLAS_CAT.format(
                atlas=source,
                warp=warp,
                out_file=out_file,
            )
            message = colored(message, "green")
            print(message)
        self.registrations_dict["native_atlas"] = out_file

    def rearrange_non_longitudinal_inputs(self):
        """
        Rearrange dictionary to match expected structure as if it was longitudinal (won't perform longitudinal registration)
        """
        for img_type in ["mean_b0", "anatomical"]:
            for session in self.sessions:
                self.registrations_dict[
                    img_type
                ] = self.registrations_dict.get(session).get(img_type)

    def register_sessions(self, target_dir: Path):
        """
        Co-register within-subject images.

        Parameters
        ----------
        target_dir : Path
            Output directory path
        """
        [
            self.coregister(img_type, target_dir)
            for img_type in ["mean_b0", "anatomical"]
        ]
        [
            self.average_coregistered(img_type, target_dir)
            for img_type in ["mean_b0", "anatomical"]
        ]

    def run(self):
        target_dir = self.registrations_dict.get("directory")
        anat_files = [
            self.registrations_dict.get(session)
            .get("initial")
            .get("anatomical")
            for session in self.sessions
        ]
        self.convert_to_nii(anat_files, target_dir)
        self.average_b0(target_dir)
        if self.longitudinal:
            self.register_sessions(target_dir)
            self.register_epi_to_anatomical(target_dir)
            self.combine_between_session_affines(target_dir)
            self.register_tensors(self.registrations_dict.get("anatomical"))
            if self.use_matlab:
                self.cat_preproc_anat(target_dir)
                self.normalize_tensors_cat()
                if self.atlas:
                    self.register_parcellation_cat()
            else:
                self.preprocess_anat(target_dir)
                self.normalize_tensors_fsl()
                if self.atlas:
                    self.register_parcellation_fsl()
        else:
            self.rearrange_non_longitudinal_inputs()
            self.register_epi_to_anatomical(target_dir)
            self.register_tensors(self.registrations_dict.get("anatomical"))
            if self.use_matlab:
                self.cat_preproc_anat(target_dir)
                self.normalize_tensors_cat()
                if self.atlas:
                    self.register_parcellation_cat()
            else:
                self.preprocess_anat(target_dir)
                self.normalize_tensors_fsl()
                if self.atlas:
                    self.register_parcellation_fsl()
