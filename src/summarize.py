#!/usr/bin/env python3
"""
Summarize command for creating natural language summaries from stored transcripts.

Usage:
    /summarize transcripts/filename.md
    python src/summarize.py transcripts/filename.md
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from storage.transcript_storage import TranscriptStorage
from utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class SummarizeCommand:
    """Command handler for creating natural language summaries from transcripts."""
    
    def __init__(self):
        """Initialize the summarize command."""
        self.config_manager = ConfigManager()
        self.transcript_storage = TranscriptStorage()
        
        # Load settings
        self.settings = self.config_manager.load_settings_config()
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.settings.get('logging', {}).get('level', 'INFO')
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=[logging.StreamHandler()]
        )
    
    def parse_command(self, args: list[str]) -> Dict[str, Any]:
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(
            description='Create natural language summary from transcript',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Examples:
  /summarize transcripts/0xresearchPodcast_20250915_4N0BUzMVMEk.md
  python src/summarize.py transcripts/file.md
'''
        )
        
        parser.add_argument(
            'transcript_path',
            help='Path to the transcript file to summarize'
        )
        
        parser.add_argument(
            '--output', '-o',
            default='podcast_summaries',
            help='Output directory for summary (default: podcast_summaries)'
        )
        
        parser.add_argument(
            '--template',
            choices=['blog', 'insights', 'brief'],
            default='blog',
            help='Summary template style (default: blog)'
        )
        
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output'
        )
        
        # Parse arguments
        parsed_args = parser.parse_args(args)
        
        return {
            'transcript_path': parsed_args.transcript_path,
            'output': parsed_args.output,
            'template': parsed_args.template,
            'verbose': parsed_args.verbose
        }
    
    async def execute(self, args: Dict[str, Any]) -> bool:
        """Execute the summarize command."""
        try:
            transcript_path = args['transcript_path']
            
            # Validate transcript file exists
            if not Path(transcript_path).exists():
                logger.error(f"Transcript file not found: {transcript_path}")
                print(f"❌ Error: Transcript file not found: {transcript_path}")
                return False
            
            logger.info(f"Loading transcript from: {transcript_path}")
            print(f"📄 Loading transcript: {transcript_path}")
            
            # Load transcript
            metadata, transcript = self.transcript_storage.load_transcript(transcript_path)
            
            if not transcript:
                logger.error(f"Could not load transcript content from: {transcript_path}")
                print(f"❌ Error: Could not load transcript content")
                return False
            
            print(f"✅ Loaded transcript ({len(transcript):,} characters)")
            
            # Create summary
            logger.info("Creating natural language summary...")
            print("🤖 Creating natural language summary...")
            
            summary = await self._create_summary(metadata, transcript, args)
            
            if not summary:
                logger.error("Failed to create summary")
                print("❌ Error: Failed to create summary")
                return False
            
            # Save summary
            output_path = await self._save_summary(summary, metadata, args)
            
            if output_path:
                print(f"✅ Summary saved: {output_path}")
                print(f"\n📖 Summary preview:")
                print("-" * 50)
                # Show first 300 characters of summary
                preview = summary[:300] + "..." if len(summary) > 300 else summary
                print(preview)
                print("-" * 50)
                return True
            else:
                print("❌ Error: Failed to save summary")
                return False
                
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return False
    
    async def _create_summary(self, metadata: Dict[str, Any], transcript: str, args: Dict[str, Any]) -> Optional[str]:
        """Create natural language summary using enhanced text analysis."""
        try:
            # Get video metadata for context
            title = metadata.get('title', 'Unknown Title')
            channel = metadata.get('uploader', 'Unknown Channel')
            duration = self._format_duration(metadata.get('duration'))
            
            template = args.get('template', 'blog')
            
            if template == 'blog':
                summary = self._create_blog_summary(title, channel, duration, transcript)
            elif template == 'insights':
                summary = self._create_insights_summary(title, channel, duration, transcript)
            elif template == 'brief':
                summary = self._create_brief_summary(title, channel, duration, transcript)
            else:
                summary = self._create_blog_summary(title, channel, duration, transcript)
            
            logger.info(f"Generated {template} summary ({len(summary)} characters)")
            return summary
            
        except Exception as e:
            logger.error(f"Error creating summary: {str(e)}")
            return None
    
    def _create_blog_summary(self, title: str, channel: str, duration: str, transcript: str) -> str:
        """Create blog-style summary."""
        
        # Extract key elements
        main_topics = self._extract_main_topics(transcript)
        key_quotes = self._extract_key_quotes(transcript)
        insights = self._extract_insights(transcript)
        takeaways = self._extract_takeaways(transcript)
        
        # Create natural blog post
        summary = f"# {title}\n\n"
        
        # Introduction
        if main_topics:
            summary += f"In this {duration} episode from {channel}, the discussion explores {', '.join(main_topics[:3])}. "
        else:
            summary += f"In this {duration} episode from {channel}, the hosts dive into current topics and trends. "
        
        # Main content
        if insights:
            summary += "The conversation reveals several important insights:\n\n"
            for insight in insights[:4]:
                summary += f"**{insight.capitalize()}** - This perspective challenges conventional thinking and offers a fresh approach to understanding the market dynamics.\n\n"
        
        # Key quotes section
        if key_quotes:
            summary += "## Notable Highlights\n\n"
            summary += "Some standout moments from the discussion:\n\n"
            for quote in key_quotes[:3]:
                summary += f'> "{quote}"\n\n'
        
        # Takeaways section
        if takeaways:
            summary += "## Key Takeaways\n\n"
            for i, takeaway in enumerate(takeaways[:4], 1):
                summary += f"{i}. **{takeaway.capitalize()}** - This actionable insight can be implemented immediately.\n\n"
        
        # Conclusion
        if main_topics:
            summary += f"This episode provides valuable perspectives on {main_topics[0] if main_topics else 'the discussed topics'}, "
        summary += "making it a worthwhile listen for anyone interested in staying current with industry developments and strategic thinking."
        
        return summary
    
    def _create_insights_summary(self, title: str, channel: str, duration: str, transcript: str) -> str:
        """Create insights-focused summary."""
        
        insights = self._extract_insights(transcript)
        key_quotes = self._extract_key_quotes(transcript)
        
        summary = f"# Key Insights: {title}\n\n"
        summary += f"**Source:** {channel} ({duration})\n\n"
        summary += "## Strategic Insights\n\n"
        
        for i, insight in enumerate(insights[:5], 1):
            summary += f"### {i}. {insight.capitalize()}\n\n"
            summary += "This insight reveals important market dynamics and strategic considerations.\n\n"
        
        if key_quotes:
            summary += "## Supporting Evidence\n\n"
            for quote in key_quotes[:3]:
                summary += f'- "{quote}"\n\n'
        
        return summary
    
    def _create_brief_summary(self, title: str, channel: str, duration: str, transcript: str) -> str:
        """Create brief summary."""
        
        main_topics = self._extract_main_topics(transcript)
        key_quote = self._extract_key_quotes(transcript)
        
        summary = f"# {title}\n\n"
        summary += f"**{channel}** • {duration}\n\n"
        
        if main_topics:
            summary += f"**Topics:** {', '.join(main_topics[:4])}\n\n"
        
        if key_quote:
            summary += f"**Key Quote:** \"{key_quote[0]}\"\n\n"
        
        summary += "**Worth Listening:** Contains valuable insights and perspectives relevant to current market dynamics."
        
        return summary
    
    def _extract_main_topics(self, transcript: str) -> list[str]:
        """Extract main topics from transcript."""
        import re
        
        words = transcript.lower().split()
        
        # Topic categories with keywords
        topics = {
            'cryptocurrency and blockchain': ['crypto', 'bitcoin', 'ethereum', 'blockchain', 'defi', 'token'],
            'business and strategy': ['business', 'strategy', 'company', 'market', 'revenue', 'growth'],
            'investing and finance': ['investment', 'portfolio', 'trading', 'valuation', 'funding', 'capital'],
            'technology and innovation': ['technology', 'platform', 'innovation', 'development', 'technical'],
            'market analysis': ['analysis', 'trend', 'outlook', 'forecast', 'prediction', 'metrics']
        }
        
        topic_scores = {}
        for topic, keywords in topics.items():
            score = sum(1 for keyword in keywords if keyword in words)
            if score > 1:  # Minimum threshold
                topic_scores[topic] = score
        
        # Return topics sorted by relevance
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, score in sorted_topics[:5]]
    
    def _extract_key_quotes(self, transcript: str) -> list[str]:
        """Extract meaningful quotes from transcript."""
        import re
        
        # Look for quoted text and impactful statements
        quotes = []
        
        # Find quoted content
        quoted_matches = re.findall(r'"([^"]{20,200})"', transcript)
        for match in quoted_matches[:10]:
            clean_match = match.strip()
            if len(clean_match) > 20:
                quotes.append(clean_match)
        
        # Find strong statements
        statement_patterns = [
            r'(?:I think|I believe|The key is|What\'s important|The reality is)\s+([^.!?]{20,150})',
            r'(?:You need to|You should|The way to)\s+([^.!?]{15,120})',
            r'(?:This is|That\'s)\s+(?:huge|important|critical|key)\s+([^.!?]{15,120})'
        ]
        
        for pattern in statement_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches[:5]:
                clean_match = match.strip()
                if len(clean_match) > 15 and clean_match not in quotes:
                    quotes.append(clean_match)
        
        return quotes[:6]
    
    def _extract_insights(self, transcript: str) -> list[str]:
        """Extract key insights from transcript."""
        import re
        
        insights = []
        
        insight_patterns = [
            r'(?:The key insight|What this means|The important thing|Here\'s what\'s interesting)\s+([^.!?]{20,150})',
            r'(?:What we\'re seeing|The trend|The shift|The change)\s+([^.!?]{20,150})',
            r'(?:The opportunity|The challenge|The problem)\s+(?:is|with|here)\s+([^.!?]{15,130})'
        ]
        
        for pattern in insight_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches[:8]:
                insight = match.strip()
                if len(insight) > 20:
                    insights.append(insight)
        
        return insights[:6]
    
    def _extract_takeaways(self, transcript: str) -> list[str]:
        """Extract actionable takeaways."""
        import re
        
        takeaways = []
        
        action_patterns = [
            r'(?:You should|I recommend|Try|Start|Focus on|Look at)\s+([^.!?]{10,120})',
            r'(?:The solution|The answer|The approach)\s+(?:is|would be)\s+([^.!?]{10,120})',
            r'(?:What works|What helps|What matters)\s+(?:is|most)\s+([^.!?]{10,120})'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches[:10]:
                takeaway = match.strip()
                if len(takeaway) > 10:
                    takeaways.append(takeaway)
        
        return takeaways[:5]
    
    async def _save_summary(self, summary: str, metadata: Dict[str, Any], args: Dict[str, Any]) -> Optional[str]:
        """Save summary to output file."""
        try:
            # Create output directory
            output_dir = args.get('output', 'podcast_summaries')
            Path(output_dir).mkdir(exist_ok=True)
            
            # Generate filename
            title = metadata.get('title', 'Unknown')
            # Clean title for filename
            clean_title = re.sub(r'[^\w\s-]', '', title)[:50]
            clean_title = re.sub(r'[-\s]+', '-', clean_title).strip('-')
            
            timestamp = datetime.now().strftime("%Y%m%d")
            template = args.get('template', 'blog')
            
            filename = f"{clean_title}-{template}-{timestamp}.md"
            output_path = Path(output_dir) / filename
            
            # Write summary
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            logger.info(f"Summary saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error saving summary: {str(e)}")
            return None
    
    def _format_duration(self, duration_seconds: Optional[int]) -> str:
        """Format duration in seconds to human-readable string."""
        if not duration_seconds:
            return "unknown duration"
        
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return f"{duration_seconds}s"


async def main():
    """Main entry point."""
    try:
        import re
        
        command = SummarizeCommand()
        
        # Parse command line arguments
        args = command.parse_command(sys.argv[1:])
        
        # Execute command
        success = await command.execute(args)
        
        if success:
            print("\n🎉 Summary completed successfully!")
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    import re
    asyncio.run(main())