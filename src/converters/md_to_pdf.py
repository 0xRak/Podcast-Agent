#!/usr/bin/env python3
"""
PDF converter adapted from AgenticResearch for podcast-specific formatting.
"""

import os
import sys
import glob
import logging
from pathlib import Path
from typing import Optional, List, Dict
import subprocess

logger = logging.getLogger(__name__)

class PodcastPDFConverter:
    """Convert podcast summary markdown files to professionally styled PDFs."""
    
    def __init__(self):
        """Initialize the PDF converter."""
        self.required_packages = ['markdown', 'pdfkit']
        self.wkhtmltopdf_binary = None
    
    def check_requirements(self) -> bool:
        """Check if required packages and binaries are available."""
        missing_packages = []
        
        # Check Python packages
        for package in self.required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error("Required packages not found. Install with:")
            logger.error(f"pip install {' '.join(missing_packages)}")
            return False
        
        # Check wkhtmltopdf binary
        if not self._check_wkhtmltopdf():
            logger.error("wkhtmltopdf not found. Install with:")
            logger.error("Ubuntu/Debian: sudo apt-get install wkhtmltopdf")
            logger.error("macOS: brew install wkhtmltopdf")
            logger.error("Windows: Download from https://wkhtmltopdf.org/downloads.html")
            return False
        
        return True
    
    def _check_wkhtmltopdf(self) -> bool:
        """Check if wkhtmltopdf is available."""
        try:
            result = subprocess.run(['wkhtmltopdf', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            self.wkhtmltopdf_binary = 'wkhtmltopdf'
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # Try common alternative paths
        alternative_paths = [
            '/usr/bin/wkhtmltopdf',
            '/usr/local/bin/wkhtmltopdf',
            'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
        ]
        
        for path in alternative_paths:
            if os.path.exists(path):
                try:
                    result = subprocess.run([path, '--version'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        self.wkhtmltopdf_binary = path
                        return True
                except subprocess.SubprocessError:
                    continue
        
        return False
    
    def convert_markdown_to_pdf(self, md_file_path: str, output_path: Optional[str] = None) -> bool:
        """
        Convert a single markdown file to PDF with podcast-specific styling.
        
        Args:
            md_file_path: Path to the markdown file
            output_path: Optional output path for PDF (defaults to same directory)
            
        Returns:
            True if conversion successful, False otherwise
        """
        try:
            if not self.check_requirements():
                return False
            
            import markdown
            import pdfkit
            
            md_path = Path(md_file_path)
            
            if not md_path.exists():
                logger.error(f"Markdown file not found: {md_file_path}")
                return False
            
            # Determine output path
            if output_path:
                pdf_path = Path(output_path)
            else:
                pdf_path = md_path.parent / f"{md_path.stem}.pdf"
            
            # Ensure output directory exists
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read markdown content
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convert markdown to HTML with extensions
            html = markdown.markdown(
                md_content, 
                extensions=['tables', 'fenced_code', 'toc', 'attr_list']
            )
            
            # Add podcast-specific CSS styling
            html_with_css = self._add_podcast_styling(html, md_path.stem)
            
            # Configure PDF options
            pdf_options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None,
                'print-media-type': None
            }
            
            # Add wkhtmltopdf binary path if found
            config = None
            if self.wkhtmltopdf_binary and self.wkhtmltopdf_binary != 'wkhtmltopdf':
                config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_binary)
            
            # Convert HTML to PDF
            pdfkit.from_string(
                html_with_css, 
                str(pdf_path), 
                options=pdf_options,
                configuration=config
            )
            
            logger.info(f"✓ PDF generated: {pdf_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting {md_file_path} to PDF: {str(e)}")
            return False
    
    def _add_podcast_styling(self, html_content: str, title: str) -> str:
        """Add podcast-specific CSS styling to HTML content."""
        
        css_styles = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                /* Base Styles */
                * {
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 30px 40px;
                    color: #333;
                    background: #fff;
                }
                
                /* Headers */
                h1 {
                    color: #2c3e50;
                    font-size: 28px;
                    font-weight: 700;
                    margin: 0 0 20px 0;
                    padding-bottom: 10px;
                    border-bottom: 3px solid #3498db;
                }
                
                h2 {
                    color: #34495e;
                    font-size: 22px;
                    font-weight: 600;
                    margin: 30px 0 15px 0;
                    padding: 10px 0;
                    border-bottom: 2px solid #ecf0f1;
                }
                
                h3 {
                    color: #2c3e50;
                    font-size: 18px;
                    font-weight: 600;
                    margin: 25px 0 12px 0;
                }
                
                h4 {
                    color: #7f8c8d;
                    font-size: 16px;
                    font-weight: 600;
                    margin: 20px 0 10px 0;
                }
                
                /* Podcast-specific styling */
                .podcast-metadata {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    border-left: 4px solid #3498db;
                }
                
                /* Emoji headers and content */
                h2:contains("🎯"), h4:contains("🔥"), h4:contains("💡"), 
                h4:contains("🚀"), h4:contains("📝"), h4:contains("📊") {
                    background: linear-gradient(90deg, #f8f9fa 0%, #fff 100%);
                    padding: 12px 15px;
                    border-radius: 6px;
                    margin: 25px 0 15px 0;
                    border-left: 4px solid #e74c3c;
                }
                
                /* Alpha and insights highlighting */
                h4:contains("🔥") {
                    border-left-color: #e74c3c;
                    background: linear-gradient(90deg, #fdf2f2 0%, #fff 100%);
                }
                
                h4:contains("💡") {
                    border-left-color: #f39c12;
                    background: linear-gradient(90deg, #fef9f3 0%, #fff 100%);
                }
                
                h4:contains("🚀") {
                    border-left-color: #27ae60;
                    background: linear-gradient(90deg, #f0f8f4 0%, #fff 100%);
                }
                
                /* Lists */
                ul, ol {
                    margin: 15px 0;
                    padding-left: 25px;
                }
                
                li {
                    margin: 8px 0;
                    line-height: 1.5;
                }
                
                li strong {
                    color: #2c3e50;
                }
                
                /* Quotes */
                blockquote {
                    border-left: 4px solid #3498db;
                    margin: 20px 0;
                    padding: 15px 20px;
                    background: #f8f9fa;
                    font-style: italic;
                    color: #555;
                    border-radius: 0 6px 6px 0;
                }
                
                /* Code */
                code {
                    background-color: #f4f4f4;
                    padding: 3px 6px;
                    border-radius: 4px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 0.9em;
                    color: #e74c3c;
                }
                
                pre {
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 6px;
                    overflow-x: auto;
                    border: 1px solid #e9ecef;
                    margin: 15px 0;
                }
                
                pre code {
                    background: none;
                    padding: 0;
                    color: #333;
                }
                
                /* Tables */
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                    background: #fff;
                    border-radius: 6px;
                    overflow: hidden;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                
                th, td {
                    border: 1px solid #dee2e6;
                    padding: 12px 15px;
                    text-align: left;
                }
                
                th {
                    background-color: #f8f9fa;
                    font-weight: 600;
                    color: #495057;
                }
                
                tr:nth-child(even) {
                    background-color: #f8f9fa;
                }
                
                /* Status indicators */
                .status-complete::before {
                    content: "✅ ";
                    color: #27ae60;
                }
                
                .status-warning::before {
                    content: "⚠️ ";
                    color: #f39c12;
                }
                
                .status-error::before {
                    content: "❌ ";
                    color: #e74c3c;
                }
                
                /* Statistics section */
                h2:contains("📊") + ul {
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #3498db;
                }
                
                /* Channel handles */
                strong:contains("@") {
                    color: #3498db;
                    font-weight: 700;
                }
                
                /* Horizontal rules */
                hr {
                    border: none;
                    height: 2px;
                    background: linear-gradient(90deg, #3498db, #ecf0f1);
                    margin: 30px 0;
                }
                
                /* Page breaks */
                .page-break {
                    page-break-before: always;
                }
                
                /* Footer */
                .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ecf0f1;
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 12px;
                }
                
                @media print {
                    body {
                        padding: 20px;
                    }
                    
                    h1, h2, h3, h4 {
                        page-break-after: avoid;
                    }
                    
                    ul, ol, blockquote {
                        page-break-inside: avoid;
                    }
                }
            </style>
        </head>
        <body>
        """ + html_content + """
        <div class="footer">
            Generated by Podcast Summary Tool | """ + f"PDF created from {title}" + """
        </div>
        </body>
        </html>
        """
        
        return css_styles
    
    def convert_multiple_files(self, md_files: List[str], output_dir: Optional[str] = None) -> Dict[str, bool]:
        """
        Convert multiple markdown files to PDF.
        
        Args:
            md_files: List of markdown file paths
            output_dir: Optional output directory for PDFs
            
        Returns:
            Dictionary mapping file paths to success status
        """
        results = {}
        
        if not md_files:
            logger.warning("No markdown files provided for conversion")
            return results
        
        logger.info(f"Converting {len(md_files)} markdown files to PDF...")
        
        for md_file in md_files:
            try:
                output_path = None
                if output_dir:
                    filename = Path(md_file).stem + '.pdf'
                    output_path = os.path.join(output_dir, filename)
                
                success = self.convert_markdown_to_pdf(md_file, output_path)
                results[md_file] = success
                
            except Exception as e:
                logger.error(f"Error converting {md_file}: {str(e)}")
                results[md_file] = False
        
        successful = sum(results.values())
        logger.info(f"PDF conversion complete: {successful}/{len(md_files)} files successful")
        
        return results
    
    def convert_directory(self, directory: str, pattern: str = "*.md") -> Dict[str, bool]:
        """
        Convert all markdown files in a directory to PDF.
        
        Args:
            directory: Directory path to search
            pattern: File pattern to match (default: "*.md")
            
        Returns:
            Dictionary mapping file paths to success status
        """
        try:
            md_files = glob.glob(os.path.join(directory, pattern))
            
            if not md_files:
                logger.warning(f"No markdown files found in {directory} matching {pattern}")
                return {}
            
            return self.convert_multiple_files(md_files)
            
        except Exception as e:
            logger.error(f"Error converting directory {directory}: {str(e)}")
            return {}


def main():
    """Command line entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert podcast summary markdown to PDF')
    parser.add_argument('files', nargs='*', help='Markdown files to convert')
    parser.add_argument('--dir', help='Directory to convert all markdown files')
    parser.add_argument('--output', help='Output directory for PDFs')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    converter = PodcastPDFConverter()
    
    if args.dir:
        # Convert all files in directory
        results = converter.convert_directory(args.dir)
    elif args.files:
        # Convert specified files
        results = converter.convert_multiple_files(args.files, args.output)
    else:
        # Convert all markdown files in current directory
        results = converter.convert_directory('.')
    
    # Print summary
    if results:
        successful = sum(results.values())
        total = len(results)
        print(f"\nConversion summary: {successful}/{total} files converted successfully")
        
        if successful < total:
            print("\nFailed conversions:")
            for file_path, success in results.items():
                if not success:
                    print(f"  ❌ {os.path.basename(file_path)}")
    else:
        print("No files were processed.")


if __name__ == "__main__":
    main()