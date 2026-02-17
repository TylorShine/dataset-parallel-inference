class CountIncrementWordChecker(Instruction):
    "Include keyword {keyword1} once in your response, keyword {keyword2} twice in your response."

    def build_description(self, keyword1=None, keyword2=None):
        """Build the instruction description.

        Args:
        keyword1: A string representing a keyword that is expected in the response.
        keyword2: A string representing a keyword that is expected in the response.

        Returns:
        A string representing the instruction description.
        """
        if not keyword1:
            self._keyword1 = instructions_util.generate_keywords(num_keywords=1)
        else:
            self._keyword1 = keyword1.strip()
        if not keyword2:
            self._keyword2 = instructions_util.generate_keywords(num_keywords=1)
        else:
            self._keyword2 = keyword2.strip()

        self._description_pattern = (
            "Include keyword {keyword1} once in your response, keyword {keyword2} twice in your response."
        )

        return self._description_pattern.format(keyword1=self._keyword1, keyword2=self._keyword2)

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"keyword1": self._keyword1, "keyword2": self._keyword2}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["keyword1", "keyword2"]

    def check_following(self, value):
        """Checks if the response contains the expected number of keywords.

        Args:
          value: A string representing the response.

        Returns:
          True if the response contains the expected number of keywords;
          otherwise, False.
        """
        actual_occurrences1 = len(re.findall(self._keyword1, value, flags=re.IGNORECASE))
        actual_occurrences2 = len(re.findall(self._keyword2, value, flags=re.IGNORECASE))

        return bool(actual_occurrences1 == 1 and actual_occurrences2 == 2)


