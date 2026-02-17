class CountUniqueChecker(Instruction):
    "Only use unique words in your response, no word should be repeated!"

    def build_description(self):
        """Build the instruction description."""
        self._description_pattern = "Only use unique words in your response, no word should be repeated!"
        return self._description_pattern

    def get_instruction_args(self):
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks that the response contains unique words."""
        words = instructions_util.nltk.word_tokenize(value)
        unique_words = set(words)
        return len(words) == len(unique_words)


