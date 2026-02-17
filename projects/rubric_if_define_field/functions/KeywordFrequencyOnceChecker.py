class KeywordFrequencyOnceChecker(Instruction):
    """Check the keyword frequency."""

    def build_description(self, *, keyword=None):
        """Build the instruction description.

        Args:
          keyword: A string representing a keyword that is expected in the response.
          frequency: An integer specifying the number of times `keyword` is expected
            to appear in the response.
          relation: A string in (`less than`, `at least`), defining the relational
            operator for comparison.
            Two relational comparisons are supported for now:
            if 'less than', the actual number of occurrences < frequency;
            if 'at least', the actual number of occurrences >= frequency.

        Returns:
          A string representing the instruction description.
        """
        if not keyword:
            self._keyword = instructions_util.generate_keywords(num_keywords=1)[0]
        else:
            self._keyword = keyword.strip()

        self._frequency = 1

        self._description_pattern = "Include keyword {keyword} in your response."

        return self._description_pattern.format(keyword=self._keyword, frequency=self._frequency)

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"keyword": self._keyword}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["keyword"]

    def check_following(self, value):
        """Checks if the response contain the keyword with required frequency."""
        actual_occurrences = len(re.findall(self._keyword, value, flags=re.IGNORECASE))

        return actual_occurrences == 1


