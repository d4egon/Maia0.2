# File: /core/sentence_parser.py

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure correct download if missing, but with better control
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    logger.warning("NLTK punkt tokenizer not found. Attempting to download...")
    try:
        nltk.download("punkt")
    except Exception as e:
        logger.error(f"Failed to download NLTK punkt tokenizer: {e}")
        raise

class SentenceParser:
    def __init__(self, download_data=True):
        """
        Initialize SentenceParser with an option to automatically download NLTK data.

        :param download_data: If True, will attempt to download NLTK data if not found.
        """
        if download_data:
            self._ensure_nltk_data()

    def _ensure_nltk_data(self):
        """Ensure that necessary NLTK data is available, prompting for download if needed."""
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            try:
                nltk.download("punkt")
                logger.info("Successfully downloaded NLTK punkt tokenizer.")
            except Exception as e:
                logger.error(f"Failed to download NLTK punkt tokenizer: {e}")
                raise

    def parse_sentence(self, input_text, include_pos=False):
        """
        Parse input text into words and sentences, optionally including POS tagging.

        :param input_text: Text to parse
        :param include_pos: If True, includes Part of Speech tagging
        :return: Dictionary with tokenized words, sentences, and optionally POS tags
        """
        try:
            result = {
                "tokens": word_tokenize(input_text),
                "sentences": sent_tokenize(input_text),
            }
            
            if include_pos:
                # Here we would need to download and check for 'averaged_perceptron_tagger'
                try:
                    nltk.data.find('taggers/averaged_perceptron_tagger')
                except LookupError:
                    nltk.download('averaged_perceptron_tagger')
                
                pos_tags = nltk.pos_tag(result["tokens"])
                result["pos_tags"] = pos_tags

            return result
        except Exception as e:
            logger.error(f"Error parsing sentence: {e}")
            raise

# Usage example:
# parser = SentenceParser()
# parsed = parser.parse_sentence("Hello, how are you today?", include_pos=True)
# print(parsed)