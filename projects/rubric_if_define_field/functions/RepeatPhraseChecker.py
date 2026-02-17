class RepeatPhraseChecker(Instruction):
    "Repeat the phrase {phrase} exactly {small_n} times, transforming it slightly each time by replacing only one word in the center of the phrase."

    def build_description(self, phrase=None, small_n=None):
        """Build the instruction description.

        Args:
          phrase: A string representing the phrase to be repeated.
          N: An integer representing the number of times to repeat the phrase.
          word_count: An integer representing the number of words in the phrase.

        Returns:
          A string representing the instruction description.
        """
        if not phrase:
            self._phrase = random.choice(_PHRASES)
        else:
            self._phrase = phrase.strip()
        if not small_n:
            self._small_n = random.randint(2, 3)
        else:
            self._small_n = small_n

        self._description_pattern = "Repeat the phrase {phrase} exactly {small_n} times, transforming it slightly each time by replacing only one word in the center of the phrase."
        return self._description_pattern.format(phrase=self._phrase, small_n=self._small_n)

    def get_instruction_args(self):
        """Returns the keyward args of `build_description`."""
        return {"phrase": self._phrase, "small_n": self._small_n}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["phrase", "small_n"]

    def check_following(self, value):
        """Checks if the response contains the expected number of phrases with the correct modifications."""
        first_word = self._phrase.split()[0]
        last_word = self._phrase.split()[-1]

        len(self._phrase.split()) - 2

        found_phrases = re.findall(rf"{first_word} .*? {last_word}", value)
        if len(found_phrases) != self._small_n:
            return False
        for phrase in found_phrases:
            phrase = phrase.split()
            ref_phrase = self._phrase.split()
            differences = 0
            if len(phrase) != len(ref_phrase):
                return False
            for i in range(len(phrase)):
                try:
                    if phrase[i] != ref_phrase[i]:
                        differences += 1
                        # Early exit if more than one difference found
                        if differences > 1:
                            return False
                except IndexError:
                    return False
        if differences == 1:
            return True


