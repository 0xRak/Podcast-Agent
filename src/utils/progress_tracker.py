"""Progress tracking and status reporting for multi-channel processing."""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class ProgressTracker:
    """Track progress and status for podcast summary processing."""
    
    def __init__(self):
        """Initialize the progress tracker."""
        self.reset()
    
    def reset(self):
        """Reset all tracking state."""
        self.start_time = None
        self.end_time = None
        self.channels = []
        self.channel_status = {}
        self.channel_times = {}
        self.errors = []
        self.current_channel = None
        self.total_videos_processed = 0
        self.successful_analyses = 0
    
    def start_processing(self, channels: List[str]):
        """Start tracking processing for given channels."""
        self.reset()
        self.start_time = datetime.now()
        self.channels = channels.copy()
        
        # Initialize channel status
        for channel in channels:
            self.channel_status[channel] = {
                'status': 'pending',
                'start_time': None,
                'end_time': None,
                'videos_found': 0,
                'videos_processed': 0,
                'success': False,
                'error': None
            }
        
        logger.info(f"Started processing {len(channels)} channels")
        self._print_progress_header()
    
    def start_channel(self, channel: str):
        """Mark a channel as starting processing."""
        self.current_channel = channel
        
        if channel in self.channel_status:
            self.channel_status[channel]['status'] = 'processing'
            self.channel_status[channel]['start_time'] = datetime.now()
            
            logger.info(f"📺 Processing @{channel}...")
            self._update_progress_display()
    
    def complete_channel(self, channel: str, success: bool = True, 
                        error: Optional[str] = None, videos_processed: int = 0):
        """Mark a channel as completed."""
        if channel in self.channel_status:
            self.channel_status[channel]['status'] = 'completed'
            self.channel_status[channel]['end_time'] = datetime.now()
            self.channel_status[channel]['success'] = success
            self.channel_status[channel]['videos_processed'] = videos_processed
            
            if error:
                self.channel_status[channel]['error'] = error
                self.errors.append(f"@{channel}: {error}")
            
            if success:
                self.successful_analyses += videos_processed
                logger.info(f"✅ @{channel} completed successfully")
            else:
                logger.error(f"❌ @{channel} failed: {error}")
            
            self.total_videos_processed += videos_processed
            self._update_progress_display()
        
        self.current_channel = None
    
    def add_video_found(self, channel: str, count: int = 1):
        """Increment videos found count for a channel."""
        if channel in self.channel_status:
            self.channel_status[channel]['videos_found'] += count
    
    def finish_processing(self):
        """Mark overall processing as finished."""
        self.end_time = datetime.now()
        logger.info("Processing completed")
        self._print_final_summary()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        if not self.start_time:
            return {}
        
        end_time = self.end_time or datetime.now()
        total_time = end_time - self.start_time
        
        successful_channels = sum(1 for status in self.channel_status.values() 
                                if status['success'])
        
        return {
            'total_time': str(total_time).split('.')[0],  # Remove microseconds
            'total_channels': len(self.channels),
            'successful_channels': successful_channels,
            'failed_channels': len(self.channels) - successful_channels,
            'success_rate': f"{successful_channels}/{len(self.channels)}",
            'total_videos_processed': self.total_videos_processed,
            'successful_analyses': self.successful_analyses,
            'errors': len(self.errors)
        }
    
    def get_current_status(self) -> str:
        """Get current processing status as a string."""
        if not self.start_time:
            return "Not started"
        
        if self.end_time:
            return "Completed"
        
        completed = sum(1 for status in self.channel_status.values() 
                       if status['status'] == 'completed')
        
        if self.current_channel:
            return f"Processing @{self.current_channel} ({completed}/{len(self.channels)} channels done)"
        else:
            return f"{completed}/{len(self.channels)} channels completed"
    
    def _print_progress_header(self):
        """Print the initial progress header."""
        print("\n" + "="*60)
        print("🎙️  PODCAST SUMMARY PROCESSING")
        print("="*60)
        print(f"Channels: {', '.join(['@' + ch for ch in self.channels])}")
        print(f"Started: {self.start_time.strftime('%H:%M:%S')}")
        print("-"*60)
    
    def _update_progress_display(self):
        """Update the progress display."""
        completed = sum(1 for status in self.channel_status.values() 
                       if status['status'] == 'completed')
        
        # Calculate progress bar
        progress = completed / len(self.channels) if self.channels else 0
        bar_length = 30
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"\r[{bar}] {completed}/{len(self.channels)} channels", end="", flush=True)
        
        if completed == len(self.channels):
            print()  # New line when complete
    
    def _print_final_summary(self):
        """Print the final processing summary."""
        if not self.start_time or not self.end_time:
            return
        
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("📊 PROCESSING SUMMARY")
        print("="*60)
        
        # Time and performance
        print(f"⏱️  Total Time: {stats['total_time']}")
        print(f"📺 Channels: {stats['successful_channels']}/{stats['total_channels']} successful")
        print(f"🎥 Videos: {stats['total_videos_processed']} processed, {stats['successful_analyses']} analyzed")
        
        # Success breakdown
        print("\n📋 Channel Results:")
        for channel, status in self.channel_status.items():
            if status['success']:
                duration = self._calculate_channel_duration(status)
                print(f"  ✅ @{channel} - {status['videos_processed']} videos ({duration})")
            else:
                error = status.get('error', 'Unknown error')
                print(f"  ❌ @{channel} - Failed: {error}")
        
        # Errors summary
        if self.errors:
            print(f"\n⚠️  Errors Encountered: {len(self.errors)}")
            for error in self.errors[:3]:  # Show first 3 errors
                print(f"  • {error}")
            if len(self.errors) > 3:
                print(f"  • ... and {len(self.errors) - 3} more")
        
        print("="*60)
    
    def _calculate_channel_duration(self, status: Dict[str, Any]) -> str:
        """Calculate processing duration for a channel."""
        if not status.get('start_time') or not status.get('end_time'):
            return "Unknown"
        
        duration = status['end_time'] - status['start_time']
        seconds = int(duration.total_seconds())
        
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def get_channel_progress(self, channel: str) -> Dict[str, Any]:
        """Get progress information for a specific channel."""
        return self.channel_status.get(channel, {})
    
    def is_processing_complete(self) -> bool:
        """Check if all processing is complete."""
        if not self.channels:
            return False
        
        return all(status['status'] == 'completed' 
                  for status in self.channel_status.values())
    
    def get_estimated_time_remaining(self) -> Optional[str]:
        """Estimate remaining processing time based on completed channels."""
        if not self.start_time or not self.channels:
            return None
        
        completed_channels = [ch for ch, status in self.channel_status.items() 
                            if status['status'] == 'completed']
        
        if not completed_channels:
            return None
        
        # Calculate average time per channel
        total_completed_time = timedelta()
        for channel in completed_channels:
            status = self.channel_status[channel]
            if status.get('start_time') and status.get('end_time'):
                total_completed_time += status['end_time'] - status['start_time']
        
        if completed_channels:
            avg_time_per_channel = total_completed_time / len(completed_channels)
            remaining_channels = len(self.channels) - len(completed_channels)
            
            if self.current_channel and self.current_channel in self.channel_status:
                current_status = self.channel_status[self.current_channel]
                if current_status.get('start_time'):
                    elapsed_current = datetime.now() - current_status['start_time']
                    remaining_current = max(timedelta(), avg_time_per_channel - elapsed_current)
                    estimated_remaining = remaining_current + (avg_time_per_channel * (remaining_channels - 1))
                else:
                    estimated_remaining = avg_time_per_channel * remaining_channels
            else:
                estimated_remaining = avg_time_per_channel * remaining_channels
            
            total_seconds = int(estimated_remaining.total_seconds())
            
            if total_seconds < 60:
                return f"{total_seconds}s"
            elif total_seconds < 3600:
                minutes = total_seconds // 60
                return f"{minutes}m"
            else:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                return f"{hours}h {minutes}m"
        
        return None


# Example usage for testing
if __name__ == "__main__":
    import time
    
    logging.basicConfig(level=logging.INFO)
    
    # Test the progress tracker
    tracker = ProgressTracker()
    
    channels = ['lexfridman', 'joerogan', 'naval']
    
    # Start processing
    tracker.start_processing(channels)
    
    # Simulate processing each channel
    for i, channel in enumerate(channels):
        tracker.start_channel(channel)
        
        # Simulate some processing time
        time.sleep(1)
        
        # Mark as completed
        success = i != 1  # Make second channel fail for testing
        error = "Connection timeout" if not success else None
        videos_processed = 0 if not success else 1
        
        tracker.complete_channel(channel, success=success, error=error, 
                               videos_processed=videos_processed)
        
        time.sleep(0.5)
    
    # Finish processing
    tracker.finish_processing()
    
    # Print statistics
    stats = tracker.get_statistics()
    print(f"\nFinal stats: {stats}")