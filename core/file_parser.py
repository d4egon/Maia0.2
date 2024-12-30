import logging
import mimetypes
import os
from PyPDF2 import PdfReader  # type: ignore
import pytesseract  # type: ignore
import speech_recognition as sr  # type: ignore
from docx import Document  # type: ignore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class FileParser:
    def parse(self, filepath, language="eng"):
        """
        Parse a file based on its MIME type.
        Supports text, PDF, images, audio, and Microsoft Word files.
        
        :param filepath: Path to the file.
        :param language: Language for OCR and speech recognition (default: "eng").
        :return: Parsed content.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        mime_type, _ = mimetypes.guess_type(filepath)
        logger.info(f"Parsing file: {filepath}, MIME type: {mime_type}")

        if mime_type.startswith("text"):
            return self.parse_text(filepath)
        elif mime_type == "application/pdf":
            return self.parse_pdf(filepath, language)
        elif mime_type.startswith("image"):
            return self.parse_image(filepath, language)
        elif mime_type.startswith("audio"):
            return self.parse_audio(filepath, language)
        elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return self.parse_docx(filepath)
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

    def parse_pdf(self, filepath, language="eng"):
        """
        Extract text from PDF files. Falls back to OCR for scanned PDFs.
        
        :param filepath: Path to the PDF file.
        :param language: Language for OCR if needed (default: "eng").
        :return: Extracted text.
        """
        try:
            reader = PdfReader(filepath)
            content = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
            if not content.strip():
                logger.warning("Text extraction failed. Attempting OCR...")
                return self.parse_image(filepath, language)
            return content
        except Exception as e:
            logger.error(f"Failed to parse PDF: {e}")
            raise ValueError("PDF parsing failed.")

    def parse_image(self, filepath, language="eng"):
        """
        Extract text from images using OCR.
        
        :param filepath: Path to the image file.
        :param language: Language for OCR (default: "eng").
        :return: Extracted text.
        """
        try:
            content = pytesseract.image_to_string(filepath, lang=language)
            return content
        except Exception as e:
            logger.error(f"Failed to parse image: {e}")
            raise

    def parse_audio(self, filepath, language="en-US"):
        """
        Transcribe audio files into text.
        
        :param filepath: Path to the audio file.
        :param language: Language for transcription (default: "en-US").
        :return: Transcribed text.
        """
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(filepath) as source:
                audio = recognizer.record(source)
            content = recognizer.recognize_google(audio, language=language)
            return content
        except sr.UnknownValueError:
            return "Audio transcription failed."
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            raise

    def parse_docx(self, filepath):
        """
        Parse Microsoft Word (.docx) files.
        
        :param filepath: Path to the .docx file.
        :return: Extracted text.
        """
        try:
            doc = Document(filepath)
            content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            if not content.strip():
                raise ValueError("DOCX content extraction failed or is empty.")
            return content
        except Exception as e:
            logger.error(f"Failed to parse DOCX: {e}")
            raise ValueError("DOCX parsing failed.")

    def parse_directory(self, dirpath, language="eng"):
        """
        Parse all files in a directory.
        
        :param dirpath: Path to the directory.
        :param language: Language for OCR and transcription (default: "eng").
        :return: Dictionary of filenames and their parsed content or errors.
        """
        results = {}
        for root, _, files in os.walk(dirpath):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    results[file] = self.parse(filepath, language)
                except Exception as e:
                    results[file] = f"Error: {e}"
        return results
