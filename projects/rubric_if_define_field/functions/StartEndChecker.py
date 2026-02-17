class StartEndChecker(Instruction):
    "Start and end your response with the same word (do not write anything after the last word, not even punctuation)."

    def build_description(self):
        """Build the instruction description."""
        self._description_pattern = "Start and end your response with the same word (do not write anything after the last word, not even punctuation)."
        return self._description_pattern

    def get_instruction_args(self):
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks if the response starts and ends with the same word.

        Args:
          value: A string representing the response.

        Returns:
          True if the response starts and ends with the same word;
          otherwise, False.
        """
        words = instructions_util.nltk.word_tokenize(value)
        if len(words) < 2:
            return False
        return words[0].lower() == words[-1].lower()
