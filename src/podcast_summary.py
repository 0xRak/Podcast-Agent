#!/usr/bin/env python3
"""
Main command parser and orchestrator for /podcast_summary command.

Usage:
    /podcast_summary @channel1 @channel2 --days=7 --limit=1 --pdf
    python src/podcast_summary.py @lexfridman @joerogan --days=14 --limit=2
"""

import sys
import argparse
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from extractors.youtube_extractor import YouTubeExtractor
from extractors.transcript_fetcher import TranscriptFetcher
from processors.claude_analyzer import ClaudeAnalyzer
from processors.content_chunker import ContentChunker
from processors.insight_formatter import InsightFormatter
from processors.natural_summarizer import NaturalSummarizer
from storage.transcript_storage import TranscriptStorage
from utils.config_manager import ConfigManager
from utils.progress_tracker import ProgressTracker
from converters.md_to_pdf import PodcastPDFConverter

logger = logging.getLogger(__name__)

class PodcastSummaryCommand:
    """Main command handler for podcast summary generation."""
    
    def __init__(self):
        """Initialize the podcast summary command."""
        self.config_manager = ConfigManager()
        self.youtube_extractor = YouTubeExtractor()
        self.transcript_fetcher = TranscriptFetcher()
        self.claude_analyzer = ClaudeAnalyzer()
        self.content_chunker = ContentChunker()
        self.insight_formatter = InsightFormatter()
        self.natural_summarizer = NaturalSummarizer()
        self.transcript_storage = TranscriptStorage()
        self.progress_tracker = ProgressTracker()
        self.pdf_converter = PodcastPDFConverter()
        
        # Load settings
        self.settings = self.config_manager.load_settings_config()
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.settings.get('logging', {}).get('level', 'INFO')
        log_to_file = self.settings.get('logging', {}).get('log_to_file', True)
        log_file = self.settings.get('logging', {}).get('log_file', 'logs/podcast_summary.log')
        
        # Create logs directory
        if log_to_file:
            Path(log_file).parent.mkdir(exist_ok=True)
        
        # Configure logging
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        handlers = [logging.StreamHandler()]
        if log_to_file:
            handlers.append(logging.FileHandler(log_file))
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=handlers
        )
    
    def parse_command(self, args: List[str]) -> Dict[str, Any]:
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(
            description='Generate summaries of latest podcast episodes',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Examples:
  /podcast_summary @lexfridman @joerogan
  /podcast_summary @naval --days=14 --limit=3
  /podcast_summary @allinchamath --pdf --output=custom_dir/
            '''
        )
        
        # Channel arguments
        parser.add_argument(
            'channels',
            nargs='+',
            help='Channel handles (e.g., @lexfridman @joerogan)'
        )
        
        # Optional flags
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to look back for videos (default: 7)'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=1,
            help='Maximum videos per channel (default: 1)'
        )
        
        parser.add_argument(
            '--pdf',
            action='store_true',
            help='Generate PDF output in addition to markdown'
        )
        
        parser.add_argument(
            '--config',
            type=str,
            help='Path to custom configuration file'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            default='podcast_summaries',
            help='Output directory (default: podcast_summaries)'
        )
        
        parser.add_argument(
            '--verbose',
            '-v',
            action='store_true',
            help='Enable verbose logging'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without actually doing it'
        )
        
        parsed_args = parser.parse_args(args)
        
        # Clean channel handles (remove @ prefix if present)
        parsed_args.channels = [ch.lstrip('@') for ch in parsed_args.channels]
        
        return vars(parsed_args)
    
    async def execute_command(self, args: Dict[str, Any]) -> bool:
        """Execute the podcast summary command."""
        try:
            logger.info(f"Starting podcast summary for channels: {args['channels']}")
            
            # Initialize progress tracker
            self.progress_tracker.start_processing(args['channels'])
            
            if args.get('verbose'):
                logger.setLevel(logging.DEBUG)
            
            # Validate channels
            valid_channels = await self._validate_channels(args['channels'])
            if not valid_channels:
                logger.error("No valid channels found")
                return False
            
            if args.get('dry_run'):
                logger.info("DRY RUN - Would process these channels:")
                for channel in valid_channels:
                    logger.info(f"  @{channel}")
                return True
            
            # Process each channel
            all_analyses = []
            
            for channel in valid_channels:
                try:
                    self.progress_tracker.start_channel(channel)
                    
                    # Extract videos
                    videos = self.youtube_extractor.get_channel_videos(
                        channel, 
                        days_back=args['days'], 
                        limit=args['limit']
                    )
                    
                    if not videos:
                        logger.warning(f"No recent videos found for @{channel}")
                        self.progress_tracker.complete_channel(channel, success=False, 
                                                             error="No recent videos")
                        continue
                    
                    # Process each video
                    for video in videos:
                        analysis = await self._process_single_video(video)
                        if analysis:
                            all_analyses.append(analysis)
                    
                    self.progress_tracker.complete_channel(channel, success=True)
                    
                    # Update channel's last processed time
                    self.config_manager.update_channel_last_processed(
                        channel, 
                        datetime.now().isoformat()
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing channel @{channel}: {str(e)}")
                    self.progress_tracker.complete_channel(channel, success=False, error=str(e))
                    continue
            
            # Generate output
            if all_analyses:
                output_file = await self._generate_output(all_analyses, args)
                
                # Generate PDF if requested
                if args.get('pdf') and output_file:
                    await self._generate_pdf(output_file)
                
                # Show summary
                self._show_completion_summary(all_analyses, output_file)
                
                return True
            else:
                logger.error("No analyses were generated")
                return False
                
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            return False
        finally:
            self.progress_tracker.finish_processing()
    
    async def _validate_channels(self, channels: List[str]) -> List[str]:
        """Validate that channels exist and are accessible."""
        valid_channels = []
        
        for channel in channels:
            try:
                if self.youtube_extractor.validate_channel_handle(channel):
                    valid_channels.append(channel)
                    logger.info(f"✓ Channel @{channel} validated")
                else:
                    logger.error(f"✗ Channel @{channel} not found or not accessible")
            except Exception as e:
                logger.error(f"✗ Error validating @{channel}: {str(e)}")
        
        return valid_channels
    
    async def _process_single_video(self, video_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single video: extract and store transcript only."""
        try:
            video_id = video_data.get('video_id')
            video_url = video_data.get('url')
            title = video_data.get('title', 'Unknown')
            
            logger.info(f"Extracting transcript: {title[:50]}...")
            
            # Extract and store transcript
            transcript_path = await self._extract_and_store_transcript(video_data)
            
            if not transcript_path:
                logger.warning(f"Could not extract transcript for: {title}")
                return None
            
            logger.info(f"✓ Transcript stored: {title[:30]}...")
            
            # Return transcript info for output generation
            analysis = {
                'video_metadata': video_data,
                'transcript_path': transcript_path,
                'processing_metadata': {
                    'extraction_timestamp': datetime.now().isoformat(),
                    'method': 'transcript_extraction_only'
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error extracting transcript for {video_data.get('title', 'Unknown')}: {str(e)}")
            return None
    
    async def _extract_and_store_transcript(self, video_data: Dict[str, Any]) -> Optional[str]:
        """Phase 1: Extract transcript and store it."""
        try:
            video_id = video_data.get('video_id')
            video_url = video_data.get('url')
            title = video_data.get('title', 'Unknown')
            
            # Check if transcript already exists
            if self.transcript_storage.transcript_exists(video_data):
                existing_path = self.transcript_storage.get_transcript_path(video_data)
                logger.info(f"Transcript already exists: {existing_path}")
                return existing_path
            
            # Get transcript
            transcript, method = self.transcript_fetcher.get_transcript(video_url, video_id)
            
            if not transcript:
                logger.warning(f"Could not get transcript for: {title}")
                return None
            
            logger.info(f"Got transcript via {method} ({len(transcript)} chars)")
            
            # Store transcript
            transcript_path = self.transcript_storage.store_transcript(video_data, transcript)
            
            if transcript_path:
                logger.info(f"Stored transcript: {transcript_path}")
                return transcript_path
            else:
                logger.error(f"Failed to store transcript for: {title}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting transcript: {str(e)}")
            return None
    
    
    async def _generate_output(self, analyses: List[Dict[str, Any]], args: Dict[str, Any]) -> str:
        """Generate transcript extraction report."""
        try:
            # Create simple extraction report
            timestamp = datetime.now().strftime("%Y-%m-%d")
            output_filename = f"transcript-extraction-{timestamp}.md"
            output_path = f"transcript_reports/{output_filename}"
            
            # Ensure output directory exists
            Path("transcript_reports").mkdir(exist_ok=True)
            
            # Generate content
            content = self._create_extraction_report(analyses)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Generated transcript extraction report: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating output: {str(e)}")
            return ""
    
    def _create_extraction_report(self, analyses: List[Dict[str, Any]]) -> str:
        """Create transcript extraction report."""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        video_count = len(analyses)
        
        # Header
        content = f"""# Transcript Extraction Report

**Generated:** {timestamp}  
**Videos Processed:** {video_count}

---

## Extracted Transcripts

"""
        
        # Add each extracted transcript info
        for analysis in analyses:
            metadata = analysis.get('video_metadata', {})
            transcript_path = analysis.get('transcript_path', 'Unknown')
            
            title = metadata.get('title', 'Unknown Title')
            channel = metadata.get('uploader', 'Unknown Channel')
            duration = self._format_duration(metadata.get('duration'))
            upload_date = metadata.get('upload_date', 'Unknown Date')
            
            content += f"""### {title}

**Channel:** {channel}  
**Duration:** {duration}  
**Published:** {upload_date}  
**Transcript:** `{transcript_path}`

**Next Steps:** Run `/summarize {transcript_path}` to create a natural language summary.

---

"""
        
        # Footer with summary commands
        content += f"""## Summary Commands

To create summaries from the extracted transcripts, use:

"""
        
        for analysis in analyses:
            transcript_path = analysis.get('transcript_path', '')
            if transcript_path:
                content += f"- `/summarize {transcript_path}`\n"
        
        content += f"""
**Processing Summary:**
- **Videos Processed:** {video_count}
- **Transcripts Extracted:** {len([a for a in analyses if a.get('transcript_path')])}
- **Generated:** {timestamp}

*Generated with the Podcast Transcript Extractor*
"""
        
        return content
    
    def _format_duration(self, duration_seconds: Optional[int]) -> str:
        """Format duration in seconds to human-readable string."""
        if not duration_seconds:
            return "Unknown"
        
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return f"{seconds}s"
    
    async def _generate_pdf(self, markdown_file: str) -> str:
        """Generate PDF from markdown file."""
        try:
            if not markdown_file or not os.path.exists(markdown_file):
                logger.error(f"Markdown file not found: {markdown_file}")
                return ""
            
            logger.info("Generating PDF from markdown...")
            
            # Generate PDF path
            md_path = Path(markdown_file)
            pdf_path = md_path.parent / f"{md_path.stem}.pdf"
            
            # Convert to PDF
            success = self.pdf_converter.convert_markdown_to_pdf(markdown_file, str(pdf_path))
            
            if success:
                logger.info(f"✓ PDF generated: {pdf_path}")
                return str(pdf_path)
            else:
                logger.error("PDF generation failed")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return ""
    
    def _show_completion_summary(self, analyses: List[Dict[str, Any]], output_file: str):
        """Show completion summary to user."""
        
        # Generate quick summary
        summary = self.insight_formatter.generate_quick_summary(analyses)
        print(summary)
        
        if output_file:
            print(f"\n📁 Full summary available at: {output_file}")
        
        # Show processing statistics
        stats = self.progress_tracker.get_statistics()
        if stats:
            print(f"\n📊 Processing Stats:")
            print(f"   • Total time: {stats.get('total_time', 'Unknown')}")
            print(f"   • Success rate: {stats.get('success_rate', 'Unknown')}")


def main():
    """Main entry point for command line usage."""
    try:
        command = PodcastSummaryCommand()
        
        # Parse command line arguments
        args = command.parse_command(sys.argv[1:])
        
        # Execute command
        success = asyncio.run(command.execute_command(args))
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Command interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Command failed: {str(e)}")
        sys.exit(1)


def podcast_summary_slash_command(command_args: str) -> bool:
    """
    Entry point for Claude Code slash command integration.
    
    Args:
        command_args: Command arguments string (e.g., "@lexfridman @joerogan --days=7")
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Parse the command string into arguments
        import shlex
        args_list = shlex.split(command_args)
        
        command = PodcastSummaryCommand()
        args = command.parse_command(args_list)
        
        return asyncio.run(command.execute_command(args))
        
    except Exception as e:
        logger.error(f"Slash command failed: {str(e)}")
        return False


if __name__ == "__main__":
    main()