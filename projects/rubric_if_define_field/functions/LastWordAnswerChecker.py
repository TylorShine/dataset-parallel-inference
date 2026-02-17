class LastWordAnswerChecker(Instruction):
    """The last word of your response should be the word {last_word}."""

    def build_description(self, last_word=None):
        """Build the instruction description.

        Args:
        first_word: A string representing the last word of each sentence.

        Returns:
        A string representing the instruction description.
        """
        if not last_word:
            self._last_word = instructions_util.generate_keywords(num_keywords=1)[0]
        else:
            self._last_word = last_word.strip()

        self._description_pattern = "The last word of your response should be the word {last_word}."

        return self._description_pattern.format(last_word=self._last_word)

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"last_word": self._last_word}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["last_word"]

    def check_following(self, value):
        """Checks if the first word of each sentence is the expected word.

        Args:
          value: A string representing the response.

        Returns:
          True if the first word of each sentence is the expected word;
          otherwise, False.
        """
        last_word = value.split()[-1].strip()
        # remove any punctuation from last_word
        last_word = re.sub(r"[^\w\s]", "", last_word)
        return last_word.lower() == self._last_word.lower()


