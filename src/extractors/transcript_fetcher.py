"""Transcript fetcher with youtube-transcript-api and web scraping fallbacks."""

import logging
import re
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

logger = logging.getLogger(__name__)

class TranscriptFetcher:
    """Fetch video transcripts with multiple fallback methods."""
    
    def __init__(self):
        """Initialize the transcript fetcher."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def get_transcript(self, video_url: str, video_id: Optional[str] = None) -> Tuple[Optional[str], str]:
        """
        Get transcript for a video using multiple methods.
        
        Args:
            video_url: YouTube video URL
            video_id: YouTube video ID (extracted from URL if not provided)
            
        Returns:
            Tuple of (transcript_text, method_used)
        """
        if not video_id:
            video_id = self._extract_video_id(video_url)
        
        if not video_id:
            logger.error(f"Could not extract video ID from URL: {video_url}")
            return None, "failed"
        
        # Method 1: youtube-transcript-api (fastest and most reliable)
        transcript, method = self._get_transcript_youtube_api(video_id)
        if transcript:
            return transcript, method
        
        # Method 2: Web scraping fallback
        transcript, method = self._get_transcript_web_scraping(video_url, video_id)
        if transcript:
            return transcript, method
        
        logger.error(f"All transcript extraction methods failed for video: {video_id}")
        return None, "failed"
    
    def _extract_video_id(self, video_url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        try:
            parsed_url = urlparse(video_url)
            
            # Handle different YouTube URL formats
            if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
                if parsed_url.path == '/watch':
                    return parse_qs(parsed_url.query).get('v', [None])[0]
                elif parsed_url.path.startswith('/embed/'):
                    return parsed_url.path.split('/embed/')[1].split('?')[0]
            elif parsed_url.hostname in ['youtu.be']:
                return parsed_url.path[1:].split('?')[0]
            
            # Try regex as last resort
            match = re.search(r'(?:v=|\/|embed\/|youtu\.be\/)([a-zA-Z0-9_-]{11})', video_url)
            return match.group(1) if match else None
            
        except Exception as e:
            logger.error(f"Error extracting video ID from {video_url}: {str(e)}")
            return None
    
    def _get_transcript_youtube_api(self, video_id: str) -> Tuple[Optional[str], str]:
        """Get transcript using youtube-transcript-api."""
        try:
            logger.info(f"Attempting to get transcript via YouTube API for {video_id}")
            
            # Try to get transcript in English first
            ytt_api = YouTubeTranscriptApi()
            fetched_transcript = ytt_api.fetch(video_id, languages=['en', 'en-US', 'en-GB'])
            
            # Get the raw transcript data
            transcript_data = fetched_transcript.to_raw_data()
            
            # Combine all transcript segments
            transcript_text = ' '.join([entry['text'] for entry in transcript_data])
            
            # Clean up the transcript
            transcript_text = self._clean_transcript(transcript_text)
            
            logger.info(f"Successfully extracted transcript via YouTube API ({len(transcript_text)} chars)")
            return transcript_text, "youtube-transcript-api"
            
        except TranscriptsDisabled:
            logger.warning(f"Transcripts disabled for video {video_id}")
            return None, "transcripts_disabled"
        except NoTranscriptFound:
            logger.warning(f"No transcript found for video {video_id}")
            return None, "no_transcript"
        except VideoUnavailable:
            logger.error(f"Video {video_id} is unavailable")
            return None, "video_unavailable"
        except Exception as e:
            logger.error(f"YouTube API transcript extraction failed for {video_id}: {str(e)}")
            return None, "api_error"
    
    def _get_transcript_web_scraping(self, video_url: str, video_id: str) -> Tuple[Optional[str], str]:
        """Get transcript using web scraping fallback methods."""
        
        # Try different transcript websites
        scrapers = [
            self._scrape_youtubetranscript_com,
            self._scrape_downsub_com,
        ]
        
        for scraper in scrapers:
            try:
                transcript = scraper(video_url, video_id)
                if transcript:
                    return transcript, f"web_scraping_{scraper.__name__}"
            except Exception as e:
                logger.warning(f"{scraper.__name__} failed for {video_id}: {str(e)}")
                continue
        
        return None, "web_scraping_failed"
    
    def _scrape_youtubetranscript_com(self, video_url: str, video_id: str) -> Optional[str]:
        """Scrape transcript from youtubetranscript.com."""
        try:
            # This is a placeholder implementation
            # In practice, you'd need to analyze the website's structure
            logger.info(f"Attempting to scrape youtubetranscript.com for {video_id}")
            
            scraping_url = f"https://youtubetranscript.com/?v={video_id}"
            response = self.session.get(scraping_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for transcript content (this would need to be updated based on actual site structure)
            transcript_element = soup.find('div', {'class': 'transcript'}) or soup.find('pre')
            
            if transcript_element:
                transcript = transcript_element.get_text().strip()
                if len(transcript) > 100:  # Basic validation
                    return self._clean_transcript(transcript)
            
            return None
            
        except Exception as e:
            logger.error(f"youtubetranscript.com scraping failed: {str(e)}")
            return None
    
    def _scrape_downsub_com(self, video_url: str, video_id: str) -> Optional[str]:
        """Scrape transcript from downsub.com."""
        try:
            # This is a placeholder implementation
            logger.info(f"Attempting to scrape downsub.com for {video_id}")
            
            scraping_url = f"https://downsub.com/?url={video_url}"
            response = self.session.get(scraping_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for subtitle/transcript download links or content
            # This would need to be implemented based on actual site structure
            transcript_links = soup.find_all('a', href=re.compile(r'\.txt|\.srt'))
            
            for link in transcript_links:
                if 'english' in link.get('href', '').lower() or 'en' in link.get('href', '').lower():
                    subtitle_url = link.get('href')
                    if subtitle_url.startswith('/'):
                        subtitle_url = f"https://downsub.com{subtitle_url}"
                    
                    subtitle_response = self.session.get(subtitle_url, timeout=30)
                    subtitle_response.raise_for_status()
                    
                    transcript = self._extract_text_from_srt(subtitle_response.text)
                    if transcript:
                        return self._clean_transcript(transcript)
            
            return None
            
        except Exception as e:
            logger.error(f"downsub.com scraping failed: {str(e)}")
            return None
    
    def _extract_text_from_srt(self, srt_content: str) -> Optional[str]:
        """Extract plain text from SRT subtitle content."""
        try:
            lines = srt_content.split('\n')
            text_lines = []
            
            for line in lines:
                line = line.strip()
                # Skip sequence numbers and timestamps
                if (line.isdigit() or 
                    re.match(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', line) or 
                    not line):
                    continue
                text_lines.append(line)
            
            return ' '.join(text_lines)
            
        except Exception as e:
            logger.error(f"Error extracting text from SRT: {str(e)}")
            return None
    
    def _clean_transcript(self, transcript: str) -> str:
        """Clean and normalize transcript text."""
        if not transcript:
            return ""
        
        # Remove extra whitespace
        transcript = re.sub(r'\s+', ' ', transcript.strip())
        
        # Remove common transcript artifacts
        transcript = re.sub(r'\[.*?\]', '', transcript)  # Remove [Music], [Applause], etc.
        transcript = re.sub(r'\(.*?\)', '', transcript)  # Remove (unclear), (inaudible), etc.
        
        # Fix common transcript issues
        transcript = re.sub(r'\s+([.!?])', r'\1', transcript)  # Fix spacing before punctuation
        transcript = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', transcript)  # Ensure space after sentences
        
        return transcript.strip()
    
    def get_transcript_info(self, video_id: str) -> Dict[str, any]:
        """Get information about available transcripts for a video."""
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)
            
            info = {
                'available': True,
                'languages': [],
                'auto_generated': [],
                'manual': []
            }
            
            for transcript in transcript_list:
                lang_info = {
                    'language': transcript.language,
                    'language_code': transcript.language_code,
                    'is_generated': transcript.is_generated
                }
                
                info['languages'].append(lang_info)
                
                if transcript.is_generated:
                    info['auto_generated'].append(lang_info)
                else:
                    info['manual'].append(lang_info)
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting transcript info for {video_id}: {str(e)}")
            return {'available': False, 'error': str(e)}


# Example usage for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    fetcher = TranscriptFetcher()
    
    # Test with a known video (replace with actual video URL for testing)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    transcript, method = fetcher.get_transcript(test_url)
    
    if transcript:
        print(f"Method used: {method}")
        print(f"Transcript length: {len(transcript)} characters")
        print(f"First 500 characters:\n{transcript[:500]}...")
    else:
        print(f"Failed to get transcript. Method: {method}")