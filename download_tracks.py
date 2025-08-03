#!/usr/bin/env python3
"""
Unified track download script for both Beatport and Spotify sources.
"""

import json
import argparse
from youtube_to_mp3 import download_youtube_to_mp3

def load_beatport_tracks():
    """Load YouTube URLs from tracks_with_youtube.json (Beatport source)"""
    with open('data/tracks_with_youtube.json', 'r', encoding='utf-8') as file:
        tracks = json.load(file)
    
    youtube_urls = []
    for track in tracks:
        youtube_url = track.get('youtube_url')
        if youtube_url:
            youtube_urls.append(youtube_url)
    
    print(f"Found {len(youtube_urls)} Beatport tracks with YouTube URLs out of {len(tracks)} total tracks")
    return youtube_urls

def load_spotify_tracks():
    """Load YouTube URLs from spotify_tracks_with_youtube.json (Spotify source)"""
    with open('data/spotify_tracks_with_youtube.json', 'r', encoding='utf-8') as file:
        tracks = json.load(file)
    
    youtube_urls = []
    for track in tracks:
        youtube_url = track.get('youtube_url')
        if youtube_url:
            youtube_urls.append(youtube_url)
    
    print(f"Found {len(youtube_urls)} Spotify tracks with YouTube URLs out of {len(tracks)} total tracks")
    return youtube_urls

def main():
    parser = argparse.ArgumentParser(description='Download tracks from Beatport or Spotify sources')
    parser.add_argument('source', choices=['beatport', 'spotify'], 
                       help='Source of tracks to download')
    
    args = parser.parse_args()
    
    if args.source == 'beatport':
        print("Loading Beatport tracks...")
        youtube_urls = load_beatport_tracks()
    elif args.source == 'spotify':
        print("Loading Spotify tracks...")
        youtube_urls = load_spotify_tracks()
    
    print(f"Starting download of {len(youtube_urls)} tracks from {args.source}...")
    download_youtube_to_mp3(youtube_urls)

if __name__ == "__main__":
    main()