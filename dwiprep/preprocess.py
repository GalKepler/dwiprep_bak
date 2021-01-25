from dwiprep import messages


class PreprocessPipeline:
    INPUT_KEYS = "anatomical", "ap", "pa"

    def __init__(self, input_dict: dict):
        self.validate_input(input_dict)
        self.input_dict = input_dict
        self.longitudinal = False
        self.infer_longitudinal()

    def validate_input(self, input_dict: dict):
        """

        Raises
        ------
        ValueError
            [description]
        """
        for key in input_dict:
            if key.lower() not in self.INPUT_KEYS:
                message = messages.BAD_INPUT.format(
                    key=key, keys=self.INPUT_KEYS
                )
                raise ValueError(message)

    def infer_longitudinal(self):
        value_type = set([type(value) for value in self.input_dict.values()])
        if len(value_type) > 1:
            raise ValueError
        else:
            value_type = value_type.pop()
        if value_type == list:
            self.longitudinal = True

    def correct_sdc():
        