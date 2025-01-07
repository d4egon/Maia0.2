# File: /core/sentence_parser.py

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
import logging
from typing import Dict, List, Tuple
from transformers import pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_nltk_data(data_name: str) -> bool:
    """Download NLTK data if not found, with error handling."""
    try:
        nltk.data.find(f"{data_name}")
        return True
    except LookupError:
        try:
            nltk.download(data_name)
            logger.info(f"Successfully downloaded NLTK {data_name}.")
            return True
        except Exception as e:
            logger.error(f"Failed to download NLTK {data_name}: {e}")
            return False

class SentenceParser:
    def __init__(self, download_data: bool = True):
        """
        Initialize SentenceParser with an option to automatically download NLTK and Hugging Face model data.

        :param download_data: If True, will attempt to download necessary NLTK and model data.
        """
        self.download_data = download_data
        if self.download_data:
            self._ensure_nltk_data()
            self.ner_model = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")  # Example NER model
        else:
            self.ner_model = None

    def _ensure_nltk_data(self):
        """Ensure that necessary NLTK data is available, prompting for download if needed."""
        for data in ['tokenizers/punkt', 'taggers/averaged_perceptron_tagger']:
            if not download_nltk_data(data):
                raise RuntimeError(f"NLTK data '{data}' could not be downloaded or found.")

    def parse_sentence(self, input_text: str, include_pos: bool = False, include_ner: bool = False) -> Dict[str, List]:
        """
        Parse input text into words and sentences, optionally including POS tagging and NER.

        :param input_text: Text to parse
        :param include_pos: If True, includes Part of Speech tagging
        :param include_ner: If True, includes Named Entity Recognition
        :return: Dictionary with tokenized words, sentences, and optionally POS tags and NER results
        """
        try:
            result = {
                "tokens": word_tokenize(input_text),
                "sentences": sent_tokenize(input_text),
            }
            
            if include_pos:
                if not self.download_data:
                    logger.warning("POS tagging requested but download_data is False. Attempting to use existing NLTK data.")
                result["pos_tags"] = pos_tag(result["tokens"])

            if include_ner and self.ner_model:
                ner_results = self.ner_model(input_text)
                result["ner"] = ner_results
            elif include_ner:
                logger.warning("NER requested but no model available. Set download_data to True or provide a model.")

            return result
        except Exception as e:
            logger.error(f"Error parsing sentence: {e}", exc_info=True)
            raise

    def parse_sentences(self, input_text: str, include_pos: bool = False, include_ner: bool = False) -> List[Dict]:
        """
        Parse multiple sentences from input text.

        :param input_text: Text containing multiple sentences to parse
        :param include_pos: If True, includes Part of Speech tagging for each sentence
        :param include_ner: If True, includes Named Entity Recognition for each sentence
        :return: List of dictionaries, each containing parsed information for a sentence
        """
        try:
            sentences = sent_tokenize(input_text)
            results = []
            for sentence in sentences:
                parsed = self.parse_sentence(sentence, include_pos, include_ner)
                results.append(parsed)
            return results
        except Exception as e:
            logger.error(f"Error parsing multiple sentences: {e}", exc_info=True)
            raise

# Usage example:
# parser = SentenceParser(download_data=True)
# parsed = parser.parse_sentence("Hello, how are you today? Elon Musk is the CEO of Tesla.", include_pos=True, include_ner=True)
# print(parsed)
# 
# or for multiple sentences
# multi_parsed = parser.parse_sentences("Hello, how are you today? Elon Musk is the CEO of Tesla.", include_pos=True, include_ner=True)
# print(multi_parsed)