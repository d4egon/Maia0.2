import re
import logging
from typing import List, Dict

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Tokenizer:
    # Define a set of keywords to be tagged during tokenization
    KEYWORDS = {"grace", "faith", "sin", "redemption", "virtue", "justice", "mercy", "truth", "love", "evil"}

    def tokenize(self, text: str) -> List[Dict[str, str]]:
        """
        Tokenize the input text into words, numbers, punctuation marks, and specific keywords.

        Tokens are categorized as:
        - word: Regular words
        - punctuation: Specific punctuation marks
        - number: Numerical values
        - keyword: Predefined theological or ethical terms

        :param text: The text string to be tokenized.
        :return: A list of dictionaries where each token includes the 'type' and 'value'.

        :raises ValueError: If the input text is not a string or is empty.
        """
        try:
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Input must be a non-empty string.")

            # Use regex to find tokens
            token_patterns = r'\b\w+\b|[.,!?;]|[\d]+(?:\.\d+)?|\b(?:' + '|'.join(self.KEYWORDS) + r')\b'
            raw_tokens = re.findall(token_patterns, text)

            # Categorize tokens
            categorized_tokens = []
            for token in raw_tokens:
                if token.lower() in self.KEYWORDS:
                    token_type = "keyword"
                elif token.isdigit() or re.match(r'^\d+(?:\.\d+)?$', token):
                    token_type = "number"
                elif re.match(r'[.,!?;]', token):
                    token_type = "punctuation"
                else:
                    token_type = "word"

                categorized_tokens.append({"type": token_type, "value": token})

            logger.info(f"[TOKENIZATION] Text '{text[:50]}{'...' if len(text) > 50 else ''}' tokenized into {len(categorized_tokens)} categorized tokens.")
            return categorized_tokens
        except ValueError as ve:
            logger.error(f"[TOKENIZATION ERROR] {ve}")
            raise
        except Exception as e:
            logger.error(f"[TOKENIZATION ERROR] Unexpected error: {e}", exc_info=True)
            raise
