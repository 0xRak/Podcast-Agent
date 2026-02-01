# Podcast Summary Tool

AI-powered tool for extracting key insights and actionable alpha from YouTube podcast episodes. Built to work seamlessly with Claude Code's agent system.

## 🚀 Features

- **Multi-Channel Processing**: Analyze latest episodes from multiple YouTube channels
- **Free Transcript Extraction**: Uses `youtube-transcript-api` with web scraping fallbacks
- **Claude AI Analysis**: Leverages Claude Code's agent system for high-quality insights
- **Structured Output**: Generates professional markdown summaries with key insights and alpha
- **HTML/PDF Export**: Professionally formatted HTML files ready for printing to PDF
- **Smart Chunking**: Handles long transcripts by intelligently splitting content
- **Progress Tracking**: Real-time status updates for multi-channel processing
- **Error Handling**: Comprehensive fallback strategies and error recovery

## 🔗 Use in Other Projects

Want to use this tool in another project? See **[INTEGRATION-SPEC.md](./INTEGRATION-SPEC.md)** for complete integration instructions. The spec includes:

- Step-by-step setup guide
- All slash command files (copy-pasteable)
- Configuration templates
- Usage examples and troubleshooting

This allows another Claude Code agent to integrate the full podcast pipeline into any project.

---

## 📋 Requirements

### Python Dependencies
Install with: `uv sync`

- youtube-transcript-api>=0.6.2
- yt-dlp>=2024.8.6
- pypandoc>=1.13
- PyYAML>=6.0.1
- requests>=2.31.0
- beautifulsoup4>=4.12.2

### System Dependencies

**Required:**
- **Pandoc**: `brew install pandoc` (required for HTML/PDF export)

**Optional (for automatic PDF generation):**
- **BasicTeX**: `brew install basictex` (enables automatic PDF generation)
- Without BasicTeX: Tool generates HTML files that can be printed to PDF via browser

## 🎯 Usage

### Command Syntax
```bash
/podcast_summary @channel1 @channel2 [options]
```

### Examples

**Basic usage** - Latest video from each channel:
```bash
/podcast_summary @lexfridman @joerogan @naval
```

**Advanced options**:
```bash
# Last 3 videos from past 14 days
/podcast_summary @lexfridman --days=14 --limit=3

# Custom output directory
/podcast_summary @allinchamath @davidperell --output=my_summaries/

# Verbose logging
/podcast_summary @naval --verbose
```

### PDF/HTML Export

**Generate shareable HTML reports:**
```bash
# Single file
/generate-pdf podcast_summaries/my-summary-blog-2025-10-07.md

# Batch convert all summaries
/generate-pdf podcast_summaries/

# Custom output directory
/generate-pdf podcast_summaries/ --output=pdfs/
```

**Output:**
- Creates professionally formatted HTML with GitHub styling, table of contents, and syntax highlighting
- HTML files can be printed to PDF via browser (⌘+P → Save as PDF)
- With BasicTeX installed: Automatically generates PDF files

### Available Flags
- `--days=N`: Look back N days for videos (default: 7)
- `--limit=N`: Max videos per channel (default: 1)
- `--output=PATH`: Custom output directory
- `--config=PATH`: Custom configuration file
- `--verbose`: Enable detailed logging
- `--dry-run`: Show what would be processed

### PDF Generation Flags (`/generate-pdf`)
- `--output=PATH`: Custom output directory for HTML/PDF files
- `--pattern=*.md`: File pattern for batch conversion
- `--verbose`: Show detailed conversion progress

## 📊 Output Format

The tool generates structured markdown files like `youtube-research-2024-01-15.md`:

```markdown
# Podcast Research Summary
**Generated:** 2024-01-15 14:30 UTC
**Channels Processed:** 3
**Videos Analyzed:** 3

## Processing Status
- [x] @lexfridman - "AI Safety with Stuart Russell" (Jan 14, 2024) ✓
- [x] @joerogan - "#2079 - Naval Ravikant Returns" (Jan 13, 2024) ✓

## 🎯 Key Insights & Alpha

### @lexfridman - "AI Safety with Stuart Russell"
**Duration:** 2h 15m | **Published:** Jan 14, 2024

#### 🔥 Main Alpha
- AI alignment companies will be critical investments as AI scales
- Regulatory catalysts expected in AI safety space by 2025-2026

#### 💡 Key Insights
1. The biggest risk isn't malicious AI but incompetent AI systems
2. Current AI safety research is underfunded relative to capabilities research

#### 🚀 Actionable Takeaways
- Monitor AI safety startups (Anthropic, Constitutional AI)
- Watch for regulatory developments in AI safety space

## 📊 Summary Statistics
- **Total Content Analyzed:** 7 hours 5 minutes
- **Key Insights Extracted:** 18
- **Actionable Alpha Points:** 12
```

## ⚙️ Configuration

### Default Channels (`config/channels.yaml`)
```yaml
channels:
  lexfridman:
    display_name: "Lex Fridman Podcast"
    category: "tech"
    priority: "high"
  
  joerogan:
    display_name: "The Joe Rogan Experience"
    category: "general"
    priority: "medium"
```

### Settings (`config/settings.yaml`)
```yaml
processing:
  max_transcript_length: 50000
  chunk_size: 8000
  concurrent_channels: 3

ai_analysis:
  focus_areas: ["insights", "alpha", "actionable_takeaways"]
  summary_length: "detailed"
  include_quotes: true
```

## 🏗️ Architecture

```
src/
├── podcast_summary.py          # Main command handler
├── extractors/
│   ├── youtube_extractor.py    # yt-dlp integration
│   └── transcript_fetcher.py   # Transcript extraction + fallbacks
├── processors/
│   ├── claude_analyzer.py      # Claude agent integration
│   ├── content_chunker.py      # Long transcript handling
│   └── insight_formatter.py    # Markdown generation
├── utils/
│   ├── config_manager.py       # Configuration handling
│   ├── progress_tracker.py     # Status tracking
│   └── error_handler.py        # Error management
└── converters/
    └── md_to_pdf.py           # PDF generation
```

## 🧠 Claude Agent Integration

The tool leverages Claude Code's agent system for analysis:

1. **Transcript Processing**: Intelligently chunks long content
2. **AI Analysis**: Specialized prompts for extracting insights and alpha  
3. **Structured Output**: Formats results for easy consumption
4. **Context Preservation**: Maintains conversation flow across chunks

**Key Analysis Areas:**
- 🔥 **Main Alpha**: Investment/business insights with competitive advantage
- 💡 **Key Insights**: Important frameworks, trends, and perspectives  
- 🚀 **Actionable Takeaways**: Specific actions readers can implement
- 📝 **Key Quotes**: Most impactful quotes that capture main ideas

## 🛠️ Development

### Running Tests
```bash
# Test individual components
python src/extractors/youtube_extractor.py
python src/extractors/transcript_fetcher.py
python src/processors/content_chunker.py

# Test full pipeline
python src/podcast_summary.py @lexfridman --dry-run --verbose
```

### Error Handling
The tool includes comprehensive error handling:
- Network timeouts → Automatic retry with backoff
- Missing transcripts → Web scraping fallbacks  
- Long content → Intelligent chunking
- Rate limits → Exponential backoff
- Analysis failures → Fallback analysis methods

### Logging
Logs are saved to `logs/podcast_summary.log` with configurable levels:
- INFO: Normal operation status
- WARNING: Recoverable issues  
- ERROR: Operation failures
- DEBUG: Detailed processing info

## 📈 Performance

**Typical Processing Times:**
- Single video analysis: 30-60 seconds
- Multi-channel batch (3 channels): 2-4 minutes
- PDF generation: 5-10 seconds additional

**Resource Usage:**
- Memory: ~100-200MB during processing
- Storage: ~1MB per summary file
- Network: Minimal (transcript extraction only)

## 🤝 Contributing

1. Follow the existing code structure and error handling patterns
2. Add comprehensive logging for debugging
3. Include fallback strategies for external API dependencies  
4. Test with various channel types and content lengths
5. Update documentation for new features

## 🔧 Troubleshooting

**Common Issues:**

1. **"Pandoc not found"** → Install with `brew install pandoc`
2. **"pdflatex not found"** → Install BasicTeX: `brew install basictex` OR use HTML→PDF via browser
3. **"No transcript available"** → Video may not have captions
4. **"Channel not found"** → Check channel handle spelling
5. **"Rate limit exceeded"** → Tool will automatically retry
6. **"Connection timeout"** → Check internet connection

**Debug Mode:**
```bash
/podcast_summary @channel --verbose --dry-run
```

## 📄 License

Built for use with Claude Code. Leverages open-source tools:
- youtube-transcript-api (MIT)
- yt-dlp (Unlicense)
- pandoc (GPL-2.0)
- pypandoc (MIT)

---

*Generated by Claude Code Podcast Summary Tool v1.0.0*
*Last updated: November 27, 2025*