class KeywordFrequencyCheckerDifferent(Instruction):
    """Check the keyword frequency."""

    def build_description(self, *, keyword=None, frequency=None, relation=None):
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

        self._frequency = frequency
        if self._frequency is None or self._frequency < 0:
            self._frequency = random.randint(1, _KEYWORD_FREQUENCY)

        if relation is None:
            self._comparison_relation = random.choice(_COMPARISON_RELATION)
        elif relation not in _COMPARISON_RELATION:
            raise ValueError(
                f"The supported relation for comparison must be in {_COMPARISON_RELATION}, but {relation} is given."
            )
        else:
            self._comparison_relation = relation

        self._description_pattern = "In your response, the word {keyword} should appear {frequency} times."

        return self._description_pattern.format(
            keyword=self._keyword, relation=self._comparison_relation, frequency=self._frequency
        )

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"keyword": self._keyword, "frequency": self._frequency, "relation": self._comparison_relation}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["keyword", "frequency", "relation"]

    def check_following(self, value):
        """Checks if the response contain the keyword with required frequency."""
        actual_occurrences = len(re.findall(self._keyword, value, flags=re.IGNORECASE))

        if self._comparison_relation == _COMPARISON_RELATION[0]:
            return actual_occurrences < self._frequency
        elif self._comparison_relation == _COMPARISON_RELATION[1]:
            return actual_occurrences >= self._frequency  # pytype: disable=bad-return-type


