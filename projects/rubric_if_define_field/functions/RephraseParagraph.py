class RephraseParagraph(Instruction):
    """Checks that the paragraph is rephrased."""

    def build_description(self, *, original_paragraph, low, high):
        """Builds the instruction description.

        Args:
          original_paragraph: A string presenting the original paragraph. The
            rephrases response should have betweeb low-high words in common.
          low: An integer presenting the lower bound of similar words.
          high: An integer representing the upper bound of similar words.

        Returns:
          A string representing the instruction description.
        """
        # TODO(jeffrey) make more encompassing
        self._original_paragraph = original_paragraph
        self._low = low
        self._high = high

        self._description = (
            "Rephrase the following paragraph: "
            + "{original_paragraph}\nYour response should have "
            + "between {low} and {high} of the same words. "
            + "Words are the same if and only if all of the "
            + "letters, ignoring cases, are the same. For "
            + "example, 'run' is the same as 'Run' but different "
            + "to 'ran'."
        )

        return self._description.format(original_paragraph=original_paragraph, low=self._low, high=self._high)

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"original_paragraph": self._original_paragraph, "low": self._low, "high": self._high}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["original_paragraph", "low", "high"]

    def check_following(self, value):
        val_words = re.findall(r"\w+", value.lower())
        original_words = re.findall(r"\w+", self._original_paragraph.lower())
        similar_words = 0

        dict_val = collections.Counter(val_words)
        dict_original = collections.Counter(original_words)

        for word in dict_original:
            similar_words += min(dict_original[word], dict_val[word])

        return similar_words >= self._low and similar_words <= self._high


