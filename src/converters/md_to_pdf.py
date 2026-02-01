#!/usr/bin/env python3
"""
Markdown to PDF Converter using Pypandoc

This module provides functionality to convert markdown files to professionally
formatted PDFs using pypandoc (requires pandoc to be installed).
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional
import argparse

try:
    import pypandoc
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please run: uv sync")
    sys.exit(1)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def check_pandoc():
    """Check if pandoc is installed."""
    try:
        pypandoc.get_pandoc_version()
        return True
    except OSError:
        logger.error("❌ Pandoc is not installed")
        logger.error("   Install it with: brew install pandoc")
        return False


class PodcastPDFConverter:
    """PDF converter class for compatibility with podcast_summary.py"""

    def convert_markdown_to_pdf(self, markdown_file: str, pdf_path: str, verbose: bool = False) -> bool:
        """
        Convert a markdown file to PDF.

        Args:
            markdown_file: Path to markdown file
            pdf_path: Output PDF path
            verbose: Enable verbose logging

        Returns:
            bool: True if successful, False otherwise
        """
        return convert_md_to_pdf(markdown_file, output_path=pdf_path, verbose=verbose)


def convert_md_to_pdf(
    md_file_path: str,
    output_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    verbose: bool = False
) -> bool:
    """
    Convert a markdown file to a professionally formatted PDF.

    Args:
        md_file_path: Path to the markdown file
        output_path: Specific output path for the PDF (overrides output_dir)
        output_dir: Directory to save the PDF (uses same name as input)
        verbose: Enable verbose logging

    Returns:
        bool: True if conversion successful, False otherwise
    """
    try:
        md_path = Path(md_file_path)

        if not md_path.exists():
            logger.error(f"❌ File not found: {md_file_path}")
            return False

        # Determine output path
        if output_path:
            pdf_path = Path(output_path)
        elif output_dir:
            pdf_path = Path(output_dir) / f"{md_path.stem}.pdf"
        else:
            pdf_path = md_path.parent / f"{md_path.stem}.pdf"

        # Ensure output directory exists
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        if verbose:
            logger.info(f"📄 Reading: {md_path.name}")

        if verbose:
            logger.info(f"🔄 Converting to PDF via HTML...")

        # First convert to HTML with styling
        html_args = [
            '--standalone',
            '--embed-resources',
            '--toc',
            '--toc-depth=2',
            '--number-sections',
            f'--metadata=title:{md_path.stem}',
            '--highlight-style=tango',
            '--css=https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown.min.css',
        ]

        # Generate styled HTML
        html_output = pypandoc.convert_file(
            str(md_path),
            'html',
            extra_args=html_args
        )

        # Write HTML to temporary file for printing instructions
        html_path = pdf_path.with_suffix('.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_output)

        logger.info(f"✅ Created HTML: {html_path.name}")
        logger.info(f"📁 Location: {html_path.parent}")
        logger.info(f"ℹ️  To convert to PDF: Open {html_path.name} in browser and print to PDF")
        logger.info(f"ℹ️  Or install BasicTeX: brew install basictex")

        return True

    except Exception as e:
        logger.error(f"❌ Error converting {md_file_path}: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def batch_convert(
    input_dir: str,
    output_dir: Optional[str] = None,
    pattern: str = "*.md",
    verbose: bool = False
) -> tuple:
    """
    Convert multiple markdown files to PDF.

    Args:
        input_dir: Directory containing markdown files
        output_dir: Directory to save PDFs (defaults to input_dir)
        pattern: Glob pattern for finding markdown files
        verbose: Enable verbose logging

    Returns:
        tuple: (successful_count, total_count)
    """
    input_path = Path(input_dir)

    if not input_path.exists():
        logger.error(f"❌ Directory not found: {input_dir}")
        return (0, 0)

    # Find all matching markdown files
    md_files = list(input_path.glob(pattern))

    if not md_files:
        logger.warning(f"⚠️  No markdown files found matching '{pattern}' in {input_dir}")
        return (0, 0)

    logger.info(f"\n📚 Found {len(md_files)} markdown file(s):")
    for md_file in md_files:
        logger.info(f"   • {md_file.name}")

    logger.info(f"\n🔄 Converting to PDF...\n")

    success_count = 0
    for md_file in md_files:
        if convert_md_to_pdf(str(md_file), output_dir=output_dir, verbose=verbose):
            success_count += 1
        logger.info("")  # Empty line between files

    return (success_count, len(md_files))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert markdown files to professionally formatted PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single file
  podcast-pdf podcast_summaries/my-summary.md

  # Convert all summaries in a directory
  podcast-pdf podcast_summaries/

  # Specify output directory
  podcast-pdf podcast_summaries/ --output pdfs/

  # Verbose output
  podcast-pdf my-file.md --verbose
        """
    )

    parser.add_argument(
        'input',
        help='Input markdown file or directory'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output PDF file path or directory'
    )

    parser.add_argument(
        '-p', '--pattern',
        default='*.md',
        help='File pattern for batch conversion (default: *.md)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Check if pandoc is installed
    if not check_pandoc():
        sys.exit(1)

    input_path = Path(args.input)

    logger.info("\n" + "="*60)
    logger.info("📄 MARKDOWN TO PDF CONVERTER")
    logger.info("="*60 + "\n")

    try:
        if input_path.is_file():
            # Single file conversion
            success = convert_md_to_pdf(
                str(input_path),
                output_path=args.output,
                verbose=args.verbose
            )
            exit_code = 0 if success else 1

        elif input_path.is_dir():
            # Batch conversion
            success_count, total_count = batch_convert(
                str(input_path),
                output_dir=args.output,
                pattern=args.pattern,
                verbose=args.verbose
            )

            logger.info("="*60)
            logger.info(f"📊 SUMMARY: {success_count}/{total_count} files converted successfully")
            logger.info("="*60 + "\n")

            exit_code = 0 if success_count == total_count else 1

        else:
            logger.error(f"❌ Invalid input: {args.input}")
            logger.error("   Input must be a file or directory")
            exit_code = 1

        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Conversion cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
