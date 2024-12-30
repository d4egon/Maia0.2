import logging
from typing import List, Dict

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SentenceParser:
    def parse(self, tokens: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """
        Parse a list of tokenized dictionaries to identify grammatical components.
        Each token is expected to be a dictionary with a 'value' key containing the word.
        """
        parsed = {
            "subject": [],
            "verb": [],
            "object": [],
            "modifiers": [],
            "phrases": {"noun_phrases": [], "verb_phrases": [], "prepositional_phrases": []}
        }

        try:
            if not isinstance(tokens, list) or not tokens:
                raise ValueError("Input must be a non-empty list of token dictionaries.")

            for token_dict in tokens:
                if not isinstance(token_dict, dict) or "value" not in token_dict:
                    logger.warning(f"[PARSE WARNING] Skipping invalid token: {token_dict}")
                    continue
                
                token = token_dict["value"]

                # Identify grammatical components
                if token.lower() in {"he", "she", "it", "they", "we", "you", "i"}:
                    parsed["subject"].append(token)
                elif token.lower() in {"is", "are", "was", "were", "be", "has", "have", "do", "does"}:
                    parsed["verb"].append(token)
                elif token.lower().endswith("ly") or token.lower() in {"very", "extremely"}:
                    parsed["modifiers"].append(token)

                # Build phrases
                if token.lower() in {"cat", "dog", "house"}:
                    parsed["phrases"]["noun_phrases"].append(token)

            logger.info(f"[PARSE] Tokens parsed into structure: {parsed}")
            return parsed
        except ValueError as ve:
            logger.error(f"[PARSE ERROR] {ve}")
            raise
        except Exception as e:
            logger.error(f"[PARSE ERROR] Unexpected error during parsing: {e}", exc_info=True)
            raise
