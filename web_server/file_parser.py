import pypandoc
import PyPDF2
import pytesseract
import speech_recognition as sr
import ffmpeg
import os
from PIL import Image

class FileParser:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    # DOCX and Text Parsing
    def parse_docx(self, file_path):
        try:
            text = pypandoc.convert_file(file_path, 'plain', format='docx')
            return text.strip()
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
            return None

    def parse_txt(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error parsing TXT: {e}")
            return None

    # PDF Parsing
    def parse_pdf(self, file_path):
        try:
            text = ""
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return None

    # Image Parsing (OCR)
    def parse_image(self, file_path):
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"Error parsing Image: {e}")
            return None

    # Audio Parsing (Speech Recognition)
    def parse_audio(self, file_path):
        try:
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                return text.strip()
        except Exception as e:
            print(f"Error parsing Audio: {e}")
            return None

    # Video Parsing (Extract Audio)
    def parse_video(self, file_path):
        try:
            audio_file = "temp_audio.wav"
            ffmpeg.input(file_path).output(audio_file, format="wav").run(overwrite_output=True)
            return self.parse_audio(audio_file)
        except Exception as e:
            print(f"Error parsing Video: {e}")
            return None
        finally:
            if os.path.exists(audio_file):
                os.remove(audio_file)