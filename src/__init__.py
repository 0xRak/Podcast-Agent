"""Podcast Summary Tool - Extract insights and alpha from YouTube podcasts."""

__version__ = "1.0.0"
__author__ = "Claude Code"
__description__ = "AI-powered podcast summary tool for extracting insights and actionable alpha"

from .podcast_summary import PodcastSummaryCommand, podcast_summary_slash_command

__all__ = ['PodcastSummaryCommand', 'podcast_summary_slash_command']