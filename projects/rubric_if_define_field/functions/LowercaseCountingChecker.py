class LowercaseCountingChecker(Instruction):
    "In your response, all lowercase words should appear at most {N} times."

    def build_description(self, N=None):
        """Build the instruction description.

        Args:
        N: An integer representing the maximum number of lowercase words allowed.

        Returns:
        A string representing the instruction description.
        """
        if not N:
            self._N = random.randint(2, 3)
        else:
            self._N = N
        self._description_pattern = "In your response, all lowercase words should appear at most {N} times."
        return self._description_pattern.format(N=self._N)

    def get_instruction_args(self):
        return {"N": self._N}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["N"]

    def check_following(self, value):
        """Checks that the response does not contain lowercase words more than N times."""
        lowercase_words = re.findall(r"\b[a-z]+\b", value)
        return len(lowercase_words) <= self._N


