#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re
import time
import csv

def extract_track_info(url):
    """Extract track name, artist, and duration from Beatport URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract track title - look for the actual track name in H1
        title_element = soup.find('h1')
        if title_element:
            title = title_element.text.strip()
            # Clean up duplicated feat. parts
            if 'feat.' in title:
                parts = title.split('feat.')
                if len(parts) > 2:
                    title = parts[0] + 'feat.' + parts[1]
                title = title.strip()
        else:
            # Fallback to page title
            title_element = soup.find('title')
            if title_element:
                page_title = title_element.text
                if ' - ' in page_title:
                    # Extract everything after the artists and before the label
                    parts = page_title.split(' - ')
                    if len(parts) >= 2:
                        title = parts[1].split(' [')[0].strip()
                    else:
                        title = 'Unknown Title'
                else:
                    title = 'Unknown Title'
            else:
                title = 'Unknown Title'
        
        # Extract artist
        artist_element = soup.find('p', class_='interior-track-artists')
        if not artist_element:
            artist_elements = soup.find_all('a', href=re.compile(r'/artist/'))
            if artist_elements:
                artist = ', '.join([a.text.strip() for a in artist_elements[:3]])
            else:
                artist = 'Unknown Artist'
        else:
            artist_links = artist_element.find_all('a')
            if artist_links:
                artist = ', '.join([a.text.strip() for a in artist_links])
            else:
                artist = artist_element.text.strip()
        
        # Extract duration
        duration_element = soup.find('p', class_='interior-track-length')
        if not duration_element:
            duration_pattern = re.compile(r'\b\d{1,2}:\d{2}\b')
            duration_match = duration_pattern.search(response.text)
            duration = duration_match.group() if duration_match else 'Unknown Duration'
        else:
            duration = duration_element.text.strip()
        
        return {
            'title': title,
            'artist': artist,
            'duration': duration,
            'url': url
        }
        
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return {
            'title': 'Error',
            'artist': 'Error',
            'duration': 'Error',
            'url': url
        }

def main():
    # Read URLs from tracklist.txt
    with open('data/tracklist.txt', 'r') as file:
        urls = [line.strip() for line in file if line.strip()]
    
    print(f"Found {len(urls)} tracks to process")
    
    tracks = []
    
    for i, url in enumerate(urls, 1):
        print(f"Processing track {i}/{len(urls)}: {url}")
        track_info = extract_track_info(url)
        tracks.append(track_info)
        
        # Be respectful to the server
        time.sleep(1)
    
    # Output results
    print("\n" + "="*80)
    print("EXTRACTED TRACK INFORMATION")
    print("="*80)
    
    for i, track in enumerate(tracks, 1):
        print(f"{i:2d}. {track['title']}")
        print(f"    Artist: {track['artist']}")
        print(f"    Duration: {track['duration']}")
        print(f"    URL: {track['url']}")
        print()
    
    # Save to CSV
    with open('data/extracted_tracks.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['track_number', 'title', 'artist', 'duration', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for i, track in enumerate(tracks, 1):
            writer.writerow({
                'track_number': i,
                'title': track['title'],
                'artist': track['artist'],
                'duration': track['duration'],
                'url': track['url']
            })
    
    print(f"Results saved to data/extracted_tracks.csv")

if __name__ == "__main__":
    main()