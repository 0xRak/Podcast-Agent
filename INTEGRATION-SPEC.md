# Podcast Morning Feed - Integration Specification

> **For Claude Code Agents**: This document contains everything needed to integrate the Podcast Morning Feed tool into another project. Follow the steps below and copy the provided files.

---

## 1. Tool Overview

**Podcast Morning Feed** is an AI-powered podcast research tool that:

1. **Extracts transcripts** from YouTube podcast channels
2. **Creates intelligent summaries** with insights, quotes, and actionable takeaways
3. **Converts summaries** to professional HTML/PDF reports for sharing

### 3-Phase Pipeline Architecture

```
Phase 1: EXTRACT               Phase 2: SUMMARIZE              Phase 3: EXPORT
┌─────────────────┐           ┌─────────────────────┐         ┌─────────────────┐
│ YouTube Channel │ ────────► │ Transcript (markdown)│ ──────► │ Summary (markdown)│ ──────► │ HTML/PDF Report │
│ @lexfridman     │           │ transcripts/*.md     │         │ podcast_summaries/*.md │   │ *.html / *.pdf  │
└─────────────────┘           └─────────────────────┘         └─────────────────┘

Command: /podcast_extract      Command: /summarize              Command: /generate_pdf
```

**Combined command**: `/podcast_report` runs all 3 phases automatically.

---

## 2. Prerequisites

### System Dependencies

```bash
# macOS - REQUIRED
brew install pandoc

# Optional: Enable PDF output (otherwise HTML only)
brew install basictex
```

### Python Requirements

- **Python**: 3.9 or higher
- **Package Manager**: UV (recommended) or pip

---

## 3. Integration Steps

### Step 1: Copy Source Files

Copy the entire `src/` directory to your target project. The structure is:

```
src/
├── podcast_summary.py           # Main extraction orchestrator
├── summarize.py                 # Summary generation
├── extractors/
│   ├── __init__.py
│   ├── youtube_extractor.py     # yt-dlp integration
│   └── transcript_fetcher.py    # Multi-method transcript fetching
├── processors/
│   ├── __init__.py
│   ├── claude_analyzer.py       # Claude analysis (optional)
│   ├── content_chunker.py       # Long transcript handling
│   ├── insight_formatter.py     # Markdown formatting
│   ├── natural_summarizer.py    # Pattern-based summarization
│   └── weekly_digest.py         # Weekly report generation
├── storage/
│   ├── __init__.py
│   └── transcript_storage.py    # File management
├── utils/
│   ├── __init__.py
│   ├── config_manager.py        # YAML config handling
│   ├── progress_tracker.py      # Status tracking
│   └── error_handler.py         # Error management
└── converters/
    ├── __init__.py
    └── md_to_pdf.py             # Markdown to HTML/PDF
```

### Step 2: Copy Configuration Directory

Copy the `config/` directory:

```
config/
├── channels.yaml    # Podcast channel definitions
└── settings.yaml    # Processing settings
```

### Step 3: Copy Slash Commands

Copy to your project's `.claude/commands/` directory:

```
.claude/commands/
├── podcast_extract.md    # Transcript extraction
├── summarize.md          # Summary creation
├── generate_pdf.md       # HTML/PDF export
└── podcast_report.md     # Combined pipeline
```

**Full contents of each file provided below in Section 5.**

### Step 4: Add Python Dependencies

Add these to your project's `pyproject.toml` under `[project]`:

```toml
dependencies = [
    "youtube-transcript-api>=0.6.2",
    "yt-dlp>=2024.8.6",
    "pypandoc>=1.13",
    "PyYAML>=6.0.1",
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.2",
    "lxml>=4.9.3",
    "html5lib>=1.1",
]
```

Then install:

```bash
uv sync
# OR
pip install -e .
```

### Step 5: Create Output Directories

```bash
mkdir -p transcripts podcast_summaries transcript_reports logs
```

### Step 6: Add CLI Entry Points (Optional)

Add to `pyproject.toml` under `[project.scripts]`:

```toml
[project.scripts]
podcast-summary = "src.podcast_summary:main"
podcast-pdf = "src.converters.md_to_pdf:main"
```

---

## 4. Directory Structure (Final)

After integration, your project should have:

```
your-project/
├── .claude/
│   └── commands/
│       ├── podcast_extract.md
│       ├── summarize.md
│       ├── generate_pdf.md
│       └── podcast_report.md
├── config/
│   ├── channels.yaml
│   └── settings.yaml
├── src/
│   ├── podcast_summary.py
│   ├── summarize.py
│   ├── extractors/
│   ├── processors/
│   ├── storage/
│   ├── utils/
│   └── converters/
├── transcripts/              # Auto-populated
├── podcast_summaries/        # Auto-populated
├── transcript_reports/       # Auto-populated
├── logs/
│   └── podcast_summary.log
└── pyproject.toml
```

---

## 5. Slash Command Contents

### File: `.claude/commands/podcast_extract.md`

```markdown
You are a podcast transcript extraction assistant. When the user provides a `/podcast_extract` command, you should:

## Primary Function: Transcript Extraction Only

1. **Parse the command arguments** from the user input:
   - Extract channel handles (e.g., @lexfridman, @joerogan)
   - Parse optional flags like --days=7, --limit=1, --verbose, --dry-run
   - Default values: --days=7, --limit=1

2. **Execute the transcript extraction tool** using UV:
   ```bash
   uv run python src/podcast_summary.py [channels] [flags]
   ```

3. **Handle the execution**:
   - Run the command with the parsed arguments
   - Monitor progress and show status updates to the user
   - Handle any errors gracefully and provide helpful feedback

4. **Present extraction results**:
   - Show which transcript files were saved to `transcripts/` directory
   - Display key statistics (channels processed, videos extracted, etc.)
   - **Important**: Guide user to next step for summarization

## Next Steps After Extraction

After successfully extracting transcripts, inform the user:

> ✅ **Transcripts extracted successfully!**
>
> **Next step**: Use the `/summarize` command to create intelligent summaries:
> - `/summarize transcripts/filename.md` (blog format)
> - `/summarize transcripts/filename.md --template=brief` (concise format)
> - `/summarize transcripts/filename.md --template=insights` (strategic insights)

## Example Usage Patterns
- `/podcast_extract @lexfridman` → Extract transcripts → Use `/summarize` on results
- `/podcast_extract @joerogan --days=14 --limit=2` → Extract multiple transcripts → Summarize individually

**Important notes:**
- This command **only extracts transcripts** - it does not create summaries
- Always use `uv run` to ensure the correct Python environment
- Remove @ prefix from channel handles when passing to the Python script
- Extracted transcripts are saved to `transcripts/` directory
- Show progress updates and be encouraging during processing
- Always guide users to use `/summarize` for the next step

**Error handling:**
- If channels don't exist: Suggest checking channel handle spelling
- If no transcripts available: Explain that some videos may not have captions
- If network issues: Suggest trying again or checking internet connection
- Always show what was successfully processed even if some channels failed
```

---

### File: `.claude/commands/summarize.md`

```markdown
When the user provides a `/summarize` command, you should create an intelligent natural language summary from a stored transcript file. Follow these steps:

## Command Processing

1. **Parse the command arguments**:
   - Extract transcript file path (e.g., `transcripts/filename.md`)
   - Parse optional template flag: `--template=blog|brief|insights` (default: blog)
   - Handle optional output directory: `--output=directory` (default: podcast_summaries)

## Summary Creation Process

2. **Read and analyze the transcript**:
   - Load the specified transcript file from the transcripts directory
   - Extract metadata (title, channel, duration) from the transcript header
   - Analyze the full content using your natural language understanding capabilities

3. **Generate intelligent summary based on template**:

   **Blog Template (default)**:
   - Create engaging introduction with context
   - Identify and explain 3-4 key insights with depth
   - Extract meaningful quotes that illustrate important points
   - Provide 3-4 actionable takeaways
   - Write conclusion connecting insights to broader implications
   - Use natural, flowing narrative style

   **Insights Template**:
   - Focus on strategic insights and market dynamics
   - Provide deeper analysis of implications
   - Include supporting evidence and context
   - Structure as numbered insights with explanations

   **Brief Template**:
   - Concise format with key topics and main quote
   - Quick overview for fast consumption
   - Include worth listening assessment

4. **Save and present results**:
   - Save to `podcast_summaries/` directory with format: `{clean-title}-{template}-{date}.md`
   - Show preview of generated summary
   - Provide file location and success confirmation

## Quality Standards

- **Use your advanced language understanding** rather than pattern matching
- **Generate contextual insights** that are specific to the content
- **Create meaningful quotes selection** based on importance and impact
- **Ensure actionable takeaways** are genuinely useful and specific
- **Maintain professional tone** while being engaging and accessible

## Error Handling

- If transcript file doesn't exist, provide helpful error message
- If file is empty or corrupted, suggest checking source
- Handle any parsing issues gracefully
- Always show what was successfully processed

## Example Usage
- `/summarize transcripts/0xresearchPodcast_20250915_4N0BUzMVMEk.md`
- `/summarize transcripts/filename.md --template=insights`
- `/summarize transcripts/filename.md --template=brief --output=summaries`

**Remember**: Your goal is to create genuinely insightful summaries that capture the essence, value, and key learnings from each podcast transcript using your natural language capabilities.
```

---

### File: `.claude/commands/generate_pdf.md`

```markdown
When the user provides a `/generate_pdf` command, you should convert podcast summary markdown files to professionally formatted PDFs for sharing. Follow these steps:

## Command Processing

1. **Parse the command arguments**:
   - Extract file or directory path (e.g., `podcast_summaries/filename.md` or `podcast_summaries/`)
   - Parse optional flags:
     - `--output=directory` - Custom output directory (default: same as input)
     - `--pattern=*.md` - File pattern for batch conversion (default: *.md)
     - `--verbose` - Show detailed conversion progress

## PDF Generation Process

2. **Validate input and show what will be processed**:
   - Check if input path exists
   - If directory: list all matching markdown files
   - If single file: confirm the file exists
   - Show user what will be converted and ask for confirmation

3. **Execute conversion using UV**:
   ```bash
   uv run podcast-pdf [input] [flags]
   ```

4. **Monitor and report progress**:
   - Show conversion progress for each file
   - Display file sizes and output locations
   - Report any errors encountered
   - Provide final summary with success/failure counts

## User Interaction & Feedback

**Before conversion:**
> 🤖 **I will convert the following to PDF:**
>
> **Files to process:**
> - mcp-servers-teaching-ai-blog-2025-10-07.md
> - another-summary-blog-2025-10-06.md
>
> **Output directory:** `podcast_summaries/`
>
> **Proceed with conversion?** (The conversion will start automatically, type 'stop' to cancel)

**During conversion:**
> 📄 Converting markdown files to PDF...

**After conversion:**
> ✅ **PDF Generation Complete!**
>
> **Results:**
> - ✅ mcp-servers-teaching-ai-blog-2025-10-07.pdf (156.3 KB)
> - ✅ another-summary-blog-2025-10-06.pdf (142.7 KB)
>
> **Summary:** 2/2 files converted successfully
> **Location:** `podcast_summaries/`

## Error Handling

- If input path doesn't exist, provide clear error message
- If no markdown files found, suggest checking the pattern
- If conversion fails, show which files succeeded and which failed
- If dependencies missing, instruct to run `uv sync`

## Command Examples

- `/generate_pdf podcast_summaries/my-summary-blog-2025-10-07.md`
  Convert a single summary to PDF

- `/generate_pdf podcast_summaries/`
  Convert all markdown files in the directory to PDF

- `/generate_pdf podcast_summaries/ --output=pdfs/`
  Convert all summaries and save PDFs to a separate directory

- `/generate_pdf podcast_summaries/ --pattern=*-blog-*.md --verbose`
  Convert only blog-template summaries with detailed output

## Quality Standards

- **Show clear feedback** at each stage (before, during, after)
- **Confirm with user** before starting batch conversions
- **Report detailed results** including file sizes and locations
- **Handle errors gracefully** and continue with remaining files
- **Provide actionable suggestions** when things go wrong

## Technical Notes

- Uses **pypandoc** (Python wrapper for Pandoc system tool)
- Generates professional HTML with GitHub styling
- PDF requires BasicTeX (`brew install basictex`)
- Supports markdown features: headings, lists, code blocks, tables, quotes
- Page numbers and professional typography included

**Important:**
- Always use `uv run podcast-pdf` for execution
- Show progress updates during conversion
- Provide human-readable file sizes
- Make sure output directories are clearly communicated to the user
```

---

### File: `.claude/commands/podcast_report.md`

```markdown
You are a combined podcast processing assistant. When the user provides a `/podcast_report` command, you should run both transcript extraction and summarization in a single workflow.

## Primary Function: Extract + Summarize Combined

1. **Parse the command arguments** from the user input:
   - Extract channel handles (e.g., @lexfridman, @joerogan)
   - Parse optional flags like --days=7, --limit=1, --template=blog, --verbose, --dry-run
   - Default values: --days=7, --limit=1, --template=blog

2. **Phase 1: Execute transcript extraction** using UV:
   ```bash
   uv run python src/podcast_summary.py [channels] [flags]
   ```

3. **Monitor Phase 1 progress**:
   - Show extraction progress and status updates
   - Handle any extraction errors gracefully
   - Track which transcript files were successfully created
   - Display extraction statistics (channels processed, videos extracted, etc.)

4. **Phase 2: Auto-summarize extracted transcripts**:
   - Automatically identify newly extracted transcript files from Phase 1
   - For each transcript file, run:
   ```bash
   /summarize transcripts/filename.md --template=[specified template]
   ```
   - Use the template specified in original command (default: blog)

5. **Monitor Phase 2 progress**:
   - Show summarization progress for each transcript
   - Handle summarization errors gracefully
   - Display summary file locations and previews

## Workflow Presentation

**Phase 1 Update:**
> 🎙️ **Phase 1/2: Extracting Transcripts**
> Processing [N] channels for the last [X] days...

**Transition Message:**
> ✅ **Phase 1 Complete!** [N] transcripts extracted
> 🧠 **Phase 2/2: Creating Intelligent Summaries**

**Final Results:**
> ✅ **Podcast Report Complete!**
>
> **📄 Transcripts:** `transcripts/` directory ([N] files)
> **📋 Summaries:** `podcast_summaries/` directory ([N] files)
>
> **Files processed:**
> - Channel: filename.md → summary-blog-date.md
> - Channel: filename.md → summary-blog-date.md

## Error Handling

- **If Phase 1 fails completely**: Stop and report extraction errors
- **If Phase 1 partially succeeds**: Continue with Phase 2 for successful extractions
- **If Phase 2 fails for some files**: Report which summaries failed, show successful ones
- **Always show what was successfully processed**

## Command Examples

- `/podcast_report @lexfridman` → Extract + Summarize with blog template
- `/podcast_report @joerogan --days=14 --limit=2` → Process multiple videos
- `/podcast_report @naval --template=insights` → Use insights template for summaries
- `/podcast_report @allinchamath @lexfridman --template=brief` → Multiple channels, brief format

## Quality Standards

- **Show clear progress** through both phases
- **Provide encouraging updates** during processing
- **Handle partial failures gracefully** - complete what's possible
- **Always show final file locations** for both transcripts and summaries
- **Display preview snippets** of generated summaries when successful

**Important notes:**
- This command combines both extraction and summarization steps
- Always use `uv run` for Python script execution
- Remove @ prefix from channel handles when passing to the Python script
- Show progress updates for both phases
- Use TodoWrite for tracking the two-phase workflow
```

---

## 6. Configuration Templates

### File: `config/channels.yaml`

```yaml
# Podcast Channel Configuration
# Add your YouTube channels here

aliases:
  # Shortcuts for frequently used channels
  # Usage: /podcast_extract @lex instead of @lexfridman
  lex: lexfridman
  # Add more aliases as needed

categories:
  # Organize channels by topic
  ai: []
  business: []
  crypto: []
  general: []

channels:
  # Example channel configuration:
  lexfridman:
    display_name: "Lex Fridman Podcast"
    category: ai
    priority: high
    url: https://www.youtube.com/@lexfridman
    enabled: true
    last_processed: null

  # Add more channels following this pattern:
  # channelhandle:
  #   display_name: "Display Name"
  #   category: ai|business|crypto|general
  #   priority: high|medium|low
  #   url: https://www.youtube.com/@channelhandle
  #   enabled: true
  #   last_processed: null

default_settings:
  days_lookback: 7           # How many days back to search for videos
  output_directory: podcast_summaries
  videos_per_channel: 1      # Default videos to process per channel
```

### File: `config/settings.yaml`

```yaml
# Processing Settings

ai_analysis:
  confidence_threshold: 0.7
  focus_areas:
    - insights
    - alpha
    - actionable_takeaways
  include_quotes: true
  summary_length: detailed

logging:
  level: INFO
  log_file: logs/podcast_summary.log
  log_to_file: true

output:
  filename_format: youtube-research-{date}.md
  include_timestamps: true
  include_video_metadata: true
  max_summary_length: 2000
  pdf_styling: professional

processing:
  chunk_size: 8000           # Characters per chunk for analysis
  concurrent_channels: 3     # Parallel channel processing
  max_transcript_length: 50000
  retry_attempts: 3
  retry_delay: 5             # Seconds between retries
```

---

## 7. Usage Examples

### Basic Workflow (3 Commands)

```bash
# Step 1: Extract transcript from a channel
/podcast_extract @lexfridman --days=7

# Step 2: Create summary from the transcript
/summarize transcripts/lexfridman_2025-10-01_abc123.md

# Step 3: Convert to shareable HTML
/generate_pdf podcast_summaries/lex-fridman-episode-blog-2025-10-01.md
```

### Combined Workflow (1 Command)

```bash
# Extract + Summarize in one command
/podcast_report @lexfridman --days=7 --template=blog
```

### Multiple Channels

```bash
# Process multiple channels at once
/podcast_report @lexfridman @joerogan @naval --days=14 --limit=2
```

### Different Summary Templates

```bash
# Blog format (default) - narrative with insights
/summarize transcripts/file.md --template=blog

# Brief format - quick overview
/summarize transcripts/file.md --template=brief

# Insights format - strategic analysis
/summarize transcripts/file.md --template=insights
```

### Batch PDF Generation

```bash
# Convert all summaries in a directory
/generate_pdf podcast_summaries/

# Convert specific pattern
/generate_pdf podcast_summaries/ --pattern=*-blog-*.md
```

---

## 8. Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| "No transcript available" | Video has no captions | Some videos don't have auto-generated or manual captions. Try a different video. |
| "Pandoc not found" | System dependency missing | Run `brew install pandoc` |
| "Module not found" | Python dependencies not installed | Run `uv sync` or `pip install -e .` |
| "Channel not found" | Invalid channel handle | Check spelling. Use format `@channelhandle` |
| "PDF generation failed" | BasicTeX not installed | HTML still works. For PDF: `brew install basictex` |
| "Rate limited" | Too many requests | Wait a few minutes, then retry with `--limit=1` |

### Common Issues

**Transcript extraction fails for some videos:**
- Not all YouTube videos have captions
- The tool tries multiple methods (youtube-transcript-api, web scraping)
- If all methods fail, the video is skipped

**Summary quality issues:**
- Try a different template (`--template=insights` for deeper analysis)
- Ensure transcript is complete (check transcripts/*.md file)

**Slow processing:**
- Reduce `--limit` to process fewer videos
- Process one channel at a time

---

## 9. Sample Output

### Transcript File (`transcripts/lexfridman_2025-10-01_abc123.md`)

```markdown
# Episode Title Here
**Channel:** Lex Fridman Podcast
**Duration:** 2 hours, 15 minutes
**Published:** 2025-10-01
**Video ID:** abc123

## Transcript

[Full transcript text here...]
```

### Summary File (`podcast_summaries/episode-title-blog-2025-10-01.md`)

```markdown
# Episode Title Here

**Source:** Lex Fridman Podcast
**Guest:** Guest Name
**Duration:** 2 hours, 15 minutes

## Key Insights

### 1. First Key Insight
Detailed explanation of the insight and its implications...

### 2. Second Key Insight
More analysis and context...

## Notable Quotes

> "Important quote from the episode that captures a key idea."

## Actionable Takeaways

1. **First actionable item** - Specific action readers can take
2. **Second actionable item** - Another concrete recommendation

## Conclusion

Synthesis of the episode's main themes and their broader implications...
```

---

## 10. Quick Start Checklist

- [ ] Install Pandoc: `brew install pandoc`
- [ ] Copy `src/` directory to target project
- [ ] Copy `config/` directory to target project
- [ ] Copy `.claude/commands/*.md` files to `.claude/commands/`
- [ ] Add dependencies to `pyproject.toml`
- [ ] Run `uv sync` to install dependencies
- [ ] Create directories: `mkdir -p transcripts podcast_summaries transcript_reports logs`
- [ ] Configure `config/channels.yaml` with your podcast channels
- [ ] Test with: `/podcast_extract @lexfridman --days=7`

---

**Source Repository:** Podcast Morning Feed
**Last Updated:** November 2025
**Tested With:** Python 3.9-3.12, macOS
