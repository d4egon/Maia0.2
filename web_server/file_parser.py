# Filename: /core/file_parser.py

import pytesseract
from PyPDF2 import PdfReader
import speech_recognition as sr
import mimetypes
import os
import logging
from transformers import pipeline
from datetime import datetime

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class FileParser:
    def __init__(self):
        self.ner = pipeline("ner", grouped_entities=True)
        self.keyword_extractor = pipeline("text-classification", model="facebook/bart-large-mnli")

    def parse(self, filepath):
        """
        Parse a file based on its MIME type.
        """
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"File not found: {filepath}")

        mime_type, _ = mimetypes.guess_type(filepath)
        logger.info(f"Parsing file: {filepath}, MIME type: {mime_type or 'Unknown'}")

        try:
            if mime_type and mime_type.startswith("text"):
                return self._analyze_text(self.parse_text(filepath))
            elif mime_type == "application/pdf":
                return self._analyze_text(self.parse_pdf(filepath))
            elif mime_type and mime_type.startswith("image"):
                return self._analyze_text(self.parse_image(filepath))
            elif mime_type and mime_type.startswith("audio"):
                return self._analyze_text(self.parse_audio(filepath))
            else:
                logger.warning(f"Unsupported file type: {mime_type or 'Unknown'}")
                raise ValueError(f"Unsupported file type: {mime_type or 'Unknown'}")
        except Exception as e:
            logger.error(f"Error parsing file {filepath}: {e}")
            raise

    def parse_text(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
            logger.info(f"Parsed text content: {len(content)} characters.")
            return content
        except Exception as e:
            logger.error(f"Failed to parse text file: {e}")
            raise

    def parse_pdf(self, filepath):
        try:
            reader = PdfReader(filepath)
            content = "".join([page.extract_text() for page in reader.pages if page])
            logger.info(f"Parsed PDF content: {len(content)} characters.")
            return content
        except Exception as e:
            logger.error(f"Failed to parse PDF file: {e}")
            raise

    def parse_image(self, filepath):
        try:
            content = pytesseract.image_to_string(filepath)
            logger.info(f"Parsed image content: {len(content)} characters.")
            return content
        except Exception as e:
            logger.error(f"Failed to parse image file: {e}")
            raise

    def parse_audio(self, filepath):
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(filepath) as source:
                audio = recognizer.record(source)
            content = recognizer.recognize_google(audio)
            logger.info(f"Parsed audio content: {len(content)} characters.")
            return content
        except sr.UnknownValueError:
            logger.error("Audio file could not be transcribed (unknown value).")
            return "Transcription failed: Could not understand audio."
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to parse audio file: {e}")
            raise

    def _analyze_text(self, text):
        """
        Extract concepts, keywords, and ethical ideas from parsed content.
        """
        try:
            metadata = {
                "extracted_date": datetime.now().isoformat(),
                "text_length": len(text)
            }

            # Extract Named Entities
            metadata["entities"] = self.ner(text)

            # Extract Keywords
            keywords = self.keyword_extractor(text, candidate_labels=["ethics", "morality", "values", "justice", "faith"])
            metadata["keywords"] = [keyword['label'] for keyword in keywords if keyword['score'] > 0.5]

            logger.info(f"Extracted Metadata: {metadata}")
            return metadata
        except Exception as e:
            logger.error(f"Failed to analyze text: {e}")
            raise