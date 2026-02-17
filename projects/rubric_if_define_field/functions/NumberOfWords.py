class NumberOfWords(Instruction):
    """Checks the number of words."""

    def build_description(self, *, num_words=None, relation=None):
        """Build the instruction description.

        Args:
          num_words: An integer specifying the number of words contained in the
            response.
          relation: A string in (`less than`, `at least`), defining the relational
            operator for comparison.
            Two relational comparisons are supported for now:
            if 'less than', the actual number of words < num_words;
            if 'at least', the actual number of words >= num_words.

        Returns:
          A string representing the instruction description.
        """

        self._num_words = num_words
        if self._num_words is None or self._num_words < 0:
            self._num_words = random.randint(_NUM_WORDS_LOWER_LIMIT, _NUM_WORDS_UPPER_LIMIT)

        if relation is None:
            self._comparison_relation = random.choice(_COMPARISON_RELATION)
        elif relation not in _COMPARISON_RELATION:
            raise ValueError(
                f"The supported relation for comparison must be in {_COMPARISON_RELATION}, but {relation} is given."
            )
        else:
            self._comparison_relation = relation

        self._description_pattern = "Answer with {relation} {num_words} words."

        return self._description_pattern.format(relation=self._comparison_relation, num_words=self._num_words)

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"num_words": self._num_words, "relation": self._comparison_relation}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["num_words", "relation"]

    def check_following(self, value):
        """Checks if the response contains the expected number of words."""
        num_words = instructions_util.count_words(value)

        if self._comparison_relation == _COMPARISON_RELATION[0]:
            return num_words < self._num_words
        elif self._comparison_relation == _COMPARISON_RELATION[1]:
            return num_words >= self._num_words  # pytype: disable=bad-return-type


