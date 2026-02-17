class BiGramWrappingChecker(Instruction):
    "Wrap every word bigram in double angular brackets, such as <<I am>> <<at home>> <<with my>> <<cute dog>>."

    def build_description(self):
        """Build the instruction description."""
        self._description_pattern = (
            "Wrap every word bigram in double angular brackets, such as <<I am>> <<at home>> <<with my>> <<cute dog>>."
        )
        return self._description_pattern

    def get_instruction_args(self):
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks if every word bigram is enclosed within double angular brackets."""
        words = value.split()
        for i in range(0, len(words) - 1, 2):
            if i + 1 < len(words) and not (words[i].startswith("<<") and words[i + 1].endswith(">>")):
                return False
        return True


