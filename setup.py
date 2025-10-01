#!/usr/bin/env python3
"""Setup script for Podcast Summary Tool."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="podcast-summary-tool",
    version="1.0.0",
    author="Claude Code",
    author_email="noreply@anthropic.com",
    description="AI-powered podcast summary tool for extracting insights and actionable alpha",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anthropics/claude-code",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video :: Analysis",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "podcast-summary=podcast_summary:main",
            "podcast-pdf=converters.md_to_pdf:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.yaml", "spec/*.md"],
    },
    keywords="podcast ai analysis youtube transcription claude insights alpha",
    project_urls={
        "Documentation": "https://docs.anthropic.com/en/docs/claude-code",
        "Source": "https://github.com/anthropics/claude-code",
        "Tracker": "https://github.com/anthropics/claude-code/issues",
    },
)