class CopyingSimpleChecker(Instruction):
    "Repeat the request without change (do not say anything before repeating the request; the request you need to repeat does not include this sentence) and do not answer the actual request!"

    def build_description(self, prompt_to_repeat=None):
        """Build the instruction description.

        Args:
        prompt_to_repeat: The prompt that is meant to be repeated.

        Returns:
        A string representing the instruction description.
        """
        if not prompt_to_repeat:
            raise ValueError("prompt_to_repeat must be set.")
        else:
            self._prompt_to_repeat = prompt_to_repeat
        self._description_pattern = "Repeat the request without change (do not say anything before repeating the request; the request you need to repeat does not include this sentence) and do not answer the actual request!"
        return self._description_pattern

    def get_instruction_args(self):
        return {"prompt_to_repeat": self._prompt_to_repeat}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["prompt_to_repeat"]

    def check_following(self, value):
        return value.strip().lower() == self._prompt_to_repeat.strip().lower()


