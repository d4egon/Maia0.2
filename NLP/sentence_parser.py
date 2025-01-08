#NLP/sentence_parser.py
import logging
import re
from typing import List, Dict

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SentenceParser:
    def parse(self, tokens: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """
        Parse a list of tokenized dictionaries to identify grammatical components.
        Each token is expected to be a dictionary with a 'type' and 'value' key.

        :param tokens: List of dictionaries, where each dictionary represents a token with 'type' and 'value'.
        :return: A dictionary containing parsed grammatical components.
        """
        parsed = {
            "subject": [],
            "verb": [],
            "object": [],
            "modifiers": [],
            "phrases": {
                "noun_phrases": [],
                "verb_phrases": [],
                "prepositional_phrases": []
            }
        }

        try:
            if not isinstance(tokens, list) or not tokens:
                raise ValueError("Input must be a non-empty list of token dictionaries.")

            # Helper function for phrase building
            def add_to_phrase(phrase_type, phrase_component):
                if not parsed["phrases"][phrase_type]:
                    parsed["phrases"][phrase_type].append([phrase_component])
                else:
                    parsed["phrases"][phrase_type][-1].append(phrase_component)

            for token_dict in tokens:
                if not isinstance(token_dict, dict) or "type" not in token_dict or "value" not in token_dict:
                    logger.warning(f"[PARSE WARNING] Skipping invalid token: {token_dict}")
                    continue

                token_type = token_dict["type"]
                token = token_dict["value"].lower()  # Convert to lowercase for easier matching

                # Identify grammatical components
                if token_type == "word":
                    if token in {"he", "she", "it", "they", "we", "you", "i"}:
                        parsed["subject"].append(token)
                        add_to_phrase("noun_phrases", token)
                    elif token.lower() in {"is", "are", "was", "were", "be", "has", "have", "do", "does"}:
                        parsed["verb"].append(token)
                        add_to_phrase("verb_phrases", token)
                    elif token.endswith("ly") or token in {"very", "extremely"}:
                        parsed["modifiers"].append(token)
                    elif re.match(r'\b[a-z]+\b', token) and not token.endswith("ly"):  # Simple noun detection
                        if parsed["subject"] and not parsed["object"]:
                            parsed["object"].append(token)
                        add_to_phrase("noun_phrases", token)  # Adds to noun phrase
                    elif token in {"in", "on", "at", "by", "with"}:  # Simple preposition detection
                        if parsed["phrases"]["prepositional_phrases"] and parsed["phrases"]["prepositional_phrases"][-1][-1] != token:
                            parsed["phrases"]["prepositional_phrases"].append([token])
                        else:
                            add_to_phrase("prepositional_phrases", token)
                
                # Handle punctuation or other token types if necessary

            # Combine phrases into strings
            for phrase_type in parsed["phrases"]:
                parsed["phrases"][phrase_type] = [" ".join(phrase) for phrase in parsed["phrases"][phrase_type]]

            logger.info(f"[PARSE] Tokens parsed into structure: {parsed}")
            return parsed
        except ValueError as ve:
            logger.error(f"[PARSE ERROR] {ve}")
            raise
        except Exception as e:
            logger.error(f"[PARSE ERROR] Unexpected error during parsing: {e}", exc_info=True)
            raise