"""Configuration manager for handling channels.yaml and settings.yaml files."""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manage configuration files for the podcast summary tool."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize the configuration manager."""
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.channels_file = self.config_dir / "channels.yaml"
        self.settings_file = self.config_dir / "settings.yaml"
        
        # Initialize default configurations if files don't exist
        self._ensure_default_configs()
    
    def _ensure_default_configs(self):
        """Create default configuration files if they don't exist."""
        if not self.channels_file.exists():
            self._create_default_channels_config()
        
        if not self.settings_file.exists():
            self._create_default_settings_config()
    
    def _create_default_channels_config(self):
        """Create default channels.yaml configuration."""
        default_channels = {
            'default_settings': {
                'days_lookback': 7,
                'videos_per_channel': 1,
                'output_directory': 'podcast_summaries'
            },
            'channels': {
                'lexfridman': {
                    'display_name': 'Lex Fridman Podcast',
                    'url': 'https://www.youtube.com/@lexfridman',
                    'category': 'tech',
                    'priority': 'high',
                    'enabled': True,
                    'last_processed': None
                },
                'joerogan': {
                    'display_name': 'The Joe Rogan Experience',
                    'url': 'https://www.youtube.com/@joerogan',
                    'category': 'general',
                    'priority': 'medium',
                    'enabled': True,
                    'last_processed': None
                },
                'naval': {
                    'display_name': 'Naval',
                    'url': 'https://www.youtube.com/@naval',
                    'category': 'business',
                    'priority': 'high',
                    'enabled': True,
                    'last_processed': None
                },
                'allinchamath': {
                    'display_name': 'All-In with Chamath, Jason, Sacks & Friedberg',
                    'url': 'https://www.youtube.com/@allinchamath',
                    'category': 'business',
                    'priority': 'high',
                    'enabled': True,
                    'last_processed': None
                },
                'davidperell': {
                    'display_name': 'David Perell',
                    'url': 'https://www.youtube.com/@davidperell',
                    'category': 'education',
                    'priority': 'medium',
                    'enabled': True,
                    'last_processed': None
                }
            }
        }
        
        self._save_yaml(self.channels_file, default_channels)
        logger.info(f"Created default channels configuration at {self.channels_file}")
    
    def _create_default_settings_config(self):
        """Create default settings.yaml configuration."""
        default_settings = {
            'processing': {
                'max_transcript_length': 50000,
                'chunk_size': 8000,
                'concurrent_channels': 3,
                'retry_attempts': 3,
                'retry_delay': 5
            },
            'output': {
                'include_timestamps': True,
                'include_video_metadata': True,
                'pdf_styling': 'professional',
                'filename_format': 'youtube-research-{date}.md',
                'max_summary_length': 2000
            },
            'ai_analysis': {
                'focus_areas': ['insights', 'alpha', 'actionable_takeaways'],
                'summary_length': 'detailed',
                'include_quotes': True,
                'extract_timestamps': False,
                'confidence_threshold': 0.7
            },
            'logging': {
                'level': 'INFO',
                'log_to_file': True,
                'log_file': 'logs/podcast_summary.log'
            }
        }
        
        self._save_yaml(self.settings_file, default_settings)
        logger.info(f"Created default settings configuration at {self.settings_file}")
    
    def load_channels_config(self) -> Dict[str, Any]:
        """Load channels configuration."""
        try:
            return self._load_yaml(self.channels_file)
        except Exception as e:
            logger.error(f"Error loading channels config: {str(e)}")
            return {}
    
    def load_settings_config(self) -> Dict[str, Any]:
        """Load settings configuration."""
        try:
            return self._load_yaml(self.settings_file)
        except Exception as e:
            logger.error(f"Error loading settings config: {str(e)}")
            return {}
    
    def save_channels_config(self, config: Dict[str, Any]):
        """Save channels configuration."""
        try:
            self._save_yaml(self.channels_file, config)
            logger.info("Channels configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving channels config: {str(e)}")
    
    def save_settings_config(self, config: Dict[str, Any]):
        """Save settings configuration."""
        try:
            self._save_yaml(self.settings_file, config)
            logger.info("Settings configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving settings config: {str(e)}")
    
    def get_channel_config(self, channel_handle: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific channel."""
        channels_config = self.load_channels_config()
        channels = channels_config.get('channels', {})
        
        # Remove @ prefix if present
        channel_handle = channel_handle.lstrip('@')
        
        return channels.get(channel_handle)
    
    def add_channel(self, handle: str, display_name: str, category: str = 'general', 
                   priority: str = 'medium', enabled: bool = True) -> bool:
        """Add a new channel to the configuration."""
        try:
            channels_config = self.load_channels_config()
            
            # Remove @ prefix if present
            handle = handle.lstrip('@')
            
            if handle in channels_config.get('channels', {}):
                logger.warning(f"Channel {handle} already exists")
                return False
            
            new_channel = {
                'display_name': display_name,
                'url': f'https://www.youtube.com/@{handle}',
                'category': category,
                'priority': priority,
                'enabled': enabled,
                'last_processed': None
            }
            
            if 'channels' not in channels_config:
                channels_config['channels'] = {}
            
            channels_config['channels'][handle] = new_channel
            self.save_channels_config(channels_config)
            
            logger.info(f"Added channel {handle} ({display_name})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding channel {handle}: {str(e)}")
            return False
    
    def update_channel_last_processed(self, channel_handle: str, timestamp: str):
        """Update the last processed timestamp for a channel."""
        try:
            channels_config = self.load_channels_config()
            channel_handle = channel_handle.lstrip('@')
            
            if channel_handle in channels_config.get('channels', {}):
                channels_config['channels'][channel_handle]['last_processed'] = timestamp
                self.save_channels_config(channels_config)
                logger.debug(f"Updated last processed time for {channel_handle}: {timestamp}")
            else:
                logger.warning(f"Channel {channel_handle} not found in configuration")
                
        except Exception as e:
            logger.error(f"Error updating last processed time for {channel_handle}: {str(e)}")
    
    def get_enabled_channels(self) -> List[str]:
        """Get list of enabled channel handles."""
        channels_config = self.load_channels_config()
        channels = channels_config.get('channels', {})
        
        enabled_channels = []
        for handle, config in channels.items():
            if config.get('enabled', True):
                enabled_channels.append(handle)
        
        return enabled_channels
    
    def get_channels_by_category(self, category: str) -> List[str]:
        """Get channels filtered by category."""
        channels_config = self.load_channels_config()
        channels = channels_config.get('channels', {})
        
        filtered_channels = []
        for handle, config in channels.items():
            if config.get('category') == category and config.get('enabled', True):
                filtered_channels.append(handle)
        
        return filtered_channels
    
    def get_channels_by_priority(self, priority: str) -> List[str]:
        """Get channels filtered by priority."""
        channels_config = self.load_channels_config()
        channels = channels_config.get('channels', {})
        
        filtered_channels = []
        for handle, config in channels.items():
            if config.get('priority') == priority and config.get('enabled', True):
                filtered_channels.append(handle)
        
        return filtered_channels
    
    def get_setting(self, key_path: str, default=None):
        """Get a specific setting using dot notation (e.g., 'processing.max_transcript_length')."""
        settings = self.load_settings_config()
        
        keys = key_path.split('.')
        current = settings
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or {}
    
    def _save_yaml(self, file_path: Path, data: Dict[str, Any]):
        """Save data to YAML file."""
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, default_flow_style=False, indent=2, allow_unicode=True)


# Example usage for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create config manager and test basic functionality
    config_manager = ConfigManager()
    
    # Test loading configurations
    channels = config_manager.load_channels_config()
    settings = config_manager.load_settings_config()
    
    print("Channels configuration:")
    for handle, config in channels.get('channels', {}).items():
        print(f"  {handle}: {config['display_name']} ({config['category']})")
    
    print(f"\nEnabled channels: {config_manager.get_enabled_channels()}")
    print(f"Tech channels: {config_manager.get_channels_by_category('tech')}")
    print(f"High priority channels: {config_manager.get_channels_by_priority('high')}")
    
    # Test getting specific settings
    print(f"\nMax transcript length: {config_manager.get_setting('processing.max_transcript_length')}")
    print(f"Include timestamps: {config_manager.get_setting('output.include_timestamps')}")