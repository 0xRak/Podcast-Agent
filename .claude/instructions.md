# Global Instructions for Podcast Morning Feed Project

## Project Overview
This project handles podcast content analysis with multiple workflow options:

### Available Commands
1. **`/podcast_extract`** - Extract transcripts from YouTube channels only
2. **`/summarize`** - Create summaries from existing transcript files
3. **`/podcast_report`** - Combined extract + summarize in single workflow
4. **`/weekly_podcast_report`** - Batch process multiple channels by category
5. **`/podcast_query`** - Natural language interface for any command

### Recommended Workflows

#### Single Episode Processing
- **Quick**: `/podcast_report @channel` → One command does extract + summarize
- **Manual**: `/podcast_extract @channel` → `/summarize transcripts/filename.md`

#### Weekly Batch Processing
- **Category-specific**: `/weekly_podcast_report --category=crypto`
- **All categories**: `/weekly_podcast_report` (processes all)

#### Natural Language Interface
- **User-friendly**: `/podcast_query "summarize crypto podcasts from last week"`

### Command Behavior Standards
- **Be concise** but helpful in responses
- **Always use TodoWrite** for multi-step tasks to track progress
- **Show progress updates** during command execution
- **Provide clear next steps** after completing each phase

## Default Preferences

### Summarization Templates
- **Default**: Blog template (natural narrative style)
- **Brief**: For quick consumption and overviews
- **Insights**: For strategic analysis and deeper thinking

### Response Style
- Keep explanations concise unless detail is requested
- Focus on actionable next steps
- Use encouraging language during processing
- Always provide specific file paths and locations

### Error Handling
- Graceful failure with helpful troubleshooting
- Show what was successfully processed even if some parts failed
- Suggest specific fixes based on error type

## Technical Standards
- Always use `uv run` for Python script execution
- Save transcripts to `transcripts/` directory
- Save summaries to `podcast_summaries/` directory
- Use proper file naming: `{clean-title}-{template}-{date}.md`

## Quality Expectations
- Generate **contextual insights** specific to each podcast's content
- Create **meaningful quote selection** based on importance and impact
- Provide **genuinely actionable takeaways** that are useful and specific
- Maintain **professional yet engaging tone** throughout summaries

## User Guidance
- Proactively suggest using the two-command workflow
- Always show file locations after successful operations
- Provide preview snippets of generated content
- Guide users on template choices based on their needs