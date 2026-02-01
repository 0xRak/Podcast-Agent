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

- Uses **weasyprint** (pure Python, no external dependencies)
- Generates professional A4 PDFs with custom styling
- Supports markdown features: headings, lists, code blocks, tables, quotes
- Page numbers and professional typography included
- Safe for macOS (no wkhtmltopdf dependency issues)

**Important:**
- Always use `uv run podcast-pdf` for execution
- Show progress updates during conversion
- Provide human-readable file sizes
- Make sure output directories are clearly communicated to the user
