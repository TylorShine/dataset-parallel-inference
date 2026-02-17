class ConstrainedResponseChecker(Instruction):
    """Checks the constrained response."""

    def build_description(self):
        """Build the instruction description."""
        # A sequence of string(s) representing the options of the expected response.
        self._constrained_responses = _CONSTRAINED_RESPONSE_OPTIONS
        self._description_pattern = "Answer with one of the following options: {response_options}"
        return self._description_pattern.format(response_options=self._constrained_responses)

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks if the response matches the constrained options.

        Args:
          value: A string representing the response.

        Returns:
          True if the actual response contains one of the options in the constrained
          responses; otherwise False.
        """
        value = value.strip()
        return any(constrained_response in value for constrained_response in self._constrained_responses)


