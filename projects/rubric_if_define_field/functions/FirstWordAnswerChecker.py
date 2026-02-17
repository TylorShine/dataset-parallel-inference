class FirstWordAnswerChecker(Instruction):
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
            self._first_word = first_word.strip()

        self._description_pattern = "The first word of your response should be the word {first_word}."

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
        if not value.strip() or len(value.split()) == 0:
            return False
        first_word = value.split()[0].strip()
        return first_word.lower() == self._first_word.lower()


