#!/usr/bin/env python3

from utils import Config, FileManager, YouTubeSearcher

def main():
    Config.ensure_dirs()
    
    # Load Spotify tracks from CSV
    spotify_tracks = FileManager.load_spotify_csv(Config.SPOTIFY_CSV)
    
    print(f"Processing {len(spotify_tracks)} Spotify tracks...")
    
    successful_matches = 0
    
    for i, track in enumerate(spotify_tracks, 1):
        print(f"\n--- Spotify Track {i}/{len(spotify_tracks)} ---")
        
        track = YouTubeSearcher.search_and_update_track(track)
        
        if track.duration_match:
            successful_matches += 1
    
    # Save results
    FileManager.save_tracks_json(spotify_tracks, Config.SPOTIFY_TRACKS_WITH_YOUTUBE_JSON)
    
    print(f"\n{'='*60}")
    print(f"SPOTIFY RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Total Spotify tracks processed: {len(spotify_tracks)}")
    print(f"Successful duration matches: {successful_matches}")
    print(f"Match rate: {successful_matches/len(spotify_tracks)*100:.1f}%")
    print(f"\nResults saved to:")
    print(f"- {Config.SPOTIFY_TRACKS_WITH_YOUTUBE_JSON}")

if __name__ == "__main__":
    main()