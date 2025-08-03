#!/usr/bin/env python3

import csv
import json
import time
from youtube_search import search_youtube_track

def main():
    # Load Spotify tracks from CSV - handle comma-separated artists properly
    spotify_tracks = []
    with open('spotify_track.csv', 'r', encoding='utf-8') as csvfile:
        # Read the raw lines to handle CSV parsing issues with commas in artist names
        lines = csvfile.readlines()
        
        # Skip header
        for i, line in enumerate(lines[1:], 1):
            # Split carefully - last comma-separated value should be duration
            parts = line.strip().split(',')
            if len(parts) >= 3:
                # Title is first part
                title = parts[0]
                # Duration is last part
                duration = parts[-1]
                # Artist is everything in between, joined back
                artist = ','.join(parts[1:-1]).strip()
                
                track = {
                    'track_number': i,
                    'title': title,
                    'artist': artist,
                    'duration': duration,
                    'source': 'spotify'
                }
                spotify_tracks.append(track)
    
    print(f"Processing {len(spotify_tracks)} Spotify tracks...")
    
    enhanced_tracks = []
    successful_matches = 0
    
    for i, track in enumerate(spotify_tracks, 1):
        print(f"\n--- Spotify Track {i}/{len(spotify_tracks)} ---")
        print(f"Title: {track['title']}")
        print(f"Artist: {track['artist']}")
        print(f"Duration: {track['duration']}")
        
        # Use the same YouTube search function (title-only search)
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
                'search_query': track['title']
            })
            print("✗ No results found")
        
        enhanced_tracks.append(track)
        
        # Be respectful to YouTube API
        time.sleep(1)
    
    # Save results
    with open('spotify_tracks_with_youtube.json', 'w', encoding='utf-8') as file:
        json.dump(enhanced_tracks, file, indent=2, ensure_ascii=False)
    
    # Save CSV version
    with open('spotify_tracks_with_youtube.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'track_number', 'title', 'artist', 'duration', 'source',
            'youtube_url', 'youtube_title', 'youtube_duration', 'youtube_channel',
            'duration_match', 'duration_difference', 'search_query'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for track in enhanced_tracks:
            writer.writerow(track)
    
    print(f"\n{'='*60}")
    print(f"SPOTIFY RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Total Spotify tracks processed: {len(spotify_tracks)}")
    print(f"Successful duration matches: {successful_matches}")
    print(f"Match rate: {successful_matches/len(spotify_tracks)*100:.1f}%")
    print(f"\nResults saved to:")
    print(f"- spotify_tracks_with_youtube.json")
    print(f"- spotify_tracks_with_youtube.csv")

if __name__ == "__main__":
    main()