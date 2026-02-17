class CopyingMultipleChecker(Instruction):
    "Repeat the request without change {N} times, separated by 6 asterisk symbols (do not say anything before repeating the request; the request you need to repeat does not include this sentence) and do not answer the actual request!"

    def build_description(self, prompt_to_repeat=None, N=None):
        """Build the instruction description.

        Args:
        prompt_to_repeat: The prompt that is meant to be repeated.
        N: An integer representing the number of times to repeat the phrase.

        Returns:
        A string representing the instruction description.
        """
        if not prompt_to_repeat:
            raise ValueError("prompt_to_repeat must be set.")
        else:
            self._prompt_to_repeat = prompt_to_repeat
        if not N:
            self._N = random.randint(2, 3)
        else:
            self._N = N
        self._description_pattern = "Repeat the request without change {N} times, separated by 6 asterisk symbols (do not say anything before repeating the request; the request you need to repeat does not include this sentence) and do not answer the actual request!"
        return self._description_pattern.format(N=self._N)

    def get_instruction_args(self):
        return {"prompt_to_repeat": self._prompt_to_repeat, "N": self._N}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["prompt_to_repeat", "N"]

    def check_following(self, value):
        prompts = value.split("******")
        if len(prompts) != self._N:
            return False
        return all(prompt.strip().lower() == self._prompt_to_repeat.strip().lower() for prompt in prompts)


