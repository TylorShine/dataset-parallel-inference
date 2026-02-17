class FirstWordSentChecker(Instruction):
    """The first word of each sentence should be the word {first_word}."""

    def build_description(self, first_word=None):
        """Build the instruction description.

        Args:
        first_word: A string representing the first word of each sentence.

        Returns:
        A string representing the instruction description.
        """
        if not first_word:
            self._first_word = instructions_util.generate_keywords(num_keywords=1)[0]
        else:
            if not isinstance(first_word, str):
                self._first_word = first_word[0].strip()
            else:
                self._first_word = first_word.strip()

        self._description_pattern = "The first word of each sentence should be the word {first_word}."

        return self._description_pattern.format(first_word=self._first_word)

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"first_word": self._first_word}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["first_word"]

    def check_following(self, value):
        """Checks if the first word of each sentence is the expected word.

        Args:
          value: A string representing the response.

        Returns:
          True if the first word of each sentence is the expected word;
          otherwise, False.
        """
        sentences = instructions_util.split_into_sentences(value)

        # Check if the first word of each sentence matches the expected word
        for sentence in sentences:
            if not sentence.strip():
                return False
            first_word = sentence.split()[0].strip()
            if first_word.lower() != self._first_word.lower():
                return False
        return True


