class PalindromeBasicChecker(Instruction):
    "Include a palindrome in your response."

    def build_description(self):
        """Build the instruction description."""
        self._description_pattern = "Include a palindrome in your response."
        return self._description_pattern

    def get_instruction_args(self):
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks if the response contains a palindrome.

        Args:
          value: A string representing the response.

        Returns:
          True if the response contains a palindrome; otherwise, False.
        """
        palindromes = [word for word in value.split() if word == word[::-1]]
        return len(palindromes) > 0


