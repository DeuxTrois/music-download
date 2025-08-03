#!/usr/bin/env python3
"""
Shared utilities for the music download pipeline.
Centralizes common functionality to reduce code duplication.
"""

import json
import csv
import subprocess
import time
import re
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path

@dataclass
class Track:
    """Track data structure used throughout the pipeline"""
    title: str
    artist: str
    duration: str
    source: str = None
    url: str = None
    track_number: int = None
    youtube_url: str = None
    youtube_title: str = None
    youtube_duration: str = None
    youtube_channel: str = None
    duration_match: bool = False
    duration_difference: float = None
    search_query: str = None

class Config:
    """Centralized configuration for file paths"""
    DATA_DIR = Path("data")
    OUTPUT_DIR = Path("output")
    
    # Input files
    TRACKLIST_TXT = DATA_DIR / "tracklist.txt"
    SPOTIFY_CSV = DATA_DIR / "spotify_track.csv"
    
    # Generated files
    EXTRACTED_TRACKS_JSON = DATA_DIR / "extracted_tracks.json"
    TRACKS_WITH_YOUTUBE_JSON = DATA_DIR / "tracks_with_youtube.json"
    SPOTIFY_TRACKS_WITH_YOUTUBE_JSON = DATA_DIR / "spotify_tracks_with_youtube.json"
    
    @classmethod
    def ensure_dirs(cls):
        """Create directories if they don't exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.OUTPUT_DIR.mkdir(exist_ok=True)

class FileManager:
    """Handles all file I/O operations"""
    
    @staticmethod
    def load_tracks_json(file_path: Path) -> List[Track]:
        """Load tracks from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return [Track(**track) for track in data]
    
    @staticmethod
    def save_tracks_json(tracks: List[Track], file_path: Path):
        """Save tracks to JSON file"""
        data = [asdict(track) for track in tracks]
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_spotify_csv(file_path: Path) -> List[Track]:
        """Load tracks from Spotify CSV file"""
        tracks = []
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            lines = csvfile.readlines()
            
            for i, line in enumerate(lines[1:], 1):
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    title = parts[0]
                    duration = parts[-1]
                    artist = ','.join(parts[1:-1]).strip()
                    
                    track = Track(
                        track_number=i,
                        title=title,
                        artist=artist,
                        duration=duration,
                        source='spotify'
                    )
                    tracks.append(track)
        return tracks
    
    @staticmethod
    def get_youtube_urls_from_tracks(tracks: List[Track]) -> List[str]:
        """Extract YouTube URLs from tracks that have them"""
        return [track.youtube_url for track in tracks if track.youtube_url]

class YouTubeSearcher:
    """Handles YouTube search functionality"""
    
    @staticmethod
    def duration_to_seconds(duration_str: str) -> int:
        """Convert duration string (M:SS or MM:SS) to total seconds"""
        try:
            if ':' not in duration_str:
                return 0
            
            parts = duration_str.split(':')
            if len(parts) == 2:
                minutes, seconds = parts
                return int(minutes) * 60 + int(seconds)
            elif len(parts) == 3:
                hours, minutes, seconds = parts
                return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
            else:
                return 0
        except (ValueError, AttributeError):
            return 0
    
    @staticmethod
    def search_youtube_track(title: str, artist: str, target_duration: str) -> Optional[Dict[str, Any]]:
        """Search for a track on YouTube and verify by duration using yt-dlp"""
        try:
            search_query = title
            print(f"Searching YouTube for: '{search_query}'")
            
            search_url = f"ytsearch5:{search_query}"
            
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                '--quiet',
                search_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"  Error running yt-dlp: {result.stderr}")
                return None
            
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        video_data = json.loads(line)
                        videos.append(video_data)
                    except json.JSONDecodeError:
                        continue
            
            if not videos:
                return None
            
            target_seconds = YouTubeSearcher.duration_to_seconds(target_duration)
            
            for video in videos:
                video_duration = video.get('duration', 0)
                video_title = video.get('title', 'Unknown')
                video_url = video.get('webpage_url', '')
                video_channel = video.get('uploader', 'Unknown')
                
                if video_duration:
                    minutes = video_duration // 60
                    seconds = video_duration % 60
                    duration_str = f"{minutes}:{seconds:02d}"
                else:
                    duration_str = "Unknown"
                
                duration_diff = abs(video_duration - target_seconds)
                
                print(f"  Found: '{video_title}' - Duration: {duration_str} ({video_duration}s) - Diff: {duration_diff}s")
                
                if duration_diff <= 5:
                    return {
                        'youtube_url': video_url,
                        'youtube_title': video_title,
                        'youtube_duration': duration_str,
                        'youtube_channel': video_channel,
                        'duration_match': True,
                        'duration_difference': duration_diff,
                        'search_query': search_query
                    }
            
            if videos:
                first_video = videos[0]
                video_duration = first_video.get('duration', 0)
                video_title = first_video.get('title', 'Unknown')
                video_url = first_video.get('webpage_url', '')
                video_channel = first_video.get('uploader', 'Unknown')
                
                if video_duration:
                    minutes = video_duration // 60
                    seconds = video_duration % 60
                    duration_str = f"{minutes}:{seconds:02d}"
                else:
                    duration_str = "Unknown"
                
                duration_diff = abs(video_duration - target_seconds)
                
                return {
                    'youtube_url': video_url,
                    'youtube_title': video_title,
                    'youtube_duration': duration_str,
                    'youtube_channel': video_channel,
                    'duration_match': False,
                    'duration_difference': duration_diff,
                    'search_query': search_query
                }
            
            return None
            
        except Exception as e:
            print(f"Error searching for '{search_query}': {str(e)}")
            return None
    
    @staticmethod
    def search_and_update_track(track: Track) -> Track:
        """Search YouTube for a track and update it with results"""
        print(f"Title: {track.title}")
        print(f"Artist: {track.artist}")
        print(f"Duration: {track.duration}")
        
        youtube_result = YouTubeSearcher.search_youtube_track(
            track.title, 
            track.artist, 
            track.duration
        )
        
        if youtube_result:
            track.youtube_url = youtube_result['youtube_url']
            track.youtube_title = youtube_result['youtube_title']
            track.youtube_duration = youtube_result['youtube_duration']
            track.youtube_channel = youtube_result['youtube_channel']
            track.duration_match = youtube_result['duration_match']
            track.duration_difference = youtube_result['duration_difference']
            track.search_query = youtube_result['search_query']
            
            if youtube_result['duration_match']:
                print(f"✓ Found matching track: {youtube_result['youtube_url']}")
            else:
                print(f"⚠ Found track but duration mismatch: {youtube_result['youtube_url']}")
        else:
            track.youtube_url = None
            track.youtube_title = None
            track.youtube_duration = None
            track.youtube_channel = None
            track.duration_match = False
            track.duration_difference = None
            track.search_query = track.title
            print("✗ No results found")
        
        time.sleep(1)
        return track

def load_tracks(source: str) -> List[str]:
    """Unified function to load YouTube URLs from either source"""
    Config.ensure_dirs()
    
    if source == 'beatport':
        tracks = FileManager.load_tracks_json(Config.TRACKS_WITH_YOUTUBE_JSON)
        print(f"Found {len(FileManager.get_youtube_urls_from_tracks(tracks))} Beatport tracks with YouTube URLs out of {len(tracks)} total tracks")
    elif source == 'spotify':
        tracks = FileManager.load_tracks_json(Config.SPOTIFY_TRACKS_WITH_YOUTUBE_JSON)
        print(f"Found {len(FileManager.get_youtube_urls_from_tracks(tracks))} Spotify tracks with YouTube URLs out of {len(tracks)} total tracks")
    else:
        raise ValueError(f"Unknown source: {source}. Use 'beatport' or 'spotify'")
    
    return FileManager.get_youtube_urls_from_tracks(tracks)