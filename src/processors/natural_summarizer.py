"""Natural language podcast summarizer using Claude agent."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class NaturalSummarizer:
    """Create natural, blog-style podcast summaries using Claude agent."""
    
    def __init__(self):
        """Initialize the natural summarizer."""
        pass
    
    def create_summary(self, video_metadata: Dict[str, Any], transcript: str) -> str:
        """
        Create a natural language summary of the podcast transcript.
        
        Args:
            video_metadata: Video information (title, channel, etc.)
            transcript: Full transcript text
            
        Returns:
            Natural language summary in blog post format
        """
        try:
            logger.info(f"Creating natural summary for: {video_metadata.get('title', 'Unknown')}")
            
            # Prepare context for summarization
            context = self._prepare_summarization_context(video_metadata, transcript)
            
            # Try to use Claude agent for natural summarization
            summary = self._generate_natural_summary(context, video_metadata)
            
            if summary:
                logger.info("Successfully generated natural summary")
                return summary
            else:
                logger.warning("Claude agent failed, creating basic summary")
                return self._create_basic_summary(video_metadata, transcript)
                
        except Exception as e:
            logger.error(f"Error creating summary: {str(e)}")
            return self._create_fallback_summary(video_metadata)
    
    def _prepare_summarization_context(self, video_metadata: Dict[str, Any], transcript: str) -> str:
        """Prepare context for Claude agent summarization."""
        
        title = video_metadata.get('title', 'Unknown Title')
        channel = video_metadata.get('uploader', 'Unknown Channel')
        channel_handle = video_metadata.get('channel_handle', 'unknown')
        duration = self._format_duration(video_metadata.get('duration'))
        upload_date = video_metadata.get('upload_date', 'Unknown Date')
        
        # Format the context
        context = f"""
**Podcast Information:**
- Title: {title}
- Channel: {channel} (@{channel_handle})
- Duration: {duration}
- Published: {upload_date}

**Full Transcript:**
{transcript}

**Task:**
Create a natural, engaging summary of this podcast in blog post format. Focus on:

1. The most interesting and relevant insights shared
2. Actionable advice that listeners can implement
3. Notable perspectives or contrarian views
4. Key takeaways that provide genuine value

Write in a natural, flowing style - like a well-written blog post or article. No bullet points or rigid structure. The length should be proportional to how much valuable content is in the transcript.

Make it engaging and informative, highlighting what makes this content worth the listener's time.
"""
        
        return context
    
    def _generate_natural_summary(self, context: str, video_metadata: Dict[str, Any]) -> Optional[str]:
        """Generate natural summary using Claude agent."""
        try:
            # Try to import and use Claude Code Task tool
            try:
                from claude_code_task import Task
                task_available = True
            except ImportError:
                task_available = False
                logger.info("Claude Code Task tool not available, using fallback")
            
            if task_available:
                try:
                    # Use Task tool for natural summarization
                    task = Task()
                    result = task.run(
                        subagent_type="general-purpose",
                        description="Create natural blog-style podcast summary",
                        prompt=context
                    )
                    
                    if result and isinstance(result, str) and len(result.strip()) > 100:
                        return result.strip()
                    else:
                        logger.warning("Task agent returned insufficient content")
                        return None
                        
                except Exception as task_error:
                    logger.error(f"Task agent failed: {str(task_error)}")
                    return None
            
            # If Task tool not available, return None to trigger fallback
            return None
            
        except Exception as e:
            logger.error(f"Error in natural summary generation: {str(e)}")
            return None
    
    def _create_basic_summary(self, video_metadata: Dict[str, Any], transcript: str) -> str:
        """Create a basic summary using text analysis when Claude agent is unavailable."""
        
        title = video_metadata.get('title', 'Unknown Title')
        channel = video_metadata.get('uploader', 'Unknown Channel')
        duration = self._format_duration(video_metadata.get('duration'))
        
        # Extract key elements from transcript
        key_topics = self._extract_main_topics(transcript)
        interesting_quotes = self._extract_interesting_quotes(transcript)
        main_themes = self._identify_main_themes(transcript)
        
        # Create natural summary
        summary = f"""# {title}

In this {duration} episode from {channel}, the discussion centers around {', '.join(main_themes[:3])}.

"""
        
        # Add main content based on what we found
        if key_topics:
            summary += f"The conversation covers {', '.join(key_topics[:4])}, providing insights into these important areas.\n\n"
        
        if interesting_quotes:
            summary += "Some notable points from the discussion:\n\n"
            for quote in interesting_quotes[:3]:
                summary += f'"{quote}"\n\n'
        
        # Add a conclusion
        summary += f"This episode offers valuable perspectives on {main_themes[0] if main_themes else 'the topic'}, "
        summary += "making it worth listening to for anyone interested in these areas."
        
        return summary
    
    def _extract_main_topics(self, transcript: str) -> list[str]:
        """Extract main topics discussed in the transcript."""
        import re
        
        # Common topic indicators
        topic_patterns = [
            r'(?:talking about|discussing|focusing on|looking at)\s+([a-z][a-z\s]{10,50})',
            r'(?:the topic of|the subject of|when it comes to)\s+([a-z][a-z\s]{10,50})',
            r'(?:in terms of|regarding|concerning)\s+([a-z][a-z\s]{10,50})'
        ]
        
        topics = []
        for pattern in topic_patterns:
            matches = re.findall(pattern, transcript.lower(), re.IGNORECASE)
            for match in matches[:10]:
                topic = match.strip()
                if len(topic) > 5 and topic not in topics:
                    topics.append(topic)
        
        return topics[:8]
    
    def _extract_interesting_quotes(self, transcript: str) -> list[str]:
        """Extract interesting quotes from the transcript."""
        import re
        
        # Look for quoted text and strong statements
        quote_patterns = [
            r'"([^"]{30,200})"',  # Quoted text
            r'(?:I think|I believe|My view is|The key is)\s+([^.!?]{30,150})',
            r'(?:What\'s interesting|What\'s important|The reality is)\s+([^.!?]{30,150})'
        ]
        
        quotes = []
        for pattern in quote_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches[:15]:
                quote = match.strip()
                if len(quote) > 25 and quote not in quotes:
                    # Clean up the quote
                    quote = re.sub(r'\s+', ' ', quote)
                    quotes.append(quote)
        
        return quotes[:6]
    
    def _identify_main_themes(self, transcript: str) -> list[str]:
        """Identify main themes from transcript content."""
        words = transcript.lower().split()
        
        # Theme categories with keywords
        themes = {
            'business and entrepreneurship': ['business', 'startup', 'entrepreneur', 'company', 'revenue', 'growth'],
            'technology and innovation': ['technology', 'ai', 'innovation', 'digital', 'platform', 'software'],
            'investing and finance': ['investment', 'portfolio', 'market', 'trading', 'finance', 'money'],
            'cryptocurrency and blockchain': ['crypto', 'bitcoin', 'ethereum', 'blockchain', 'defi', 'token'],
            'personal development': ['success', 'mindset', 'habits', 'productivity', 'learning', 'growth'],
            'strategy and frameworks': ['strategy', 'framework', 'approach', 'methodology', 'process', 'system']
        }
        
        theme_scores = {}
        for theme, keywords in themes.items():
            score = sum(1 for keyword in keywords if keyword in words)
            if score > 0:
                theme_scores[theme] = score
        
        # Return themes sorted by relevance
        sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, score in sorted_themes if score >= 2]
    
    def _create_fallback_summary(self, video_metadata: Dict[str, Any]) -> str:
        """Create minimal fallback summary when analysis fails."""
        
        title = video_metadata.get('title', 'Unknown Title')
        channel = video_metadata.get('uploader', 'Unknown Channel')
        duration = self._format_duration(video_metadata.get('duration'))
        
        return f"""# {title}

This {duration} episode from {channel} contains valuable insights and discussion. The transcript has been successfully extracted and is available for review.

Due to processing limitations, a detailed summary could not be automatically generated. However, the full transcript is preserved and can be manually reviewed for key insights and takeaways.

The content appears to cover topics relevant to the channel's focus area and may contain actionable advice and interesting perspectives worth exploring.
"""
    
    def _format_duration(self, duration_seconds: Optional[int]) -> str:
        """Format duration in seconds to human-readable string."""
        if not duration_seconds:
            return "unknown duration"
        
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return f"{seconds}s"


# Example usage for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    summarizer = NaturalSummarizer()
    
    # Test with sample data
    sample_metadata = {
        'title': 'Building Successful Startups: Lessons from Silicon Valley',
        'uploader': 'Entrepreneurship Podcast',
        'channel_handle': 'entrepreneurpod',
        'duration': 3600,  # 1 hour
        'upload_date': '2024-01-15'
    }
    
    sample_transcript = """
    Welcome to today's episode where we discuss the key strategies for building 
    successful startups. I think the most important thing entrepreneurs need to 
    understand is product-market fit. "You can have the best product in the world, 
    but if there's no market for it, you'll fail," says our guest.
    
    The reality is that most startups fail because they build something nobody wants. 
    What's interesting is that successful founders often pivot multiple times before 
    finding their sweet spot. The key is to listen to your customers and iterate quickly.
    
    When it comes to funding, timing is everything. You need to raise money when 
    you're strong, not when you're desperate. The best approach is to build 
    relationships with investors long before you need their money.
    """
    
    # Generate summary
    summary = summarizer.create_summary(sample_metadata, sample_transcript)
    
    print("Generated Summary:")
    print("=" * 50)
    print(summary)