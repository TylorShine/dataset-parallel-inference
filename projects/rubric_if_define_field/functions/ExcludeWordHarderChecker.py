class ExcludeWordHarderChecker(Instruction):
    """Checks that specified words are not used in response."""

    def build_description(self, keyword=None, instruction=None):
        """Build the instruction description.

        Args:
          forbidden_words: A sequences of strings respresenting words that are not
            allowed in the response.

        Returns:
          A string representing the instruction description.
        """
        if not keyword:
            self._keyword = random.choice(instruction.split())
        else:
            self._keyword = keyword.strip()

        self._description_pattern = "Do not include keyword {keyword} in the response."

        return self._description_pattern.format(keyword=self._keyword)

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"keyword": self._keyword}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["keyword"]

    def check_following(self, value):
        """Check if the response does not contain the expected keywords."""
        return " " + self._keyword + " " not in value


