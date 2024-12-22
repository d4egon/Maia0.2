import logging
from typing import List, Dict

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SentenceParser:
    def parse(self, tokens: List[str]) -> Dict[str, str]:
        """
        Parse a list of tokens to extract subject, action, and object based on simple rules.

        This parser specifically looks for sentences where 'you' is the subject and 'are' is 
        the verb, then assumes the last token to be the object. This is a very basic structure 
        and only works for simple declarative sentences.

        :param tokens: A list of tokenized words from the sentence.
        :return: A dictionary with 'subject', 'action', and 'object' keys, where values 
                 could be None if not found or applicable.

        :raises ValueError: If tokens is not a list or if it's empty.
        """
        parsed = {"subject": None, "action": None, "object": None}

        try:
            if not isinstance(tokens, list) or not tokens:
                raise ValueError("Input must be a non-empty list of tokens.")

            if "you" in tokens and "are" in tokens:
                parsed["subject"] = "you"
                parsed["action"] = "are"
                parsed["object"] = tokens[-1]  # Assume last word as object
                logger.info(f"[PARSE] Parsed sentence: {parsed}")

            else:
                logger.info("[PARSE] Sentence structure not recognized for parsing.")
            
            return parsed
        except ValueError as ve:
            logger.error(f"[PARSE ERROR] {ve}")
            raise
        except Exception as e:
            logger.error(f"[PARSE ERROR] Unexpected error during parsing: {e}", exc_info=True)
            raise