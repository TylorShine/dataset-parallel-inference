class SentenceHyphenChecker(Instruction):
    """All sentences must be connected using hyphens, with no spaces between them."""

    def build_description(self):
        """Build the instruction description."""
        self._description_pattern = "All sentences must be connected using hyphens, with no spaces between them."
        return self._description_pattern

    def get_instruction_args(self):
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks if all sentences are connected using hyphens, with no spaces between them."""
        sentences_gold = re.sub("-", " ", value)
        sentences_gold = instructions_util.split_into_sentences(sentences_gold)
        sentences = value.split("-")
        # Check if there are any spaces between sentences
        for sentence, gold in zip(sentences, sentences_gold):
            if sentence.strip() != sentence or sentence != gold:
                return False
        return True


