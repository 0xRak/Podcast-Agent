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