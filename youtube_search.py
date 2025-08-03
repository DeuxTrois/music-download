#!/usr/bin/env python3

import json
import time
import re
import subprocess
import urllib.parse

def duration_to_seconds(duration_str):
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

def youtube_duration_to_seconds(youtube_duration):
    """Convert YouTube duration (e.g., '5:52', '1:23:45') to seconds"""
    try:
        if not youtube_duration:
            return 0
        
        # Remove any non-digit, non-colon characters
        clean_duration = re.sub(r'[^\d:]', '', youtube_duration)
        
        parts = clean_duration.split(':')
        if len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + int(seconds)
        elif len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        else:
            return 0
    except (ValueError, IndexError):
        return 0

def search_youtube_track(title, artist, target_duration):
    """Search for a track on YouTube and verify by duration using yt-dlp"""
    try:
        # Create search query - using title only for better hit rate
        search_query = title
        
        print(f"Searching YouTube for: '{search_query}'")
        
        # Use yt-dlp to search YouTube
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
        
        # Parse results
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
        
        target_seconds = duration_to_seconds(target_duration)
        
        for video in videos:
            video_duration = video.get('duration', 0)
            video_title = video.get('title', 'Unknown')
            video_url = video.get('webpage_url', '')
            video_channel = video.get('uploader', 'Unknown')
            
            # Convert duration to readable format
            if video_duration:
                minutes = video_duration // 60
                seconds = video_duration % 60
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Unknown"
            
            # Check if duration is within 5 seconds
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
        
        # If no duration match found, return the first result with a flag
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

def main():
    # Load extracted tracks
    with open('extracted_tracks.json', 'r', encoding='utf-8') as file:
        tracks = json.load(file)
    
    print(f"Processing {len(tracks)} tracks...")
    
    enhanced_tracks = []
    successful_matches = 0
    
    for i, track in enumerate(tracks, 1):
        print(f"\n--- Track {i}/{len(tracks)} ---")
        print(f"Title: {track['title']}")
        print(f"Artist: {track['artist']}")
        print(f"Duration: {track['duration']}")
        
        youtube_result = search_youtube_track(
            track['title'], 
            track['artist'], 
            track['duration']
        )
        
        if youtube_result:
            track.update(youtube_result)
            if youtube_result['duration_match']:
                successful_matches += 1
                print(f"✓ Found matching track: {youtube_result['youtube_url']}")
            else:
                print(f"⚠ Found track but duration mismatch: {youtube_result['youtube_url']}")
        else:
            track.update({
                'youtube_url': None,
                'youtube_title': None,
                'youtube_duration': None,
                'youtube_channel': None,
                'duration_match': False,
                'duration_difference': None,
                'search_query': f"{track['artist']} {track['title']}"
            })
            print("✗ No results found")
        
        enhanced_tracks.append(track)
        
        # Be respectful to YouTube API
        time.sleep(1)
    
    # Save results
    with open('tracks_with_youtube.json', 'w', encoding='utf-8') as file:
        json.dump(enhanced_tracks, file, indent=2, ensure_ascii=False)
    
    # Save CSV version
    import csv
    with open('tracks_with_youtube.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'track_number', 'title', 'artist', 'duration', 'url',
            'youtube_url', 'youtube_title', 'youtube_duration', 'youtube_channel',
            'duration_match', 'duration_difference', 'search_query'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for track in enhanced_tracks:
            writer.writerow(track)
    
    print(f"\n{'='*60}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Total tracks processed: {len(tracks)}")
    print(f"Successful duration matches: {successful_matches}")
    print(f"Match rate: {successful_matches/len(tracks)*100:.1f}%")
    print(f"\nResults saved to:")
    print(f"- tracks_with_youtube.json")
    print(f"- tracks_with_youtube.csv")

if __name__ == "__main__":
    main()