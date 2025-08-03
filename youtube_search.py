#!/usr/bin/env python3

from utils import Config, FileManager, YouTubeSearcher, Track

def main():
    Config.ensure_dirs()
    
    # Load extracted tracks
    tracks_data = FileManager.load_tracks_json(Config.EXTRACTED_TRACKS_JSON)
    
    print(f"Processing {len(tracks_data)} tracks...")
    
    successful_matches = 0
    
    for i, track in enumerate(tracks_data, 1):
        print(f"\n--- Track {i}/{len(tracks_data)} ---")
        
        track = YouTubeSearcher.search_and_update_track(track)
        
        if track.duration_match:
            successful_matches += 1
    
    # Save results
    FileManager.save_tracks_json(tracks_data, Config.TRACKS_WITH_YOUTUBE_JSON)
    
    print(f"\n{'='*60}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Total tracks processed: {len(tracks_data)}")
    print(f"Successful duration matches: {successful_matches}")
    print(f"Match rate: {successful_matches/len(tracks_data)*100:.1f}%")
    print(f"\nResults saved to:")
    print(f"- {Config.TRACKS_WITH_YOUTUBE_JSON}")

# Keep the old function for backwards compatibility
def search_youtube_track(title, artist, target_duration):
    """Legacy function for backwards compatibility"""
    return YouTubeSearcher.search_youtube_track(title, artist, target_duration)

if __name__ == "__main__":
    main()