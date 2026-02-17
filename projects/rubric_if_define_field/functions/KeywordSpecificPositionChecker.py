class KeywordSpecificPositionChecker(Instruction):
    "Include keyword {keyword1} in the {n}-th sentence, as the {m}-th word of that sentence."

    def build_description(self, keyword=None, n=None, m=None):
        """Build the instruction description.

        Args:
          keyword: A string representing a keyword that is expected in the response.
          n: An integer representing the sentence number.
          m: An integer representing the word number.

        Returns:
          A string representing the instruction description.
        """
        if not keyword:
            self._keyword = instructions_util.generate_keywords(num_keywords=1)[0]
        else:
            if not isinstance(keyword, str):
                self._keyword = keyword[0].strip()
            else:
                self._keyword = keyword.strip()
        if not n:
            self._n = random.randint(1, 20)
        else:
            self._n = n
        if not m:
            self._m = random.randint(1, 30)
        else:
            self._m = m

        self._description_pattern = (
            "Include keyword {keyword} in the {n}-th sentence, as the {m}-th word of that sentence."
        )

        return self._description_pattern.format(keyword=self._keyword, n=self._n, m=self._m)

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"keyword": self._keyword, "n": self._n, "m": self._m}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["keyword", "n", "m"]

    def check_following(self, value):
        """Checks if the response contains the expected number of keywords.

        Args:
          value: A string representing the response.

        Returns:
          True if the response contains the expected number of keywords;
          otherwise, False.
        """
        sentences = instructions_util.split_into_sentences(value)
        if len(sentences) < self._n:
            return False
        words = instructions_util.nltk.word_tokenize(sentences[self._n - 1])
        if len(words) < self._m:
            return False
        return words[self._m - 1] == self._keyword


