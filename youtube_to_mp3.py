import yt_dlp
import os
from typing import List
from utils import Config

def download_youtube_to_mp3(urls: List[str], output_dir: str = None):
    """
    Download YouTube videos as MP3 files from a list of URLs.
    
    Args:
        urls: List of YouTube URLs to download
        output_dir: Directory to save the MP3 files (default: Config.OUTPUT_DIR)
    """
    if output_dir is None:
        output_dir = str(Config.OUTPUT_DIR)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # yt-dlp options for extracting MP3
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    successful_downloads = []
    failed_downloads = []
    
    for url in urls:
        try:
            print(f"Downloading: {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            successful_downloads.append(url)
            print(f"✓ Successfully downloaded: {url}")
        except Exception as e:
            failed_downloads.append((url, str(e)))
            print(f"✗ Failed to download {url}: {e}")
    
    # Summary
    print(f"\n--- Download Summary ---")
    print(f"Successful: {len(successful_downloads)}")
    print(f"Failed: {len(failed_downloads)}")
    
    if failed_downloads:
        print("\nFailed downloads:")
        for url, error in failed_downloads:
            print(f"  {url}: {error}")

if __name__ == "__main__":
    # Example usage
    example_urls = [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',  # Example URL
    ]
    
    print("This is the core download function.")
    print("Use 'python download_tracks.py beatport' or 'python download_tracks.py spotify' for batch downloads.")
    print("\nExample usage:")
    print("download_youtube_to_mp3(['https://www.youtube.com/watch?v=...'])")
    
    # Uncomment to test with example URL
    # download_youtube_to_mp3(example_urls)