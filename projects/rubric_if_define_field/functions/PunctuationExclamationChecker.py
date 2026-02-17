class PunctuationExclamationChecker(Instruction):
    "In your entire response, refrain from the use of ! (i.e. exclamation marks) as punctuation and in general."

    def build_description(self):
        """Build the instruction description."""
        self._description_pattern = "In your entire response, refrain from the use of ! (i.e. exclamation marks) as punctuation and in general."
        return self._description_pattern

    def get_instruction_args(self):
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks that the response does not contain exclamation marks."""
        return not re.search(r"\!", value)


