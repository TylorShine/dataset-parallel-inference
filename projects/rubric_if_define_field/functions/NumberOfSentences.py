class NumberOfSentences(Instruction):
    """Check the number of sentences."""

    def build_description(self, *, num_sentences=None, relation=None):
        """Build the instruction description.

        Args:
          num_sentences: An integer specifying the number of sentences as a
            threshold.
          relation: A string in (`less than`, `at least`), defining the relational
            operator for comparison.
            Two relational comparisons are supported for now:
            if 'less than', the actual number of sentences < the threshold;
            if 'at least', the actual number of sentences >= the threshold.

        Returns:
          A string representing the instruction description.
        """
        # The number of sentences as a threshold for comparison.
        self._num_sentences_threshold = num_sentences
        if self._num_sentences_threshold is None or self._num_sentences_threshold < 0:
            self._num_sentences_threshold = random.randint(1, _MAX_NUM_SENTENCES)

        if relation is None:
            self._comparison_relation = random.choice(_COMPARISON_RELATION)
        elif relation not in _COMPARISON_RELATION:
            raise ValueError(
                f"The supported relation for comparison must be in {_COMPARISON_RELATION}, but {relation} is given."
            )
        else:
            self._comparison_relation = relation

        self._description_pattern = "Your response should contain {relation} {num_sentences} sentences."
        return self._description_pattern.format(
            relation=self._comparison_relation, num_sentences=self._num_sentences_threshold
        )

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"num_sentences": self._num_sentences_threshold, "relation": self._comparison_relation}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["num_sentences", "relation"]

    def check_following(self, value):
        """Check if the number of sentences follows the instruction.

        Args:
          value: A string representing the response.

        Returns:
          True if the response follows the instruction.

        Raise:
            ValueError if the string in `instruction_args` is not in
            [`less_than`, `at_least`].
        """
        num_sentences = instructions_util.count_sentences(value)
        if self._comparison_relation == _COMPARISON_RELATION[0]:
            return num_sentences < self._num_sentences_threshold
        elif self._comparison_relation == _COMPARISON_RELATION[1]:
            return num_sentences >= self._num_sentences_threshold  # pytype: disable=bad-return-type


