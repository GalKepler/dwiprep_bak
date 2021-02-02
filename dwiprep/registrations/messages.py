### ERRORS ###
MISSING_KEYS_LONGITUDIANL = """There are not enough sessions ({num_sessions}) to refer to the pipeline as longitudinal."""

### WARNINGS ###
MULTIPLE_SESSIONS_WARNING = """There are multiple sessions ({num_sessions}) found, but the pipeline is not about to perform longitudinal registrations, and will register each session seperately.
"""
FILE_EXISTS = "Tried to create an existing file\s: {fname}. To avoid unneccesary computations, This procedure is skipped. To re-create the file\s, please delete the existing one."


### MESSAGES ###
CONVERT_TO_NII = """Converting file to NIfTI (.nii.gz) format for compatability with used functions...
Input file: {in_file}
Output file: {out_file}
Command: {command}
"""
COREGISTER = """Registering between-session {img_type} images.
This procedure includes: 
(1) Linear registration of images to each other (bidirectional)
Commands: 
{cmd_1_a}
{cmd_1_b}
(2) Calculation of halfway transformation matrices (to register for a midway space)
Commands: 
{cmd_2_a}
{cmd_2_b}
(3) Linear registration of original images to halfway space, using calculated transforms:
Commands:
{cmd_3_a}
{cmd_3_b}
"""
AVERAGE_IMAGES = """Averaging coregistered {img_type} images.
Inputs:
    1. pre2post image: {ses_1}
    1. post2pre image: {ses_2}
Output:
    Averaged file: {out_file}
Command: 
    {cmd}
"""
APPLY_XFM = """Applying pre-calculated transformation matrix on tensor-derived parameter.
Input:
    {in_file}
Affine matrix:
    {aff}
Reference:
    {ref}
Output:
    {out_file}
Command:
    {command}

"""