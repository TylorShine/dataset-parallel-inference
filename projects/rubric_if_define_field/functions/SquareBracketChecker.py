class SquareBracketChecker(Instruction):
    """Enclose every word in your response within square brackets."""

    def build_description(self):
        """Build the instruction description."""
        self._description_pattern = "Enclose every word in your response within square brackets."
        return self._description_pattern

    def get_instruction_args(self):
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks if every word in the response is enclosed within square brackets."""
        words = value.split()
        return all(word.startswith("[") and word.endswith("]") for word in words)


