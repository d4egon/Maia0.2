import logging
from typing import List, Dict

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SentenceParser:
    def parse(self, tokens: List[str]) -> Dict[str, List[str]]:
        """
        Parse a list of tokens to identify grammatical components like subject, verb, object, and modifiers.

        The parser supports basic dependency analysis and extracts:
        - Subjects
        - Verbs
        - Objects
        - Modifiers (e.g., adjectives, adverbs)
        - Phrases (e.g., noun phrases, verb phrases)

        :param tokens: A list of tokenized words from the sentence.
        :return: A dictionary with components such as 'subject', 'verb', 'object', 'modifiers', and 'phrases'.

        :raises ValueError: If tokens is not a list or if it's empty.
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
                raise ValueError("Input must be a non-empty list of tokens.")

            # Simple rules-based dependency analysis
            for i, token in enumerate(tokens):
                # Identify subjects and verbs (basic rule: subject precedes verb)
                if token.lower() in {"he", "she", "it", "they", "we", "you", "i"}:
                    parsed["subject"].append(token)
                elif token.lower() in {"is", "are", "was", "were", "be", "has", "have", "do", "does"}:
                    parsed["verb"].append(token)
                elif i > 0 and tokens[i - 1].lower() in {"the", "a", "an"}:
                    parsed["object"].append(token)  # Assume articles precede objects

                # Identify modifiers (adjectives or adverbs)
                if token.lower().endswith("ly") or token.lower() in {"very", "extremely"}:
                    parsed["modifiers"].append(token)

                # Build phrases
                if i > 0 and tokens[i - 1].lower() in {"in", "on", "at", "with", "by"}:
                    parsed["phrases"]["prepositional_phrases"].append(f"{tokens[i - 1]} {token}")
                if token.lower() in {"run", "eat", "read"}:
                    parsed["phrases"]["verb_phrases"].append(f"{token} {tokens[i + 1]}" if i + 1 < len(tokens) else token)
                if token.lower() in {"cat", "dog", "house"}:
                    parsed["phrases"]["noun_phrases"].append(f"{tokens[i - 1]} {token}" if i > 0 else token)

            logger.info(f"[PARSE] Tokens parsed into structure: {parsed}")
            return parsed
        except ValueError as ve:
            logger.error(f"[PARSE ERROR] {ve}")
            raise
        except Exception as e:
            logger.error(f"[PARSE ERROR] Unexpected error during parsing: {e}", exc_info=True)
            raise
