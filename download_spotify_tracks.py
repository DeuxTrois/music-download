import json
from youtube_to_mp3 import download_youtube_to_mp3

def load_spotify_youtube_urls():
    """Load YouTube URLs from spotify_tracks_with_youtube.json file"""
    with open('spotify_tracks_with_youtube.json', 'r', encoding='utf-8') as file:
        tracks = json.load(file)
    
    youtube_urls = []
    valid_tracks = []
    
    for track in tracks:
        youtube_url = track.get('youtube_url')
        if youtube_url:
            youtube_urls.append(youtube_url)
            valid_tracks.append(track)
    
    print(f"Found {len(youtube_urls)} Spotify tracks with YouTube URLs out of {len(tracks)} total tracks")
    return youtube_urls, valid_tracks

if __name__ == "__main__":
    # Load all YouTube URLs from the Spotify tracks file
    youtube_urls, tracks = load_spotify_youtube_urls()
    
    print(f"Starting download of {len(youtube_urls)} Spotify tracks...")
    
    # Download all URLs to MP3
    download_youtube_to_mp3(youtube_urls)