class CopySpanIdxChecker(Instruction):
    """{prompt_to_repeat}. Copy the span of words that lies between (and including) index {n_start} and {n_end}, the indices are character indices!"""

    def build_description(self, prompt_to_repeat=None, n_start=None, n_end=None):
        """Build the instruction description.

        Args:
        n_start: An integer representing the start index of the span.
        n_end: An integer representing the end index of the span.

        Returns:
        A string representing the instruction description.
        """
        if not prompt_to_repeat:
            raise ValueError("prompt_to_repeat must be set.")
        else:
            self._prompt_to_repeat = prompt_to_repeat
        if not n_start:
            self._n_start = random.randint(0, len(self._prompt_to_repeat) - 2)
        else:
            self._n_start = n_start
        if not n_end:
            self._n_end = random.randint(self._n_start + 1, len(self._prompt_to_repeat) - 1)
        else:
            self._n_end = n_end
        self._description_pattern = "Copy the span of words that lies between (and including) index {n_start} and {n_end}, the indices are character indices!"
        return self._description_pattern.format(
            n_start=self._n_start, n_end=self._n_end, prompt_to_repeat=self._prompt_to_repeat
        )

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"n_start": self._n_start, "n_end": self._n_end, "prompt_to_repeat": self._prompt_to_repeat}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["n_start", "n_end", "prompt_to_repeat"]

    def check_following(self, value):
        """Checks if the response contains the expected number of phrases with the correct modifications."""
        return value.strip().lower() == self._prompt_to_repeat[self._n_start : self._n_end].strip().lower()


