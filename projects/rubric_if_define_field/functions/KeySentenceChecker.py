class KeySentenceChecker(Instruction):
    """Check the existence of certain key sentences."""

    def build_description(self, key_sentences=None, num_sentences=None):
        """Build the instruction description.

        Args:
          key_sentences: A sequences of strings representing the key sentences that
            are expected in the response.
          num_sentences: The number of key sentences that are expected to be seen in
            the response.

        Returns:
          A string representing the instruction description.
        """

        if not key_sentences:
            # TODO(jeffrey) make a generate sentences function? wonderwords package
            self._key_sentences = set(["For now, this is fine."])
        else:
            self._key_sentences = key_sentences

        if not num_sentences:
            self._num_sentences = random.randint(1, len(self._key_sentences))
        else:
            self._num_sentences = num_sentences

        self._description_pattern = "Include {num_sentences} of the following sentences {key_sentences}"

        return self._description_pattern.format(num_sentences=self._num_sentences, key_sentences=self._key_sentences)

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"num_sentences": self._num_sentences, "key_sentences": list(self._key_sentences)}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["num_sentences", "key_sentences"]

    def check_following(self, value):
        """Checks if the response contains the expected key sentences."""
        count = 0
        sentences = instructions_util.split_into_sentences(value)
        for sentence in self._key_sentences:
            if sentence in sentences:
                count += 1

        return count == self._num_sentences


