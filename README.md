# Music Discovery & Download Pipeline

A Python-based tool for extracting track metadata from Beatport and Spotify, finding corresponding YouTube videos, and downloading them as MP3 files.

## Features

- **Track Extraction**: Scrape track metadata from Beatport URLs
- **YouTube Search**: Find matching YouTube videos with duration verification
- **MP3 Download**: Convert YouTube videos to high-quality MP3 files
- **Dual Source Support**: Works with both Beatport and Spotify track lists
- **Error Handling**: Robust error handling with detailed logging

## Workflow

1. **Extract Track Info** (`extract_tracklist.py`): Scrape Beatport URLs to get track metadata
2. **Find YouTube Matches** (`youtube_search.py`): Search YouTube for matching tracks with duration verification
3. **Download as MP3** (`youtube_to_mp3.py`): Download and convert to MP3 format

## Scripts

### Core Scripts
- `extract_tracklist.py` - Extracts track metadata from Beatport URLs
- `youtube_search.py` - Searches YouTube for tracks and verifies duration matches
- `youtube_to_mp3.py` - Downloads YouTube videos and converts to MP3
- `spotify_youtube_search.py` - YouTube search for Spotify tracks

### Batch Download Scripts
- `download_all_tracks.py` - Downloads all tracks from Beatport tracklist
- `download_spotify_tracks.py` - Downloads all tracks from Spotify tracklist

## Data Files

### Input
- `tracklist.txt` - List of Beatport URLs
- `spotify_track.csv` - Spotify track list

### Generated Data
- `extracted_tracks.csv/json` - Extracted Beatport track metadata
- `tracks_with_youtube.csv/json` - Beatport tracks with YouTube matches
- `spotify_tracks_with_youtube.csv/json` - Spotify tracks with YouTube matches

### Output
- `output/` - Downloaded MP3 files

## Requirements

```bash
pip install yt-dlp requests beautifulsoup4
```

## Usage

1. **Extract Beatport tracks**:
   ```bash
   python extract_tracklist.py
   ```

2. **Find YouTube matches**:
   ```bash
   python youtube_search.py
   ```

3. **Download all tracks**:
   ```bash
   python download_all_tracks.py
   ```

## Features

- **Duration Verification**: Matches YouTube tracks within ±5 seconds of original duration
- **Individual Processing**: Downloads tracks one-by-one to avoid playlist issues
- **Error Recovery**: Continues processing even if individual tracks fail
- **Progress Tracking**: Detailed console output with success/failure statistics

## Notes

- MP3 files are saved with 192kbps quality
- Original track metadata is preserved in CSV/JSON format
- Failed downloads are logged with error details
- YouTube URLs are validated before download