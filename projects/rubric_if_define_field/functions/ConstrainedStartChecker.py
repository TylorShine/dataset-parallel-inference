class ConstrainedStartChecker(Instruction):
    """Checks the response start."""

    def build_description(self, *, starter=None):
        """Build the instruction description.

        Args:
          starter: A string representing the keyward that the response should start
            with.

        Returns:
          A string representing the instruction description.
        """
        self._starter = starter.strip() if isinstance(starter, str) else starter
        if self._starter is None:
            self._starter = random.choice(_STARTER_OPTIONS)
        self._description_pattern = (
            "During the conversation, when it is your turn, " + "please always start with {starter}"
        )
        return self._description_pattern.format(starter=self._starter)

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"starter": self._starter}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["starter"]

    def check_following(self, value):
        """Checks if the response starts with the constrained keyword or phrase.

        Args:
          value: A string representing the response.

        Returns:
          True if the response starts with the given phrase or keyword that is
          contained in `instruction_args`; otherwise, False.
        """
        response_pattern = r"^\s*" + self._starter + r".*$"
        response_with_constrained_start = re.search(response_pattern, value, flags=re.MULTILINE)
        return bool(response_with_constrained_start)


