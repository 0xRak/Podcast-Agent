"""Insight formatter for generating structured markdown output."""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class InsightFormatter:
    """Format podcast analysis results into structured markdown output."""
    
    def __init__(self, output_dir: str = "podcast_summaries"):
        """Initialize the insight formatter."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def format_podcast_summary(self, analyses: List[Dict[str, Any]], 
                             output_filename: Optional[str] = None) -> str:
        """
        Format multiple podcast analyses into a comprehensive summary.
        
        Args:
            analyses: List of analysis dictionaries from Claude analyzer
            output_filename: Custom output filename (optional)
            
        Returns:
            Path to the generated markdown file
        """
        try:
            if not analyses:
                logger.warning("No analyses provided for formatting")
                return ""
            
            # Generate filename if not provided
            if not output_filename:
                timestamp = datetime.now().strftime("%Y-%m-%d")
                output_filename = f"youtube-research-{timestamp}.md"
            
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Generate markdown content
            markdown_content = self._generate_markdown_content(analyses)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(markdown_content)
            
            logger.info(f"Generated podcast summary: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error formatting podcast summary: {str(e)}")
            return ""
    
    def _generate_markdown_content(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate the complete markdown content."""
        
        # Header section
        header = self._generate_header(analyses)
        
        # Processing status section
        status = self._generate_processing_status(analyses)
        
        # Main insights section
        insights = self._generate_insights_section(analyses)
        
        # Summary statistics
        stats = self._generate_summary_statistics(analyses)
        
        # Combine all sections
        content = f"{header}\n\n{status}\n\n---\n\n{insights}\n\n---\n\n{stats}"
        
        return content
    
    def _generate_header(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate the header section."""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        channels_count = len(analyses)
        videos_count = sum(1 for analysis in analyses if analysis.get('analysis', {}).get('confidence_score', 0) > 0)
        
        header = f"""# Podcast Research Summary
**Generated:** {timestamp}  
**Channels Processed:** {channels_count}  
**Videos Analyzed:** {videos_count}"""
        
        return header
    
    def _generate_processing_status(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate the processing status checklist."""
        
        status_lines = ["## Processing Status"]
        
        for analysis in analyses:
            metadata = analysis.get('video_metadata', {})
            analysis_data = analysis.get('analysis', {})
            
            channel_handle = metadata.get('channel_handle', 'unknown')
            title = metadata.get('title', 'Unknown Title')
            upload_date = metadata.get('upload_date', 'Unknown Date')
            confidence = analysis_data.get('confidence_score', 0)
            
            # Format upload date
            formatted_date = self._format_upload_date(upload_date)
            
            # Determine status icon
            status_icon = "✓" if confidence > 0.5 else "⚠️" if confidence > 0 else "❌"
            
            status_line = f"- [x] **@{channel_handle}** - \"{title}\" ({formatted_date}) {status_icon}"
            status_lines.append(status_line)
        
        return "\n".join(status_lines)
    
    def _generate_insights_section(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate the main insights section."""
        
        insights_sections = ["## 🎯 Key Insights & Alpha"]
        
        for analysis in analyses:
            metadata = analysis.get('video_metadata', {})
            analysis_data = analysis.get('analysis', {})
            
            # Skip failed analyses
            if analysis_data.get('confidence_score', 0) <= 0:
                continue
            
            section = self._format_individual_podcast_insights(metadata, analysis_data)
            insights_sections.append(section)
        
        return "\n\n".join(insights_sections)
    
    def _format_individual_podcast_insights(self, metadata: Dict[str, Any], 
                                          analysis: Dict[str, Any]) -> str:
        """Format insights for a single podcast."""
        
        channel_handle = metadata.get('channel_handle', 'unknown')
        title = metadata.get('title', 'Unknown Title')
        duration = self._format_duration(metadata.get('duration'))
        upload_date = self._format_upload_date(metadata.get('upload_date'))
        
        # Build the section
        section_lines = [
            f"### @{channel_handle} - \"{title}\"",
            f"**Duration:** {duration} | **Published:** {upload_date}",
            ""
        ]
        
        # Main Alpha section
        main_alpha = analysis.get('main_alpha', [])
        if main_alpha:
            section_lines.extend([
                "#### 🔥 Main Alpha",
                *[f"- **{item.strip()}**" for item in main_alpha[:3]],  # Limit to top 3
                ""
            ])
        
        # Key Insights section
        key_insights = analysis.get('key_insights', [])
        if key_insights:
            section_lines.extend([
                "#### 💡 Key Insights"
            ])
            
            for i, insight in enumerate(key_insights[:5], 1):  # Limit to top 5
                section_lines.append(f"{i}. **{insight.strip()}**")
            
            section_lines.append("")
        
        # Key Quotes section
        key_quotes = analysis.get('key_quotes', [])
        if key_quotes:
            section_lines.extend([
                "#### 📝 Key Quotes"
            ])
            
            for quote in key_quotes[:3]:  # Limit to top 3
                section_lines.append(f'> "{quote.strip()}"')
            
            section_lines.append("")
        
        # Actionable Takeaways section
        takeaways = analysis.get('actionable_takeaways', [])
        if takeaways:
            section_lines.extend([
                "#### 🚀 Actionable Takeaways"
            ])
            
            for takeaway in takeaways[:5]:  # Limit to top 5
                section_lines.append(f"- {takeaway.strip()}")
            
            section_lines.append("")
        
        # Main Topics
        topics = analysis.get('main_topics', [])
        if topics:
            topics_str = " • ".join(topics[:5])
            section_lines.extend([
                f"**Topics:** {topics_str}",
                ""
            ])
        
        return "\n".join(section_lines)
    
    def _generate_summary_statistics(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate summary statistics section."""
        
        # Calculate statistics
        total_duration = 0
        successful_analyses = 0
        total_insights = 0
        total_alpha = 0
        total_takeaways = 0
        
        for analysis in analyses:
            metadata = analysis.get('video_metadata', {})
            analysis_data = analysis.get('analysis', {})
            
            if metadata.get('duration'):
                total_duration += metadata['duration']
            
            if analysis_data.get('confidence_score', 0) > 0:
                successful_analyses += 1
                total_insights += len(analysis_data.get('key_insights', []))
                total_alpha += len(analysis_data.get('main_alpha', []))
                total_takeaways += len(analysis_data.get('actionable_takeaways', []))
        
        # Format duration
        formatted_duration = self._format_duration(total_duration)
        
        # Calculate transcript quality percentage
        transcript_quality = (successful_analyses / len(analyses) * 100) if analyses else 0
        
        stats_content = f"""## 📊 Summary Statistics
- **Total Content Analyzed:** {formatted_duration}
- **Key Insights Extracted:** {total_insights}
- **Actionable Alpha Points:** {total_alpha}
- **Takeaways Identified:** {total_takeaways}
- **Success Rate:** {successful_analyses}/{len(analyses)} videos ({transcript_quality:.0f}%)
- **Generated:** {datetime.now().strftime("%Y-%m-%d at %H:%M UTC")}"""
        
        return stats_content
    
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
    
    def _format_upload_date(self, date_string: Optional[str]) -> str:
        """Format upload date string."""
        if not date_string:
            return "Unknown Date"
        
        try:
            # Try parsing ISO format
            if 'T' in date_string:
                date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                return date_obj.strftime("%b %d, %Y")
            
            # Try parsing YYYY-MM-DD format
            if len(date_string) == 10 and date_string.count('-') == 2:
                date_obj = datetime.strptime(date_string, "%Y-%m-%d")
                return date_obj.strftime("%b %d, %Y")
            
            # Try parsing YYYYMMDD format
            if len(date_string) == 8 and date_string.isdigit():
                date_obj = datetime.strptime(date_string, "%Y%m%d")
                return date_obj.strftime("%b %d, %Y")
            
            return date_string  # Return as-is if can't parse
            
        except Exception:
            return date_string or "Unknown Date"
    
    def generate_quick_summary(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate a quick text summary for command-line display."""
        
        if not analyses:
            return "No analyses to summarize."
        
        successful = sum(1 for a in analyses if a.get('analysis', {}).get('confidence_score', 0) > 0)
        total_alpha = sum(len(a.get('analysis', {}).get('main_alpha', [])) for a in analyses)
        total_insights = sum(len(a.get('analysis', {}).get('key_insights', [])) for a in analyses)
        
        summary = f"""
📊 Processing Complete:
   • {successful}/{len(analyses)} videos analyzed successfully
   • {total_alpha} alpha insights extracted
   • {total_insights} key insights identified
   
📁 Output saved to: {self.output_dir}/
        """.strip()
        
        return summary
    
    def create_channel_specific_summary(self, analysis: Dict[str, Any], 
                                       output_filename: Optional[str] = None) -> str:
        """Create a summary file for a single channel/video."""
        
        try:
            if not output_filename:
                channel = analysis.get('video_metadata', {}).get('channel_handle', 'unknown')
                timestamp = datetime.now().strftime("%Y-%m-%d")
                output_filename = f"{channel}-summary-{timestamp}.md"
            
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Generate single-video markdown content
            metadata = analysis.get('video_metadata', {})
            analysis_data = analysis.get('analysis', {})
            
            content = f"""# {metadata.get('title', 'Podcast Summary')}

**Channel:** @{metadata.get('channel_handle', 'unknown')}  
**Duration:** {self._format_duration(metadata.get('duration'))}  
**Published:** {self._format_upload_date(metadata.get('upload_date'))}  
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}

---

{self._format_individual_podcast_insights(metadata, analysis_data)}

---

**Analysis Confidence:** {analysis_data.get('confidence_score', 0):.2f}  
**Content Category:** {analysis_data.get('content_category', 'general')}
"""
            
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            logger.info(f"Generated channel-specific summary: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating channel-specific summary: {str(e)}")
            return ""


# Example usage for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    formatter = InsightFormatter()
    
    # Test with sample analysis data
    sample_analyses = [
        {
            'video_metadata': {
                'title': 'AI Safety and the Future of Technology',
                'uploader': 'Lex Fridman',
                'channel_handle': 'lexfridman',
                'duration': 7800,
                'upload_date': '2024-01-15T00:00:00Z',
                'view_count': 125000
            },
            'analysis': {
                'main_alpha': [
                    'AI alignment companies will be critical investments as AI scales',
                    'Regulatory catalysts expected in AI safety space by 2025'
                ],
                'key_insights': [
                    'The biggest risk is AI achieving wrong objectives, not malicious AI',
                    'Current AI safety research is underfunded 100:1 vs capabilities',
                    'Constitutional AI shows promise but insufficient for AGI'
                ],
                'actionable_takeaways': [
                    'Monitor AI safety startups like Anthropic',
                    'Consider ESG implications in AI investments',
                    'Watch for regulatory developments'
                ],
                'key_quotes': [
                    'The biggest risk is not that AI becomes malicious, but that it becomes very capable at achieving the wrong objective'
                ],
                'content_category': 'technology',
                'main_topics': ['ai_safety', 'regulation', 'investing'],
                'confidence_score': 0.92
            }
        }
    ]
    
    # Generate summary
    output_path = formatter.format_podcast_summary(sample_analyses)
    print(f"Generated summary: {output_path}")
    
    # Generate quick summary
    quick_summary = formatter.generate_quick_summary(sample_analyses)
    print(quick_summary)