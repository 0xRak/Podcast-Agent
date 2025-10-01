# Podcast Summary Slash Command Specification

## Overview

The `/podcast_summary` command is a custom slash command that fetches the latest podcasts from specified YouTube channels, extracts transcripts, and generates structured summaries focused on key insights and actionable alpha for readers.

## Command Interface

### Basic Syntax
```bash
/podcast_summary @channel1 @channel2 @channel3
```

### Supported Flags
- `--days=N` : Only process videos published in the last N days (default: 7)
- `--limit=N` : Maximum number of videos per channel (default: 1)
- `--pdf` : Generate PDF output in addition to markdown
- `--config=path` : Use custom channel configuration file
- `--output=path` : Specify custom output directory (default: `podcast_summaries/`)

### Examples
```bash
# Basic usage - latest video from each channel
/podcast_summary @lexfridman @joerogan @naval

# Last 3 videos from past 14 days
/podcast_summary @lexfridman --days=14 --limit=3

# Generate PDF and use custom config
/podcast_summary @allinchamath @davidperell --pdf --config=my_channels.yaml
```

## Technical Architecture

### Core Dependencies (Free)
- **youtube-transcript-api**: Direct transcript extraction from YouTube
- **yt-dlp**: Video metadata extraction (title, date, channel info)
- **pdfkit + wkhtmltopdf**: PDF generation (adapted from AgenticResearch)
- **requests + BeautifulSoup**: Fallback transcript scraping if needed
- **pyyaml**: Configuration file handling

### AI Integration
- **Claude Code Agent System**: Leverages existing Claude agents for high-quality summarization
- **Specialized Prompts**: Custom prompts designed for podcast/video content analysis
- **Context Management**: Handles long transcripts through intelligent chunking

### Data Flow
1. **Input Processing**: Parse channel handles and flags
2. **Channel Discovery**: Use yt-dlp to get latest video URLs and metadata
3. **Transcript Extraction**: Primary via youtube-transcript-api, fallback to web scraping
4. **AI Analysis**: Launch Claude agents with specialized podcast analysis prompts
5. **Output Generation**: Create structured markdown with insights and alpha
6. **Optional PDF**: Convert to PDF using AgenticResearch's proven pipeline

## File Structure

```
Podcast Morning Feed/
├── spec/
│   └── podcast-summary-spec.md        # This specification
├── src/
│   ├── podcast_summary.py             # Main command implementation
│   ├── extractors/
│   │   ├── youtube_extractor.py       # yt-dlp wrapper
│   │   ├── transcript_fetcher.py      # youtube-transcript-api + fallbacks
│   │   └── metadata_parser.py         # Video info processing
│   ├── processors/
│   │   ├── claude_analyzer.py         # Claude agent integration
│   │   ├── content_chunker.py         # Long transcript handling
│   │   └── insight_formatter.py      # Markdown structure generation
│   ├── utils/
│   │   ├── config_manager.py          # Channel configuration
│   │   ├── file_organizer.py          # Output management
│   │   └── progress_tracker.py        # Status reporting
│   └── converters/
│       └── md_to_pdf.py              # PDF generation (from AgenticResearch)
├── podcast_summaries/                 # Generated outputs
│   └── youtube-research-YYYY-MM-DD.md
├── config/
│   ├── channels.yaml                  # Default channel configurations
│   └── settings.yaml                  # Global preferences
└── requirements.txt                   # Python dependencies
```

## Output Format

### Primary Output: `podcast_summaries/youtube-research-YYYY-MM-DD.md`

```markdown
# Podcast Research Summary
**Generated:** 2024-01-15 14:30 UTC  
**Channels Processed:** 3  
**Videos Analyzed:** 3  

## Processing Status
- [x] **@lexfridman** - "AI Safety with Stuart Russell" (Jan 14, 2024) ✓
- [x] **@joerogan** - "#2079 - Naval Ravikant Returns" (Jan 13, 2024) ✓  
- [x] **@allinchamath** - "Market Outlook 2024" (Jan 12, 2024) ✓

---

## 🎯 Key Insights & Alpha

### @lexfridman - "AI Safety with Stuart Russell" 
**Duration:** 2h 15m | **Published:** Jan 14, 2024

#### 🔥 Main Alpha
- **AI Control Problem**: Russell argues the biggest risk isn't malicious AI but incompetent AI systems pursuing misaligned objectives
- **Investment Thesis**: Companies solving AI alignment (constitutional AI, RLHF) will be critical as AI scales
- **Regulatory Timeline**: Expect significant AI safety regulations by 2025-2026

#### 💡 Key Insights
1. **"The biggest risk is not that AI becomes malicious, but that it becomes very capable at achieving the wrong objective"**
2. Current AI safety research is underfunded relative to AI capabilities research (1:100 ratio)
3. Constitutional AI and RLHF are promising but insufficient for AGI-level systems

#### 🚀 Actionable Takeaways
- Monitor AI safety startups (Anthropic, Constitutional AI, Alignment Research)
- Consider ESG implications of AI investments
- Watch for regulatory catalysts in AI safety space

---

### @joerogan - "#2079 - Naval Ravikant Returns"
**Duration:** 3h 5m | **Published:** Jan 13, 2024

#### 🔥 Main Alpha
- **Wealth Creation Framework**: "Wealth is assets that earn while you sleep" - focus on building systems, not trading time
- **Crypto Perspective**: Bitcoin remains digital gold, but real innovation happening in DeFi protocols and DAOs
- **Career Strategy**: Specific knowledge + leverage + accountability = wealth creation formula

#### 💡 Key Insights
1. **"The internet allows anyone to become a media company, a education company, a product company"**
2. Most people optimize for social approval rather than personal fulfillment
3. Reading and meditation are the highest-leverage activities for decision-making

#### 🚀 Actionable Takeaways
- Build specific knowledge in emerging tech areas (AI, crypto, biotech)
- Create content/products with network effects and zero marginal cost
- Focus on long-term reputation over short-term gains

---

### @allinchamath - "Market Outlook 2024"
**Duration:** 1h 45m | **Published:** Jan 12, 2024

#### 🔥 Main Alpha
- **Fed Policy**: Rate cuts likely Q2 2024, creating opportunities in growth stocks
- **Sector Rotation**: From mega-cap tech to mid-cap industrial and healthcare
- **Geopolitical**: US-China tensions creating opportunities in "friend-shoring" supply chains

#### 💡 Key Insights
1. **"2024 will be the year of the magnificent 7 breaking apart"** - stock picking returns
2. Energy transition investments will accelerate regardless of election outcomes
3. Consumer spending patterns permanently changed - experience over goods

#### 🚀 Actionable Takeaways
- Position for rate-sensitive sectors (REITs, utilities, small-cap)
- Consider supply chain reshoring plays (domestic manufacturing)
- Monitor energy transition ETFs and individual names

---

## 📊 Summary Statistics
- **Total Content Analyzed:** 7 hours 5 minutes
- **Key Insights Extracted:** 18
- **Actionable Alpha Points:** 12
- **Average Processing Time:** 2.3 minutes per video
- **Transcript Quality:** 100% (all videos had high-quality auto-generated captions)
```

### Optional PDF Output
- Professional styling adapted from AgenticResearch
- Optimized for reading and sharing
- Includes all markdown content with enhanced formatting
- Generated using `--pdf` flag

## Error Handling & Edge Cases

### Transcript Availability
- **Primary**: youtube-transcript-api (fastest, most reliable)
- **Fallback 1**: Web scraping transcript sites (youtubetranscript.com, downsub.com)
- **Fallback 2**: Manual transcript extraction if video has captions
- **Failure Mode**: Mark video as "No transcript available" in status checklist

### Channel Issues
- **Invalid Channel**: Clear error message with suggestions
- **No Recent Videos**: Report last video date and skip gracefully
- **Private/Deleted Videos**: Log and continue with available content
- **Rate Limiting**: Implement exponential backoff and retry logic

### Content Processing
- **Long Transcripts**: Chunk content intelligently (preserve conversation context)
- **Poor Audio Quality**: Flag low-confidence transcripts in output
- **Multiple Languages**: Support English transcripts only (for now)
- **Live Streams**: Handle live content vs. uploaded videos differently

### System Requirements
- **Dependencies**: Clear installation guide for wkhtmltopdf and Python packages
- **Disk Space**: Monitor output folder size, implement cleanup for old summaries
- **Network**: Handle intermittent connectivity gracefully
- **Performance**: Progress bars for multi-channel/multi-video processing

## Configuration Management

### Default Channel Configuration (`config/channels.yaml`)
```yaml
default_settings:
  days_lookback: 7
  videos_per_channel: 1
  output_directory: "podcast_summaries"
  
channels:
  lexfridman:
    display_name: "Lex Fridman Podcast"
    url: "https://www.youtube.com/@lexfridman"
    category: "tech"
    priority: "high"
    
  joerogan:
    display_name: "The Joe Rogan Experience" 
    url: "https://www.youtube.com/@joerogan"
    category: "general"
    priority: "medium"
    
  naval:
    display_name: "Naval"
    url: "https://www.youtube.com/@naval"
    category: "business"
    priority: "high"
```

### Global Settings (`config/settings.yaml`)
```yaml
processing:
  max_transcript_length: 50000  # characters
  chunk_size: 8000              # characters per AI analysis
  concurrent_channels: 3        # parallel processing limit
  
output:
  include_timestamps: true
  include_video_metadata: true
  pdf_styling: "professional"
  
ai_analysis:
  focus_areas: ["insights", "alpha", "actionable_takeaways"]
  summary_length: "detailed"    # brief, detailed, comprehensive
  include_quotes: true
```

## Future Enhancements

### Phase 2 Features
- **Multi-platform Support**: Spotify, Apple Podcasts, Substack
- **Custom Analysis Prompts**: User-defined focus areas (technical, business, personal)
- **Notification System**: Alert when favorite channels publish new content
- **Search & Filter**: Query historical summaries by topic, channel, or date

### Phase 3 Features  
- **Collaborative Features**: Share and comment on summaries
- **Trend Analysis**: Cross-channel topic trending and correlation
- **Integration**: Export to note-taking apps (Notion, Obsidian, Roam)
- **Advanced AI**: Fact-checking, sentiment analysis, speaker identification

## Success Metrics

### User Experience
- Command execution time < 30 seconds for single channel
- 95%+ transcript extraction success rate
- Zero manual intervention required for standard use cases

### Content Quality
- Summaries capture key insights accurately (user validation)
- Actionable alpha is genuinely actionable (trackable outcomes)
- Format enables quick scanning (5-minute read for 3-hour content)

### Technical Performance  
- Handles 10+ channels in single command execution
- Graceful degradation when services unavailable
- Memory usage stays reasonable for long-running processes