# sentence_parser.py

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

# Ensure correct download if missing
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")


class SentenceParser:
    def parse_sentence(self, input_text):
        """Parse input text into words and sentences."""
        tokens = word_tokenize(input_text)
        return {
            "tokens": tokens,
            "sentences": sent_tokenize(input_text),
        }