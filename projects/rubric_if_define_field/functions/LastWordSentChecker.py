class LastWordSentChecker(Instruction):
    """The last word of each sentence should be the word {last_word}."""

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
            if not isinstance(last_word, str):
                self._last_word = last_word[0].strip()
            else:
                self._last_word = last_word.strip()

        self._description_pattern = (
            "The last word of each sentence, before punctuation, should be the word {last_word}."
        )

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
        sentences = instructions_util.split_into_sentences(value)

        # Check if the first word of each sentence matches the expected word
        for sentence in sentences:
            if not sentence.strip():
                return False
            last_word = sentence.split()[-1].strip()
            # remove any punctuation from last_word
            last_word = re.sub(r"[^\w\s]", "", last_word)
            if last_word.lower() != self._last_word.lower():
                return False
        return True


