import re
import logging
from typing import List

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Tokenizer:
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize the input text into words and certain punctuation marks.

        This method splits the text into tokens where:
        - Words are considered as sequences of word characters (\w+).
        - Specific punctuation marks like '.', ',', '!', '?', and ';' are treated as individual tokens.

        :param text: The text string to be tokenized.
        :return: A list of tokens.

        :raises ValueError: If the input text is not a string or is empty.
        """
        try:
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Input must be a non-empty string.")

            # Use regex to find words and specific punctuation marks
            tokens = re.findall(r'\b\w+\b|[.,!?;]', text)
            logger.info(f"[TOKENIZATION] Text '{text[:50]}{'...' if len(text) > 50 else ''}' tokenized into {len(tokens)} tokens.")
            return tokens
        except ValueError as ve:
            logger.error(f"[TOKENIZATION ERROR] {ve}")
            raise
        except Exception as e:
            logger.error(f"[TOKENIZATION ERROR] Unexpected error: {e}", exc_info=True)
            raise