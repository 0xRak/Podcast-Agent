"""Transcript storage system for clean file organization."""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TranscriptStorage:
    """Store and retrieve podcast transcripts with clean file structure."""
    
    def __init__(self, storage_dir: str = "transcripts"):
        """Initialize transcript storage."""
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
    def store_transcript(self, video_metadata: Dict[str, Any], transcript: str) -> str:
        """
        Store transcript with metadata in organized file structure.
        
        Args:
            video_metadata: Video information (title, channel, etc.)
            transcript: Full transcript text
            
        Returns:
            Path to stored transcript file
        """
        try:
            # Generate clean filename
            channel = video_metadata.get('channel_handle', 'unknown').replace('@', '')
            video_id = video_metadata.get('video_id', 'unknown')
            upload_date = video_metadata.get('upload_date', '')
            
            # Format date for filename
            date_str = self._format_date_for_filename(upload_date)
            
            filename = f"{channel}_{date_str}_{video_id}.md"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Create transcript content with metadata
            content = self._format_transcript_content(video_metadata, transcript)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Stored transcript: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error storing transcript: {str(e)}")
            return ""
    
    def load_transcript(self, filepath: str) -> tuple[Dict[str, Any], str]:
        """
        Load transcript and metadata from file.
        
        Args:
            filepath: Path to transcript file
            
        Returns:
            Tuple of (metadata, transcript_text)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse metadata and transcript from content
            metadata, transcript = self._parse_transcript_content(content)
            
            logger.info(f"Loaded transcript: {filepath}")
            return metadata, transcript
            
        except Exception as e:
            logger.error(f"Error loading transcript: {str(e)}")
            return {}, ""
    
    def get_transcript_path(self, video_metadata: Dict[str, Any]) -> str:
        """Get the expected filepath for a transcript."""
        channel = video_metadata.get('channel_handle', 'unknown').replace('@', '')
        video_id = video_metadata.get('video_id', 'unknown')
        upload_date = video_metadata.get('upload_date', '')
        
        date_str = self._format_date_for_filename(upload_date)
        filename = f"{channel}_{date_str}_{video_id}.md"
        
        return os.path.join(self.storage_dir, filename)
    
    def transcript_exists(self, video_metadata: Dict[str, Any]) -> bool:
        """Check if transcript already exists for this video."""
        filepath = self.get_transcript_path(video_metadata)
        return os.path.exists(filepath)
    
    def list_transcripts(self, channel: Optional[str] = None) -> list[str]:
        """List all stored transcript files, optionally filtered by channel."""
        try:
            files = []
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.md'):
                    if channel is None or filename.startswith(f"{channel}_"):
                        files.append(os.path.join(self.storage_dir, filename))
            
            # Sort by modification time (newest first)
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            return files
            
        except Exception as e:
            logger.error(f"Error listing transcripts: {str(e)}")
            return []
    
    def _format_transcript_content(self, metadata: Dict[str, Any], transcript: str) -> str:
        """Format transcript content with metadata header."""
        
        # Clean metadata for display
        title = metadata.get('title', 'Unknown Title')
        channel = metadata.get('uploader', 'Unknown Channel')
        channel_handle = metadata.get('channel_handle', 'unknown')
        duration = self._format_duration(metadata.get('duration'))
        upload_date = metadata.get('upload_date', 'Unknown Date')
        video_url = metadata.get('url', '')
        video_id = metadata.get('video_id', '')
        
        # Format date for display
        formatted_date = self._format_date_for_display(upload_date)
        
        content = f"""# {title}

**Channel:** {channel} (@{channel_handle})  
**Duration:** {duration}  
**Published:** {formatted_date}  
**Video ID:** {video_id}  
**URL:** {video_url}

**Extracted:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

---

## Transcript

{transcript.strip()}

---

**Metadata:**
```json
{json.dumps(metadata, indent=2)}
```
"""
        return content
    
    def _parse_transcript_content(self, content: str) -> tuple[Dict[str, Any], str]:
        """Parse metadata and transcript from stored content."""
        try:
            # Find transcript section
            transcript_start = content.find("## Transcript\n\n")
            metadata_start = content.find("**Metadata:**\n```json\n")
            
            if transcript_start == -1:
                return {}, content.strip()
            
            transcript_start += len("## Transcript\n\n")
            
            if metadata_start == -1:
                transcript_text = content[transcript_start:].strip()
                return {}, transcript_text
            
            # Extract transcript text
            transcript_text = content[transcript_start:metadata_start].strip()
            if transcript_text.endswith("---"):
                transcript_text = transcript_text[:-3].strip()
            
            # Extract metadata
            metadata_start += len("**Metadata:**\n```json\n")
            metadata_end = content.find("\n```", metadata_start)
            
            if metadata_end == -1:
                return {}, transcript_text
            
            metadata_json = content[metadata_start:metadata_end]
            metadata = json.loads(metadata_json)
            
            return metadata, transcript_text
            
        except Exception as e:
            logger.error(f"Error parsing transcript content: {str(e)}")
            return {}, content.strip()
    
    def _format_duration(self, duration_seconds: Optional[int]) -> str:
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
    
    def _format_date_for_filename(self, date_string: str) -> str:
        """Format date string for use in filename."""
        if not date_string:
            return "unknown"
        
        try:
            # Handle ISO format
            if 'T' in date_string:
                date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                return date_obj.strftime('%Y%m%d')
            
            # Handle YYYY-MM-DD format
            if len(date_string) == 10 and date_string.count('-') == 2:
                date_obj = datetime.strptime(date_string, '%Y-%m-%d')
                return date_obj.strftime('%Y%m%d')
            
            # Handle YYYYMMDD format
            if len(date_string) == 8 and date_string.isdigit():
                return date_string
            
            return "unknown"
            
        except Exception:
            return "unknown"
    
    def _format_date_for_display(self, date_string: str) -> str:
        """Format date string for display."""
        if not date_string:
            return "Unknown Date"
        
        try:
            # Handle ISO format
            if 'T' in date_string:
                date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                return date_obj.strftime('%B %d, %Y')
            
            # Handle YYYY-MM-DD format
            if len(date_string) == 10 and date_string.count('-') == 2:
                date_obj = datetime.strptime(date_string, '%Y-%m-%d')
                return date_obj.strftime('%B %d, %Y')
            
            # Handle YYYYMMDD format
            if len(date_string) == 8 and date_string.isdigit():
                date_obj = datetime.strptime(date_string, '%Y%m%d')
                return date_obj.strftime('%B %d, %Y')
            
            return date_string
            
        except Exception:
            return date_string or "Unknown Date"


# Example usage for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    storage = TranscriptStorage()
    
    # Test storing transcript
    sample_metadata = {
        'title': 'Sample Podcast Episode',
        'uploader': 'Test Channel',
        'channel_handle': 'testchannel',
        'duration': 3600,  # 1 hour
        'upload_date': '2024-01-15',
        'video_id': 'abc123',
        'url': 'https://youtube.com/watch?v=abc123'
    }
    
    sample_transcript = """
    This is a sample transcript for testing the storage system.
    It contains multiple lines of dialogue and content.
    """
    
    # Store transcript
    filepath = storage.store_transcript(sample_metadata, sample_transcript)
    print(f"Stored at: {filepath}")
    
    # Load transcript back
    loaded_metadata, loaded_transcript = storage.load_transcript(filepath)
    print(f"Loaded metadata: {loaded_metadata.get('title')}")
    print(f"Loaded transcript length: {len(loaded_transcript)} chars")
    
    # List transcripts
    transcripts = storage.list_transcripts()
    print(f"Found {len(transcripts)} transcripts")