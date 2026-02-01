#!/usr/bin/env python3
"""
Script to fetch transcript for a specific YouTube video and prepare it for summarization.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from extractors.youtube_extractor import YouTubeExtractor
from extractors.transcript_fetcher import TranscriptFetcher
from storage.transcript_storage import TranscriptStorage

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Fetch transcript for a YouTube video')
    parser.add_argument('url', help='YouTube video URL')
    args = parser.parse_args()

    url = args.url
    print(f"I will process video: {url}")

    # 1. Get Video Details
    extractor = YouTubeExtractor()
    # We need to get video_id first to extract details properly if we use the internal methods, 
    # but let's try to use the public methods if possible.
    # YouTubeExtractor doesn't have a simple "get_video_details(url)" public method, 
    # but it has _get_video_details. Let's use that or replicate it.
    
    # Actually, let's use the TranscriptFetcher to get the ID, then use that.
    fetcher = TranscriptFetcher()
    video_id = fetcher._extract_video_id(url)
    
    if not video_id:
        print("Error: Could not extract video ID from URL")
        sys.exit(1)
        
    print(f"Video ID: {video_id}")
    
    # Get details
    try:
        import yt_dlp
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': True, # Use flat extraction which is faster and less error prone for metadata
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_data = ydl.extract_info(url, download=False)
    except Exception as e:
        print(f"Error extracting with yt-dlp: {e}")
        video_data = None

    if not video_data:
        print("Warning: Could not get video details. Using fallback metadata.")
        video_data = {
            'id': video_id,
            'webpage_url': url,
            'title': f'YouTube Video {video_id}',
            'description': 'Description not available',
            'duration': 0,
            'upload_date': '20240101',
            'uploader': 'Unknown Channel',
            'uploader_id': 'unknown',
            'view_count': 0
        }
        
    # Clean up video data to match what TranscriptStorage expects
    # In extract_flat=True mode, the keys might be slightly different or limited
    clean_video_data = {
        'video_id': video_data.get('id') or video_id,
        'url': video_data.get('webpage_url') or url,
        'title': (video_data.get('title') or '').strip(),
        'description': (video_data.get('description') or '').strip(),
        'duration': video_data.get('duration'),
        'upload_date': video_data.get('upload_date'), 
        'uploader': (video_data.get('uploader') or '').strip(),
        'channel_handle': video_data.get('uploader_id') or video_data.get('channel_url', '').split('/')[-1] or 'unknown',
        'view_count': video_data.get('view_count'),
    }
    
    print(f"Title: {clean_video_data['title']}")
    
    # 2. Get Transcript
    transcript, method = fetcher.get_transcript(url, video_id)
    
    if not transcript:
        print("Error: Could not fetch transcript")
        sys.exit(1)
        
    print(f"Fetched transcript ({len(transcript)} chars) via {method}")
    
    # 3. Store Transcript
    storage = TranscriptStorage()
    filepath = storage.store_transcript(clean_video_data, transcript)
    
    if filepath:
        print(f"SUCCESS: Transcript saved to: {filepath}")
        print(filepath) # Print raw path on last line for parsing
    else:
        print("Error: Failed to save transcript")
        sys.exit(1)

if __name__ == "__main__":
    main()
