import re

class Tokenizer:
    def tokenize(self, text):
        # Split text into words and punctuation using regex
        return re.findall(r'\b\w+\b|[.,!?;]', text)