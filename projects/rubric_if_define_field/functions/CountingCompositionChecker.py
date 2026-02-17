class CountingCompositionChecker(Instruction):
    "Write 3 paragraphs, delimited by the markdown divider: * * *, with exactly {n_sent} sentences each, with exactly {n_words} words in each sentence."

    def build_description(self, n_sent=None, n_words=None):
        """Build the instruction description.

        Args:
        n_sent: An integer representing the number of sentences in each paragraph.
        n_words: An integer representing the number of words in each sentence.

        Returns:
        A string representing the instruction description.
        """
        if not n_sent:
            self._n_sent = random.randint(2, 3)
        else:
            self._n_sent = n_sent
        if not n_words:
            self._n_words = random.randint(2, 3)
        else:
            self._n_words = n_words
        self._description_pattern = "Write 3 paragraphs, delimited by the markdown divider: * * *, with exactly {n_sent} sentences each, with exactly {n_words} words in each sentence."
        return self._description_pattern.format(n_sent=self._n_sent, n_words=self._n_words)

    def get_instruction_args(self):
        return {"n_sent": self._n_sent, "n_words": self._n_words}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["n_sent", "n_words"]

    def check_following(self, value):
        """Checks that the response contains the expected number of paragraphs, sentences, and words.

        Args:
          value: A string representing the response.

        Returns:
          True if the response meets the requirements; otherwise, False.
        """
        paragraphs = re.split(r"\s?\*\*\*\s?", value)
        num_paragraphs = len(paragraphs)

        for index, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                if index == 0 or index == len(paragraphs) - 1:
                    num_paragraphs -= 1
                else:
                    return False

            sentences = instructions_util.split_into_sentences(paragraph)
            num_sentences = len(sentences)

            if num_sentences != self._n_sent:
                return False

            for sentence in sentences:
                words = instructions_util.nltk.word_tokenize(sentence)
                num_words = len(words)

                if num_words != self._n_words:
                    return False

        return num_paragraphs == 3


