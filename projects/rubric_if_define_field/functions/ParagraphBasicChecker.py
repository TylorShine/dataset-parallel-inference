class ParagraphBasicChecker(Instruction):
    """Checks the paragraphs."""

    def build_description(self):
        """Build the instruction description.

        Args:
          num_paragraphs: An integer specifying the number of paragraphs.

        Returns:
          A string representing the instruction description.
        """
        self._description_pattern = (
            "There should be 2 paragraphs. " + "Paragraphs are separated with the markdown divider: ***"
        )

        return self._description_pattern

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks the response contains required number of paragraphs.

        Args:
          value: A string representing the response. The response may contain
            paragraphs that are separated by the markdown divider: `***`.

        Returns:
          True if the actual number of paragraphs is the same as required;
          otherwise, False.
        """
        paragraphs = re.split(r"\s?\*\*\*\s?", value)
        num_paragraphs = len(paragraphs)

        for index, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                if index == 0 or index == len(paragraphs) - 1:
                    num_paragraphs -= 1
                else:
                    return False

        return num_paragraphs == 2


