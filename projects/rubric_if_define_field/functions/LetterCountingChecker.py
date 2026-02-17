class LetterCountingChecker(Instruction):
    "Answer with {relation} {N} letters."

    def build_description(self, N=None, relation=None):
        """Build the instruction description.

        Args:
        N: An integer representing the maximum number of letters allowed.

        Returns:
        A string representing the instruction description.
        """
        if not N:
            self._N = random.randint(2, 3)
        else:
            self._N = N
        if not relation:
            self._relation = random.choice(_COMPARISON_RELATION)
        else:
            self._relation = relation
        self._description_pattern = "Answer with {relation} {N} letters."
        return self._description_pattern.format(N=self._N, relation=self._relation)

    def get_instruction_args(self):
        return {"N": self._N, "relation": self._relation}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["N", "relation"]

    def check_following(self, value):
        """Checks that the response does not contain lowercase words more than N times."""
        letters = re.findall(r"[a-zA-Z]", value)
        if self._relation == "at least":
            return len(letters) >= self._N
        elif self._relation == "less than":
            return len(letters) < self._N


