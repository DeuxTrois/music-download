#!/usr/bin/env python3
"""
Unified track download script for both Beatport and Spotify sources.
"""

import argparse
from youtube_to_mp3 import download_youtube_to_mp3
from utils import load_tracks

def main():
    parser = argparse.ArgumentParser(description='Download tracks from Beatport or Spotify sources')
    parser.add_argument('source', choices=['beatport', 'spotify'], 
                       help='Source of tracks to download')
    
    args = parser.parse_args()
    
    print(f"Loading {args.source} tracks...")
    youtube_urls = load_tracks(args.source)
    
    print(f"Starting download of {len(youtube_urls)} tracks from {args.source}...")
    download_youtube_to_mp3(youtube_urls)

if __name__ == "__main__":
    main()