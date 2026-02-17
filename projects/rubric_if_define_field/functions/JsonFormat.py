class JsonFormat(Instruction):
    """Check the Json format."""

    def build_description(self):
        self._description_pattern = (
            "Entire output should be wrapped in JSON format. You can use markdown ticks such as ```."
        )
        return self._description_pattern

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        value = (
            value.strip()
            .removeprefix("```json")
            .removeprefix("```Json")
            .removeprefix("```JSON")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )
        try:
            json.loads(value)
        except ValueError:
            return False
        return True


