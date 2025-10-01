"""Comprehensive error handling system with fallbacks and logging."""

import sys
import traceback
import logging
from typing import Any, Callable, Optional, Dict, List
from functools import wraps
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class PodcastSummaryError(Exception):
    """Base exception for podcast summary operations."""
    pass

class TranscriptExtractionError(PodcastSummaryError):
    """Error during transcript extraction."""
    pass

class AnalysisError(PodcastSummaryError):
    """Error during AI analysis."""
    pass

class OutputGenerationError(PodcastSummaryError):
    """Error during output generation."""
    pass

class ConfigurationError(PodcastSummaryError):
    """Error in configuration or setup."""
    pass

class ErrorHandler:
    """Centralized error handling with fallback strategies."""
    
    def __init__(self, log_file: Optional[str] = None):
        """Initialize error handler."""
        self.log_file = log_file
        self.error_counts = {
            'transcript_errors': 0,
            'analysis_errors': 0,
            'network_errors': 0,
            'configuration_errors': 0,
            'unknown_errors': 0
        }
        self.recent_errors = []
        self.max_recent_errors = 50
    
    def handle_error(self, error: Exception, context: str = "", 
                    operation: str = "unknown", channel: str = "", 
                    video_title: str = "") -> Dict[str, Any]:
        """
        Handle an error with comprehensive logging and categorization.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            operation: The operation that was being performed
            channel: Channel handle if applicable
            video_title: Video title if applicable
            
        Returns:
            Dictionary with error information and suggested fallbacks
        """
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'operation': operation,
            'channel': channel,
            'video_title': video_title,
            'traceback': traceback.format_exc(),
            'severity': self._categorize_error_severity(error),
            'category': self._categorize_error(error),
            'suggested_fallback': self._suggest_fallback(error, operation)
        }
        
        # Update error counts
        category = error_info['category']
        if category in self.error_counts:
            self.error_counts[category] += 1
        else:
            self.error_counts['unknown_errors'] += 1
        
        # Add to recent errors
        self.recent_errors.append(error_info)
        if len(self.recent_errors) > self.max_recent_errors:
            self.recent_errors.pop(0)
        
        # Log the error
        self._log_error(error_info)
        
        # Save to error log file if configured
        if self.log_file:
            self._save_error_to_file(error_info)
        
        return error_info
    
    def _categorize_error(self, error: Exception) -> str:
        """Categorize error for statistics and handling."""
        
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Network-related errors
        if any(keyword in error_message for keyword in 
               ['connection', 'timeout', 'network', 'dns', 'unreachable']):
            return 'network_errors'
        
        # Transcript-related errors
        if (isinstance(error, TranscriptExtractionError) or 
            any(keyword in error_message for keyword in 
                ['transcript', 'subtitle', 'caption', 'unavailable'])):
            return 'transcript_errors'
        
        # Analysis-related errors
        if (isinstance(error, AnalysisError) or
            any(keyword in error_message for keyword in 
                ['analysis', 'ai', 'claude', 'processing'])):
            return 'analysis_errors'
        
        # Configuration errors
        if (isinstance(error, ConfigurationError) or
            any(keyword in error_message for keyword in 
                ['config', 'setting', 'permission', 'access'])):
            return 'configuration_errors'
        
        return 'unknown_errors'
    
    def _categorize_error_severity(self, error: Exception) -> str:
        """Categorize error severity level."""
        
        error_message = str(error).lower()
        
        # Critical errors that stop execution
        if any(keyword in error_message for keyword in 
               ['permission denied', 'file not found', 'memory error', 'disk space']):
            return 'critical'
        
        # High severity - affects functionality but may have workarounds
        if any(keyword in error_message for keyword in 
               ['connection refused', 'authentication', 'rate limit']):
            return 'high'
        
        # Medium severity - affects specific operations
        if any(keyword in error_message for keyword in 
               ['timeout', 'not available', 'parsing error']):
            return 'medium'
        
        # Low severity - minor issues with fallbacks available
        return 'low'
    
    def _suggest_fallback(self, error: Exception, operation: str) -> str:
        """Suggest fallback strategies based on error type and operation."""
        
        error_message = str(error).lower()
        
        # Transcript extraction fallbacks
        if operation == 'transcript_extraction':
            if 'not available' in error_message or 'disabled' in error_message:
                return 'try_web_scraping_fallback'
            elif 'timeout' in error_message or 'connection' in error_message:
                return 'retry_with_delay'
            else:
                return 'skip_video_and_continue'
        
        # Analysis fallbacks
        elif operation == 'analysis':
            if 'timeout' in error_message:
                return 'chunk_content_smaller'
            elif 'rate limit' in error_message:
                return 'retry_with_exponential_backoff'
            else:
                return 'use_fallback_analysis'
        
        # Video extraction fallbacks
        elif operation == 'video_extraction':
            if 'not found' in error_message or 'unavailable' in error_message:
                return 'check_channel_handle'
            elif 'private' in error_message or 'restricted' in error_message:
                return 'skip_channel_and_continue'
            else:
                return 'retry_with_different_parameters'
        
        # PDF generation fallbacks
        elif operation == 'pdf_generation':
            if 'wkhtmltopdf' in error_message:
                return 'install_wkhtmltopdf_dependency'
            elif 'permission' in error_message:
                return 'check_output_directory_permissions'
            else:
                return 'skip_pdf_generation'
        
        # Generic fallbacks
        if 'network' in error_message or 'connection' in error_message:
            return 'retry_with_delay'
        elif 'memory' in error_message:
            return 'reduce_processing_batch_size'
        else:
            return 'log_error_and_continue'
    
    def _log_error(self, error_info: Dict[str, Any]):
        """Log error with appropriate severity level."""
        
        severity = error_info['severity']
        message = f"{error_info['operation']}: {error_info['error_message']}"
        
        if error_info['channel']:
            message = f"[@{error_info['channel']}] {message}"
        
        if error_info['context']:
            message = f"{message} | Context: {error_info['context']}"
        
        if severity == 'critical':
            logger.critical(message)
        elif severity == 'high':
            logger.error(message)
        elif severity == 'medium':
            logger.warning(message)
        else:
            logger.info(f"Minor issue: {message}")
    
    def _save_error_to_file(self, error_info: Dict[str, Any]):
        """Save error information to file for later analysis."""
        try:
            import os
            
            # Ensure error log directory exists
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            
            # Append error to log file
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_info, indent=2) + '\n')
                f.write('-' * 80 + '\n')
                
        except Exception as e:
            logger.error(f"Failed to save error to file: {str(e)}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics summary."""
        total_errors = sum(self.error_counts.values())
        
        return {
            'total_errors': total_errors,
            'error_breakdown': self.error_counts.copy(),
            'recent_error_count': len(self.recent_errors),
            'most_common_error': max(self.error_counts.keys(), 
                                   key=lambda x: self.error_counts[x]) if total_errors > 0 else None
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent error information."""
        return self.recent_errors[-limit:] if self.recent_errors else []
    
    def clear_error_history(self):
        """Clear error history and statistics."""
        self.recent_errors.clear()
        for key in self.error_counts:
            self.error_counts[key] = 0


def with_error_handling(operation: str = "unknown", reraise: bool = False):
    """Decorator for automatic error handling."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Try to get error handler from instance
                error_handler = None
                if args and hasattr(args[0], 'error_handler'):
                    error_handler = args[0].error_handler
                else:
                    error_handler = ErrorHandler()
                
                # Handle the error
                error_info = error_handler.handle_error(
                    e, 
                    context=f"Function: {func.__name__}",
                    operation=operation
                )
                
                if reraise:
                    raise
                else:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    return None
        
        return wrapper
    return decorator


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, 
                      backoff_factor: float = 2.0):
    """Decorator for retrying operations with exponential backoff."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries - 1:
                        # Last attempt, don't wait
                        break
                    
                    delay = base_delay * (backoff_factor ** attempt)
                    logger.info(f"Attempt {attempt + 1} failed, retrying in {delay:.1f}s...")
                    time.sleep(delay)
            
            # All retries failed, raise the last exception
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test error handler
    error_handler = ErrorHandler("logs/error_log.json")
    
    # Simulate different types of errors
    try:
        raise TranscriptExtractionError("Could not extract transcript from video")
    except Exception as e:
        error_handler.handle_error(e, "Test transcript extraction", 
                                 "transcript_extraction", "testchannel", "Test Video")
    
    try:
        raise ConnectionError("Connection timeout to YouTube")
    except Exception as e:
        error_handler.handle_error(e, "Test network error", 
                                 "video_extraction", "testchannel")
    
    # Get statistics
    stats = error_handler.get_error_statistics()
    print("Error Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Test decorator
    @with_error_handling(operation="test_operation")
    def failing_function():
        raise ValueError("This function always fails")
    
    result = failing_function()  # Will handle error and return None
    print(f"Function result: {result}")
    
    # Test retry decorator
    @retry_with_backoff(max_retries=3, base_delay=0.1)
    def sometimes_failing_function(success_on_attempt: int = 2):
        if not hasattr(sometimes_failing_function, 'attempt_count'):
            sometimes_failing_function.attempt_count = 0
        
        sometimes_failing_function.attempt_count += 1
        
        if sometimes_failing_function.attempt_count < success_on_attempt:
            raise ConnectionError(f"Failed on attempt {sometimes_failing_function.attempt_count}")
        
        return f"Success on attempt {sometimes_failing_function.attempt_count}"
    
    try:
        result = sometimes_failing_function(3)
        print(f"Retry result: {result}")
    except Exception as e:
        print(f"Retry failed: {str(e)}")