import logging
import mimetypes
import os
from PyPDF2 import PdfReader
import pytesseract
import speech_recognition as sr

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class FileParser:
    def parse(self, filepath):
        """
        Parse a file based on its MIME type.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        mime_type, _ = mimetypes.guess_type(filepath)
        logger.info(f"Parsing file: {filepath}, MIME type: {mime_type}")

        if mime_type.startswith("text"):
            return self.parse_text(filepath)
        elif mime_type == "application/pdf":
            return self.parse_pdf(filepath)
        elif mime_type.startswith("image"):
            return self.parse_image(filepath)
        elif mime_type.startswith("audio"):
            return self.parse_audio(filepath)
        else:
            raise ValueError(f"Unsupported file type: {mime_type}")

    def parse_text(self, filepath):
        """
        Parse plain text files.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
            return content
        except Exception as e:
            logger.error(f"Failed to parse text file: {e}")
            raise

    def parse_pdf(self, filepath):
        """
        Extract text from PDF files.
        """
        try:
            reader = PdfReader(filepath)
            content = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
            if not content.strip():
                raise ValueError("PDF content extraction failed or is empty.")
            return content
        except Exception as e:
            logger.error(f"Failed to parse PDF: {e}")
            raise ValueError("PDF parsing failed.")

    def parse_image(self, filepath):
        """
        Extract text from images using OCR.
        """
        try:
            content = pytesseract.image_to_string(filepath)
            return content
        except Exception as e:
            logger.error(f"Failed to parse image: {e}")
            raise

    def parse_audio(self, filepath):
        """
        Transcribe audio files into text.
        """
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(filepath) as source:
                audio = recognizer.record(source)
            content = recognizer.recognize_google(audio)
            return content
        except sr.UnknownValueError:
            return "Audio transcription failed."
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            raise
