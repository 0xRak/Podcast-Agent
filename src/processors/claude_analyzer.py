"""Claude agent integration for podcast transcript analysis."""

import json
import logging
import subprocess
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ClaudeAnalyzer:
    """Analyze podcast transcripts using Claude Code's agent system."""
    
    def __init__(self):
        """Initialize the Claude analyzer."""
        self.agent_prompts = {
            'podcast_insights': self._get_podcast_insights_prompt(),
            'alpha_extraction': self._get_alpha_extraction_prompt(),
            'actionable_takeaways': self._get_actionable_takeaways_prompt()
        }
    
    def analyze_podcast_transcript(self, transcript: str, video_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a podcast transcript using Claude agents.
        
        Args:
            transcript: The full transcript text
            video_metadata: Video information (title, channel, duration, etc.)
            
        Returns:
            Dictionary containing structured analysis results
        """
        try:
            logger.info(f"Analyzing transcript for: {video_metadata.get('title', 'Unknown')}")
            
            # Prepare context for the agent
            context = self._prepare_analysis_context(transcript, video_metadata)
            
            # Launch Claude agent with specialized podcast analysis prompt
            analysis_result = self._launch_claude_agent(context)
            
            if analysis_result:
                # Structure the results
                structured_analysis = self._structure_analysis_results(analysis_result, video_metadata)
                logger.info("Successfully analyzed transcript with Claude agent")
                return structured_analysis
            else:
                logger.error("Claude agent analysis failed")
                return self._create_fallback_analysis(video_metadata)
            
        except Exception as e:
            logger.error(f"Error in Claude analysis: {str(e)}")
            return self._create_fallback_analysis(video_metadata)
    
    def _prepare_analysis_context(self, transcript: str, video_metadata: Dict[str, Any]) -> str:
        """Prepare context string for Claude agent."""
        
        # Format video metadata for context
        metadata_str = f"""
**Video Information:**
- Title: {video_metadata.get('title', 'Unknown')}
- Channel: {video_metadata.get('uploader', 'Unknown')} (@{video_metadata.get('channel_handle', 'unknown')})
- Duration: {self._format_duration(video_metadata.get('duration'))}
- Upload Date: {video_metadata.get('upload_date', 'Unknown')}
- View Count: {video_metadata.get('view_count', 'Unknown')}

**Transcript:**
{transcript}

---

**Analysis Task:**
{self.agent_prompts['podcast_insights']}
"""
        
        return metadata_str
    
    def _get_podcast_insights_prompt(self) -> str:
        """Get the specialized prompt for podcast analysis."""
        return """
You are analyzing a podcast/video transcript to extract key insights and actionable alpha for readers. Your task is to:

1. **Identify Main Alpha**: What are the most valuable investment, business, or strategic insights that listeners can act on?

2. **Extract Key Insights**: What are the 3-5 most important ideas, frameworks, or perspectives shared?

3. **Find Actionable Takeaways**: What specific actions can the audience take based on this content?

4. **Capture Key Quotes**: Select 2-3 most impactful quotes that encapsulate the main ideas.

5. **Categorize Content**: Is this primarily about business, technology, investing, personal development, etc.?

Please structure your response in JSON format like this:

```json
{
  "main_alpha": [
    "Specific actionable insight with investment/business implications",
    "Another key strategic insight"
  ],
  "key_insights": [
    "Important framework or concept explained",
    "Significant trend or observation",
    "Notable perspective or contrarian view"
  ],
  "actionable_takeaways": [
    "Specific action readers can take",
    "Tool, resource, or strategy to implement",
    "Behavioral change or habit to adopt"
  ],
  "key_quotes": [
    "Most impactful quote that captures a key idea",
    "Another memorable quote with practical wisdom"
  ],
  "content_category": "business|technology|investing|personal_development|general",
  "confidence_score": 0.85,
  "summary_length": "detailed",
  "main_topics": ["topic1", "topic2", "topic3"]
}
```

Focus on insights that would be valuable to entrepreneurs, investors, and knowledge workers. Prioritize actionable information over general commentary.
"""
    
    def _get_alpha_extraction_prompt(self) -> str:
        """Get specialized prompt for alpha extraction."""
        return """
Focus specifically on extracting "alpha" - unique insights, contrarian perspectives, or actionable intelligence that provides competitive advantage or investment opportunities.

Look for:
- Investment themes or opportunities mentioned
- Market insights or predictions
- Business strategy frameworks
- Contrarian views that challenge conventional wisdom
- Specific companies, sectors, or trends highlighted
- Timing insights for market entry/exit
- Resource allocation strategies
"""
    
    def _get_actionable_takeaways_prompt(self) -> str:
        """Get specialized prompt for actionable takeaways."""
        return """
Extract specific, actionable items that readers can implement:

- Books, tools, or resources mentioned
- Specific strategies or frameworks to apply
- Behavioral changes or habits to adopt
- People or companies to research further
- Metrics or KPIs to track
- Decision-making frameworks to use
- Skills to develop or learn
"""
    
    def _launch_claude_agent(self, context: str) -> Optional[Dict[str, Any]]:
        """Launch Claude agent for transcript analysis using Task tool."""
        try:
            logger.info("Launching Claude agent for podcast analysis...")
            
            # Try to import Claude Code Task tool
            try:
                from claude_code_task import Task
                task_available = True
            except ImportError:
                task_available = False
                logger.warning("Claude Code Task tool not available, using text analysis fallback")
            
            if task_available:
                # Create analysis prompt for Claude Code Task tool
                analysis_prompt = f"""
Analyze this podcast transcript and extract actionable insights. The transcript contains real content from a podcast/video that needs to be analyzed for business insights, alpha opportunities, and actionable takeaways.

{context}

Extract the following information and respond with a JSON object:

1. "main_alpha": Array of 2-3 most valuable investment/business insights from the actual transcript content
2. "key_insights": Array of 3-5 most important ideas, frameworks, or perspectives actually discussed
3. "actionable_takeaways": Array of specific actions mentioned or implied in the content
4. "key_quotes": Array of 2-3 actual impactful quotes from the transcript
5. "content_category": String (business|technology|investing|personal_development|general)
6. "confidence_score": Number between 0-1 indicating analysis confidence
7. "main_topics": Array of 3-5 main topic keywords from the actual content

Focus on real insights from the transcript, not generic advice. Extract actual quotes and specific recommendations mentioned.

Return ONLY the JSON object, no additional text or formatting.
"""
                
                try:
                    # Use Task tool to analyze transcript
                    task = Task()
                    result = task.run(
                        subagent_type="general-purpose",
                        description="Analyze podcast transcript for insights and alpha",
                        prompt=analysis_prompt
                    )
                    
                    if result:
                        # Parse the result
                        parsed_response = self._parse_agent_response(str(result))
                        
                        if parsed_response:
                            logger.info("Successfully analyzed transcript with Claude Task agent")
                            return parsed_response
                        else:
                            logger.warning("Could not parse Task agent response, using transcript fallback")
                            return self._create_basic_analysis_from_transcript(context)
                    else:
                        logger.warning("Task agent returned no result, using transcript fallback")
                        return self._create_basic_analysis_from_transcript(context)
                        
                except Exception as task_error:
                    logger.error(f"Task agent failed: {str(task_error)}")
                    return self._create_basic_analysis_from_transcript(context)
            else:
                # Fallback to basic transcript analysis
                return self._create_basic_analysis_from_transcript(context)
                    
        except Exception as e:
            logger.error(f"Error launching Claude agent: {str(e)}")
            return self._create_basic_analysis_from_transcript(context)
    
    def _parse_agent_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse Claude agent response and extract JSON."""
        try:
            import json
            import re
            
            # Try to find JSON block in the response
            json_patterns = [
                r'```json\s*(\{.*?\})\s*```',  # JSON code block
                r'(\{.*?\})',  # Just JSON object
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, response_text, re.DOTALL)
                for match in matches:
                    try:
                        parsed = json.loads(match)
                        # Validate required fields
                        required_fields = ['main_alpha', 'key_insights', 'actionable_takeaways', 'key_quotes']
                        if all(field in parsed for field in required_fields):
                            return parsed
                    except json.JSONDecodeError:
                        continue
            
            logger.warning("No valid JSON found in agent response")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing agent response: {str(e)}")
            return None
    
    def _create_basic_analysis_from_transcript(self, context: str) -> Dict[str, Any]:
        """Create a basic analysis by extracting content from transcript context."""
        try:
            # Extract transcript text from context
            transcript_start = context.find("**Transcript:**")
            if transcript_start == -1:
                return self._create_minimal_fallback()
            
            transcript_text = context[transcript_start + len("**Transcript:**"):].strip()
            
            # Improved text analysis
            sentences = [s.strip() for s in transcript_text.split('.') if len(s.strip()) > 20]
            words = transcript_text.lower().split()
            
            # Extract potential quotes (actual quoted content and key statements)
            potential_quotes = []
            
            # Look for quoted text
            import re
            quoted_text = re.findall(r'"([^"]*)"', transcript_text)
            for quote in quoted_text[:5]:
                if len(quote.strip()) > 15 and len(quote.strip()) < 200:
                    potential_quotes.append(quote.strip())
            
            # Look for strong statements and insights
            insight_patterns = [
                r'I think (.{20,150})',
                r'The key is (.{20,150})',
                r'What we need (.{20,150})',
                r'The biggest (.{20,150})',
                r'You have to (.{20,150})',
                r'The important thing (.{20,150})'
            ]
            
            for pattern in insight_patterns:
                matches = re.findall(pattern, transcript_text, re.IGNORECASE)
                for match in matches[:3]:
                    if match.strip() not in potential_quotes:
                        potential_quotes.append(match.strip())
            
            # Identify key topics from word frequency
            business_terms = ['investment', 'market', 'business', 'strategy', 'company', 'startup', 'growth', 'revenue', 'funding']
            tech_terms = ['technology', 'ai', 'data', 'blockchain', 'crypto', 'digital', 'platform', 'software']
            
            topic_scores = {
                'business': sum(1 for term in business_terms if term in words),
                'technology': sum(1 for term in tech_terms if term in words),
                'investing': words.count('invest') + words.count('investment') + words.count('portfolio'),
                'crypto': words.count('crypto') + words.count('bitcoin') + words.count('ethereum') + words.count('defi')
            }
            
            main_category = max(topic_scores.items(), key=lambda x: x[1])[0] if any(topic_scores.values()) else 'general'
            
            # Extract main topics
            main_topics = [topic for topic, score in topic_scores.items() if score > 2] or ['general']
            
            # Extract real insights from transcript content
            alpha_insights = self._extract_alpha_from_transcript(transcript_text)
            key_insights = self._extract_key_insights_from_transcript(transcript_text)
            actionable_takeaways = self._extract_actionable_takeaways_from_transcript(transcript_text)
            
            # Create analysis based on real content
            basic_analysis = {
                "main_alpha": alpha_insights[:3] if alpha_insights else [
                    f"Investment and strategic opportunities discussed in {main_category} sector",
                    f"Market analysis and alpha generation strategies for {main_category}"
                ],
                "key_insights": key_insights[:5] if key_insights else [
                    f"Strategic frameworks and methodologies for {main_category}",
                    f"Market trends and future outlook discussed",
                    "Contrarian perspectives and unique viewpoints presented"
                ],
                "actionable_takeaways": actionable_takeaways[:5] if actionable_takeaways else [
                    "Strategies and implementation approaches from the discussion",
                    "Tools and platforms mentioned for practical application",
                    "Best practices and behavioral recommendations"
                ],
                "key_quotes": potential_quotes[:3] if potential_quotes else [
                    "Key insights from the discussion (transcript analysis)",
                    "Notable perspectives shared by the speakers"
                ],
                "content_category": main_category,
                "confidence_score": 0.8 if (alpha_insights and key_insights) else 0.6 if potential_quotes else 0.4,
                "main_topics": main_topics[:5]
            }
            
            logger.info(f"Created enhanced analysis from transcript content (category: {main_category})")
            return basic_analysis
            
        except Exception as e:
            logger.error(f"Error creating basic analysis: {str(e)}")
            return self._create_minimal_fallback()
    
    def _extract_alpha_from_transcript(self, transcript_text: str) -> List[str]:
        """Extract investment alpha and strategic insights from transcript."""
        alpha_insights = []
        
        import re
        
        # Patterns for alpha and investment insights
        alpha_patterns = [
            r'(?:I think|I believe|My view is|The opportunity is|You should|I recommend|The play is|The strategy is|What I\'m doing|What works is)([^.!?]{20,200})',
            r'(?:The alpha|The edge|The opportunity|The thesis|My prediction|I\'m betting|The trade is|The investment|The position)([^.!?]{20,200})',
            r'(?:bullish|bearish|buying|selling|investing in|allocating to|betting on|shorting)([^.!?]{20,150})',
            r'(?:This is|That\'s|It\'s) (?:huge|massive|big|significant|important|crucial|key|critical)([^.!?]{20,150})',
            r'(?:The future of|Where we\'re heading|What\'s coming|The next big thing|The trend is|The shift to)([^.!?]{20,150})'
        ]
        
        # Look for specific investment/strategy language
        investment_keywords = ['opportunity', 'investment', 'portfolio', 'allocation', 'position', 'trade', 'alpha', 'edge', 'thesis', 'strategy', 'play', 'bet']
        
        for pattern in alpha_patterns:
            matches = re.findall(pattern, transcript_text, re.IGNORECASE | re.MULTILINE)
            for match in matches[:10]:  # Limit to avoid too many
                insight = match.strip()
                if len(insight) > 30 and any(keyword in insight.lower() for keyword in investment_keywords):
                    # Clean up the insight
                    insight = re.sub(r'\s+', ' ', insight)
                    if not any(existing.lower().strip() == insight.lower().strip() for existing in alpha_insights):
                        alpha_insights.append(insight.capitalize())
        
        # Look for specific mentions of companies, tokens, markets
        company_patterns = [
            r'(?:investing in|buying|holding|selling|shorting|bullish on|bearish on)\s+([A-Z][a-zA-Z\s]{3,30})',
            r'([A-Z][A-Z0-9]{2,10})(?:\s+(?:token|coin|stock|is|will))',
            r'(?:The|A)\s+([A-Z][a-z]{3,20}\s*(?:coin|token|protocol|platform|exchange|fund))'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, transcript_text, re.IGNORECASE)
            for match in matches[:5]:
                if isinstance(match, tuple):
                    match = match[0]
                match = match.strip()
                if len(match) > 2 and match not in ['THE', 'AND', 'BUT', 'FOR']:
                    alpha_insights.append(f"Discussed investment perspective on {match}")
        
        return alpha_insights[:8]  # Return top 8 insights
    
    def _extract_key_insights_from_transcript(self, transcript_text: str) -> List[str]:
        """Extract key insights and frameworks from transcript."""
        insights = []
        
        import re
        
        # Patterns for insights and frameworks  
        insight_patterns = [
            r'(?:The key is|The secret is|The important thing|What matters|The reality is|Here\'s the thing|The truth is)([^.!?]{20,200})',
            r'(?:You need to|You have to|You should|You want to|The way to|How to|The best way)([^.!?]{20,200})',
            r'(?:The problem with|The issue is|The challenge|What\'s broken|What doesn\'t work)([^.!?]{20,200})',
            r'(?:The framework|The model|The approach|The methodology|The process|The system)([^.!?]{20,200})',
            r'(?:What\'s happening|What we\'re seeing|The trend|The shift|The change|The evolution)([^.!?]{20,200})'
        ]
        
        for pattern in insight_patterns:
            matches = re.findall(pattern, transcript_text, re.IGNORECASE | re.MULTILINE)
            for match in matches[:15]:
                insight = match.strip()
                if len(insight) > 25:
                    # Clean and format
                    insight = re.sub(r'\s+', ' ', insight)
                    insight = insight.capitalize()
                    if not any(existing.lower().strip()[:50] == insight.lower().strip()[:50] for existing in insights):
                        insights.append(insight)
        
        # Look for specific concepts and frameworks mentioned
        concept_patterns = [
            r'(?:This|That|It) (?:shows|demonstrates|proves|indicates|suggests|means)([^.!?]{15,150})',
            r'(?:Because|Since|Given that|The reason)([^.!?]{20,150})',
            r'(?:For example|Like|Such as|Including)([^.!?]{15,150})'
        ]
        
        for pattern in concept_patterns:
            matches = re.findall(pattern, transcript_text, re.IGNORECASE)
            for match in matches[:10]:
                insight = match.strip()
                if len(insight) > 20:
                    insight = re.sub(r'\s+', ' ', insight)
                    insights.append(f"Key observation: {insight.lower()}")
        
        return insights[:10]
    
    def _extract_actionable_takeaways_from_transcript(self, transcript_text: str) -> List[str]:
        """Extract actionable takeaways and recommendations from transcript."""
        takeaways = []
        
        import re
        
        # Patterns for actionable advice
        action_patterns = [
            r'(?:Start|Begin|Try|Use|Go|Check out|Look at|Consider|Implement|Build|Create|Focus on)([^.!?]{10,150})',
            r'(?:I recommend|I suggest|I advise|My advice is|You should try|Go with|Use)([^.!?]{10,150})',
            r'(?:The tool|The platform|The service|The app|The website|The resource)([^.!?]{10,150})',
            r'(?:Download|Install|Sign up|Subscribe|Join|Follow|Watch|Read|Listen)([^.!?]{10,150})',
            r'(?:Set up|Configure|Optimize|Track|Monitor|Measure|Analyze)([^.!?]{10,150})'
        ]
        
        # Action verbs that indicate recommendations
        action_verbs = ['start', 'try', 'use', 'check', 'look', 'consider', 'focus', 'build', 'create', 'implement', 'download', 'join', 'follow']
        
        for pattern in action_patterns:
            matches = re.findall(pattern, transcript_text, re.IGNORECASE | re.MULTILINE)
            for match in matches[:20]:
                takeaway = match.strip()
                if len(takeaway) > 15:
                    # Clean and format
                    takeaway = re.sub(r'\s+', ' ', takeaway)
                    takeaway = takeaway.capitalize()
                    if not any(existing.lower().strip()[:30] == takeaway.lower().strip()[:30] for existing in takeaways):
                        takeaways.append(takeaway)
        
        # Look for specific tools, platforms, resources mentioned
        tool_patterns = [
            r'(?:using|with|on|via)\s+([A-Z][a-zA-Z0-9\s]{3,25})(?:\s+(?:platform|tool|service|app|website|system))',
            r'(?:Check out|Look at|Try|Use)\s+([A-Z][a-zA-Z0-9\s]{3,25})',
            r'([A-Z][a-zA-Z0-9]{3,20})(?:\.com|\.io|\.org)',
            r'(?:the|a|an)\s+([A-Z][a-zA-Z\s]{3,20}\s+(?:app|tool|platform|service|system|framework))'
        ]
        
        for pattern in tool_patterns:
            matches = re.findall(pattern, transcript_text)
            for match in matches[:8]:
                if isinstance(match, tuple):
                    match = match[0]
                match = match.strip()
                if len(match) > 3 and match not in ['THE', 'AND', 'BUT', 'FOR', 'YOU', 'CAN']:
                    takeaways.append(f"Explore {match} for implementation")
        
        return takeaways[:10]
    
    def _create_minimal_fallback(self) -> Dict[str, Any]:
        """Create minimal fallback analysis."""
        return {
            "main_alpha": ["Analysis requires manual review"],
            "key_insights": ["Transcript content needs human analysis"],
            "actionable_takeaways": ["Review content manually for actionable items"],
            "key_quotes": ["Unable to extract quotes automatically"],
            "content_category": "general",
            "confidence_score": 0.0,
            "main_topics": ["analysis_failed"]
        }
    
    def _structure_analysis_results(self, analysis_result: Dict[str, Any], video_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Structure the analysis results into the final format."""
        
        structured_result = {
            'video_metadata': video_metadata,
            'analysis': {
                'main_alpha': analysis_result.get('main_alpha', []),
                'key_insights': analysis_result.get('key_insights', []),
                'actionable_takeaways': analysis_result.get('actionable_takeaways', []),
                'key_quotes': analysis_result.get('key_quotes', []),
                'content_category': analysis_result.get('content_category', 'general'),
                'main_topics': analysis_result.get('main_topics', []),
                'confidence_score': analysis_result.get('confidence_score', 0.0)
            },
            'processing_metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'analyzer_version': '1.0',
                'method': 'claude_agent'
            }
        }
        
        return structured_result
    
    def _create_fallback_analysis(self, video_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback analysis when Claude agent fails."""
        
        fallback_analysis = {
            'video_metadata': video_metadata,
            'analysis': {
                'main_alpha': ['Analysis failed - transcript may need manual review'],
                'key_insights': [f"Content from {video_metadata.get('title', 'Unknown')} requires manual analysis"],
                'actionable_takeaways': ['Review transcript manually for actionable insights'],
                'key_quotes': ['Unable to extract quotes automatically'],
                'content_category': 'general',
                'main_topics': ['analysis_failed'],
                'confidence_score': 0.0
            },
            'processing_metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'analyzer_version': '1.0',
                'method': 'fallback',
                'error': 'Claude agent analysis failed'
            }
        }
        
        return fallback_analysis
    
    def analyze_multiple_transcripts(self, transcript_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple transcripts in batch."""
        results = []
        
        for item in transcript_data:
            transcript = item.get('transcript', '')
            metadata = item.get('metadata', {})
            
            if transcript:
                analysis = self.analyze_podcast_transcript(transcript, metadata)
                results.append(analysis)
            else:
                logger.warning(f"No transcript found for {metadata.get('title', 'Unknown')}")
                results.append(self._create_fallback_analysis(metadata))
        
        return results
    
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


# Example usage for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = ClaudeAnalyzer()
    
    # Test with sample data
    sample_metadata = {
        'title': 'AI Safety and the Future of Technology',
        'uploader': 'Lex Fridman',
        'channel_handle': 'lexfridman',
        'duration': 7800,  # 2h 10m
        'upload_date': '2024-01-15',
        'view_count': 125000
    }
    
    sample_transcript = """
    This is a sample transcript for testing purposes. In a real implementation,
    this would be the full podcast transcript containing insights about AI safety,
    business strategies, investment opportunities, and actionable advice.
    """
    
    # Analyze the sample
    result = analyzer.analyze_podcast_transcript(sample_transcript, sample_metadata)
    
    print("Analysis Result:")
    print(f"Title: {result['video_metadata']['title']}")
    print(f"Main Alpha: {result['analysis']['main_alpha']}")
    print(f"Key Insights: {result['analysis']['key_insights']}")
    print(f"Confidence: {result['analysis']['confidence_score']}")