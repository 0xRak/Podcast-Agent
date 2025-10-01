"""YouTube metadata extractor using yt-dlp."""

import yt_dlp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class YouTubeExtractor:
    """Extract video metadata from YouTube channels using yt-dlp."""
    
    def __init__(self):
        """Initialize the YouTube extractor with optimal settings."""
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
        }
    
    def get_channel_videos(self, channel_handle: str, days_back: int = 7, limit: int = 1) -> List[Dict[str, Any]]:
        """
        Get recent videos from a YouTube channel.
        
        Args:
            channel_handle: YouTube channel handle (e.g., 'lexfridman')
            days_back: Number of days to look back for videos
            limit: Maximum number of videos to return
            
        Returns:
            List of video metadata dictionaries
        """
        try:
            # Build channel URL from handle - use /videos path for video listings
            channel_url = f"https://www.youtube.com/@{channel_handle.lstrip('@')}/videos"
            logger.info(f"Extracting videos from {channel_url}")
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract channel info and video list
                channel_info = ydl.extract_info(channel_url, download=False)
                
                if not channel_info or 'entries' not in channel_info:
                    logger.error(f"Could not extract channel info for {channel_handle}")
                    return []
                
                videos = []
                processed_count = 0
                
                for entry in channel_info['entries']:
                    if processed_count >= limit:
                        break

                    if not entry:
                        continue

                    # Get video URL from entry
                    video_id = entry.get('id')
                    video_url = entry.get('url') or entry.get('webpage_url')

                    # Construct URL from ID if not available
                    if not video_url and video_id:
                        video_url = f"https://www.youtube.com/watch?v={video_id}"

                    if not video_url:
                        logger.warning(f"Could not determine video URL for entry: {entry}")
                        continue

                    # Try to get detailed video info, but fall back to basic info if it fails
                    video_info = self._get_video_details(video_url)
                    if not video_info:
                        # Fall back to basic info from channel listing
                        logger.warning(f"Using basic info for {video_id} due to extraction errors")
                        video_info = entry

                    # Check if video is within date range (use basic info if detailed failed)
                    upload_date = self._parse_upload_date(video_info.get('upload_date'))
                    if upload_date and upload_date < cutoff_date:
                        continue

                    # Extract relevant metadata with fallbacks and safe string handling
                    video_data = {
                        'video_id': video_info.get('id') or video_id,
                        'url': video_info.get('webpage_url') or video_url,
                        'title': (video_info.get('title') or '').strip(),
                        'description': (video_info.get('description') or '').strip(),
                        'duration': video_info.get('duration'),
                        'upload_date': upload_date.isoformat() if upload_date else None,
                        'uploader': (video_info.get('uploader') or '').strip(),
                        'channel_handle': channel_handle,
                        'view_count': video_info.get('view_count'),
                        'like_count': video_info.get('like_count'),
                        'has_subtitles': bool(video_info.get('subtitles') or video_info.get('automatic_captions'))
                    }

                    videos.append(video_data)
                    processed_count += 1
                    logger.info(f"Extracted: {video_data['title'][:50]}...")
                
                logger.info(f"Found {len(videos)} recent videos for {channel_handle}")
                return videos
                
        except Exception as e:
            logger.error(f"Error extracting videos from {channel_handle}: {str(e)}")
            return []
    
    def _get_video_details(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific video."""
        try:
            # Use different options for video details to avoid format extraction
            video_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'extract_flat': False,  # Need full info but no download
                'no_check_certificate': True,
                'listformats': False,  # Don't list formats
                'format': 'worst',  # Use worst format to avoid extraction issues
                'noplaylist': True
            }
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                return ydl.extract_info(video_url, download=False)
        except Exception as e:
            logger.error(f"Error getting video details for {video_url}: {str(e)}")
            return None
    
    def _parse_upload_date(self, date_string: str) -> Optional[datetime]:
        """Parse upload date string into datetime object."""
        if not date_string:
            return None
        
        try:
            # yt-dlp returns dates in YYYYMMDD format
            if len(date_string) == 8 and date_string.isdigit():
                return datetime.strptime(date_string, '%Y%m%d')
        except ValueError:
            pass
        
        try:
            # Try other common formats
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y']:
                return datetime.strptime(date_string, fmt)
        except ValueError:
            pass
        
        logger.warning(f"Could not parse upload date: {date_string}")
        return None
    
    def format_duration(self, duration_seconds: Optional[int]) -> str:
        """Format duration in seconds to human-readable string."""
        if not duration_seconds:
            return "Unknown"
        
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def validate_channel_handle(self, handle: str) -> bool:
        """Validate if a channel handle exists and is accessible."""
        try:
            channel_url = f"https://www.youtube.com/@{handle.lstrip('@')}/videos"
            with yt_dlp.YoutubeDL({**self.ydl_opts, 'extract_flat': True}) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                return info is not None and 'entries' in info
        except Exception:
            return False


# Example usage for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    extractor = YouTubeExtractor()
    
    # Test with a known channel
    videos = extractor.get_channel_videos('lexfridman', days_back=14, limit=2)
    
    for video in videos:
        print(f"Title: {video['title']}")
        print(f"URL: {video['url']}")
        print(f"Duration: {extractor.format_duration(video['duration'])}")
        print(f"Upload Date: {video['upload_date']}")
        print(f"Has Subtitles: {video['has_subtitles']}")
        print("-" * 50)