import requests
import os
import hashlib
from urllib.parse import urlparse
from datetime import datetime

# Directory to save images
SAVE_DIR = "Fetched_Images"

def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from filename."""
    return "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.')).strip()

def get_filename_from_url(url: str, response: requests.Response) -> str:
    """Extract filename from URL or generate one based on timestamp and MIME type."""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    if not filename or "." not in filename:
        # Try inferring extension from Content-Type header
        content_type = response.headers.get("Content-Type", "")
        ext = ""
        if "image/" in content_type:
            ext = "." + content_type.split("/")[-1].split(";")[0]
        filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"

    return sanitize_filename(filename)

def is_duplicate(filepath: str, content: bytes) -> bool:
    """Check if file already exists by comparing SHA256 hash."""
    if not os.path.exists(filepath):
        return False
    
    with open(filepath, "rb") as f:
        existing_hash = hashlib.sha256(f.read()).hexdigest()
    new_hash = hashlib.sha256(content).hexdigest()
    return existing_hash == new_hash

def fetch_image(url: str):
    try:
        # Create directory if it doesn’t exist
        os.makedirs(SAVE_DIR, exist_ok=True)

        # Fetch image with timeout
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Check important headers
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"✗ Skipped (Not an image): {url}")
            return

        # Extract/generate filename
        filename = get_filename_from_url(url, response)
        filepath = os.path.join(SAVE_DIR, filename)

        # Read content in chunks
        content = response.content

        # Prevent duplicate downloads
        if os.path.exists(filepath) and is_duplicate(filepath, content):
            print(f"✗ Duplicate skipped: {filename}")
            return

        # Save image in binary mode
        with open(filepath, "wb") as f:
            f.write(content)

        print(f"✓ Successfully fetched: {filename}")
        print(f"✓ Image saved to {filepath}")

    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error: {e}")
    except Exception as e:
        print(f"✗ An error occurred: {e}")

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")

    # Accept multiple URLs
    while True:
        url = input("Please enter the image URL (or type 'exit' to quit): ").strip()
        if url.lower() == "exit":
            break
        if url:
            fetch_image(url)

    print("\nConnection strengthened. Community enriched.")

if __name__ == "__main__":
    main()
