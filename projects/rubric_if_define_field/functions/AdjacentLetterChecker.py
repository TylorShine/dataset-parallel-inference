class AdjacentLetterChecker(Instruction):
    """No two adjacent words can start with consecutive letters of the alphabet."""

    def build_description(self):
        """Build the instruction description."""
        self._description_pattern = "No two adjacent words can start with consecutive letters of the alphabet."
        return self._description_pattern

    def get_instruction_args(self):
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks if no two adjacent words start with consecutive letters of the alphabet."""
        words = value.split()
        for i in range(len(words) - 1):
            first_letter = words[i][0].lower()
            second_letter = words[i + 1][0].lower()
            if len(first_letter) != 1 or len(second_letter) != 1:
                return False
            if ord(second_letter) - ord(first_letter) == 1:
                return False
        return True


