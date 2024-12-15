# Filename: google_image_downloader.py

from google_images_download import google_images_download
from PIL import Image, ImageFilter
import os

# Initialize the downloader
response = google_images_download.googleimagesdownload()

# Resize downloaded images to 48x48 and filter out images with excessive noise or text
def resize_and_filter_images(directory):
    """
    Resizes images to 48x48 and applies a basic heuristic to filter out images with excessive text or noise.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".jpg", ".jpeg", ".png")):
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        # Convert to grayscale for simpler analysis
                        img_gray = img.convert("L")

                        # Apply an edge-detection filter to identify text-heavy images
                        edges = img_gray.filter(ImageFilter.FIND_EDGES)
                        edge_data = edges.getdata()
                        high_edges = sum(1 for pixel in edge_data if pixel > 128)

                        # If more than 20% of the image is edges, consider it "text-heavy"
                        total_pixels = img.size[0] * img.size[1]
                        if high_edges / total_pixels > 0.2:
                            print(f"Filtered out (too much text/noise): {file_path}")
                            os.remove(file_path)
                            continue

                        # Resize and overwrite the image
                        img = img.resize((48, 48))
                        img.save(file_path)
                        print(f"Resized: {file_path}")
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")

# Define download attributes
def download_images():
    """
    Downloads images from Google Images and processes them by resizing and filtering.
    """
    queries = {
        "joy": "people smiling, happiness, joyful moments -text",
        "sadness": "people crying, sadness, grief -text",
        "love": "romantic couple, family love, affection -text",
        "frustration": "angry faces, frustration, annoyed expressions -text"
    }

    for emotion, keywords in queries.items():
        arguments = {
            "keywords": keywords,
            "limit": 100,  # Download up to 100 images per query
            "output_directory": "dataset/images",
            "image_directory": emotion,
            "format": "jpg",
            "silent_mode": True,
            "print_urls": False,
            "size": "medium",  # Avoid excessively large files
            "aspect_ratio": "square",  # Prefer square images for consistent resizing
        }
        try:
            print(f"Downloading images for {emotion}...")
            paths = response.download(arguments)
            print(f"Completed downloading images for {emotion}: {paths}")

            # Resize and filter images in the current directory
            emotion_dir = os.path.join("dataset/images", emotion)
            resize_and_filter_images(emotion_dir)
        except Exception as e:
            print(f"Error downloading images for {emotion}: {e}")

if __name__ == "__main__":
    download_images()