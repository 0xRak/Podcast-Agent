"""Content chunker for handling long transcripts within Claude's context limits."""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import deque

logger = logging.getLogger(__name__)

class ContentChunker:
    """Intelligently chunk long transcripts for AI processing."""
    
    def __init__(self, max_chunk_size: int = 8000, overlap_size: int = 500):
        """
        Initialize the content chunker.
        
        Args:
            max_chunk_size: Maximum characters per chunk
            overlap_size: Number of characters to overlap between chunks
        """
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.sentence_endings = r'[.!?]\s+'
        self.paragraph_breaks = r'\n\s*\n'
    
    def chunk_transcript(self, transcript: str, preserve_context: bool = True) -> List[Dict[str, Any]]:
        """
        Chunk a transcript into manageable pieces for AI processing.
        
        Args:
            transcript: The full transcript text
            preserve_context: Whether to preserve conversation context between chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        try:
            if len(transcript) <= self.max_chunk_size:
                return [{
                    'chunk_id': 1,
                    'text': transcript,
                    'start_char': 0,
                    'end_char': len(transcript),
                    'word_count': len(transcript.split()),
                    'is_complete': True
                }]
            
            logger.info(f"Chunking transcript of {len(transcript)} characters")
            
            if preserve_context:
                chunks = self._chunk_with_context_preservation(transcript)
            else:
                chunks = self._chunk_simple(transcript)
            
            # Add metadata to chunks
            enhanced_chunks = []
            for i, chunk in enumerate(chunks):
                enhanced_chunk = {
                    'chunk_id': i + 1,
                    'text': chunk['text'],
                    'start_char': chunk['start_char'],
                    'end_char': chunk['end_char'],
                    'word_count': len(chunk['text'].split()),
                    'char_count': len(chunk['text']),
                    'is_complete': chunk.get('is_complete', False),
                    'has_overlap': chunk.get('has_overlap', False),
                    'context_preserved': preserve_context
                }
                enhanced_chunks.append(enhanced_chunk)
            
            logger.info(f"Created {len(enhanced_chunks)} chunks")
            return enhanced_chunks
            
        except Exception as e:
            logger.error(f"Error chunking transcript: {str(e)}")
            # Return single chunk as fallback
            return [{
                'chunk_id': 1,
                'text': transcript,
                'start_char': 0,
                'end_char': len(transcript),
                'word_count': len(transcript.split()),
                'is_complete': True,
                'error': str(e)
            }]
    
    def _chunk_with_context_preservation(self, transcript: str) -> List[Dict[str, str]]:
        """Chunk transcript while preserving conversational context."""
        
        # First, split by paragraphs to find natural breaks
        paragraphs = re.split(self.paragraph_breaks, transcript)
        
        chunks = []
        current_chunk = ""
        current_start = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check if adding this paragraph would exceed limit
            test_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if len(test_chunk) <= self.max_chunk_size:
                current_chunk = test_chunk
            else:
                # Current paragraph is too large, need to split
                if current_chunk:
                    # Save current chunk
                    chunks.append({
                        'text': current_chunk,
                        'start_char': current_start,
                        'end_char': current_start + len(current_chunk),
                        'is_complete': True
                    })
                    current_start += len(current_chunk)
                
                # Handle large paragraph by splitting on sentences
                if len(paragraph) > self.max_chunk_size:
                    sentence_chunks = self._split_large_paragraph(paragraph, current_start)
                    chunks.extend(sentence_chunks)
                    current_start = chunks[-1]['end_char']
                    current_chunk = ""
                else:
                    current_chunk = paragraph
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                'text': current_chunk,
                'start_char': current_start,
                'end_char': current_start + len(current_chunk),
                'is_complete': True
            })
        
        # Add overlap between chunks if specified
        if self.overlap_size > 0:
            chunks = self._add_overlap_to_chunks(chunks, transcript)
        
        return chunks
    
    def _split_large_paragraph(self, paragraph: str, start_pos: int) -> List[Dict[str, str]]:
        """Split a large paragraph into sentence-based chunks."""
        
        sentences = re.split(self.sentence_endings, paragraph)
        chunks = []
        current_chunk = ""
        current_start = start_pos
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Add sentence ending back (except for last sentence)
            if i < len(sentences) - 1:
                sentence += ". "
            
            test_chunk = current_chunk + sentence
            
            if len(test_chunk) <= self.max_chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append({
                        'text': current_chunk,
                        'start_char': current_start,
                        'end_char': current_start + len(current_chunk),
                        'is_complete': False
                    })
                    current_start += len(current_chunk)
                
                # If single sentence is too long, split by words
                if len(sentence) > self.max_chunk_size:
                    word_chunks = self._split_by_words(sentence, current_start)
                    chunks.extend(word_chunks)
                    current_start = chunks[-1]['end_char']
                    current_chunk = ""
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append({
                'text': current_chunk,
                'start_char': current_start,
                'end_char': current_start + len(current_chunk),
                'is_complete': False
            })
        
        return chunks
    
    def _split_by_words(self, text: str, start_pos: int) -> List[Dict[str, str]]:
        """Split text by words when sentences are too long."""
        
        words = text.split()
        chunks = []
        current_chunk = ""
        current_start = start_pos
        
        for word in words:
            test_chunk = current_chunk + " " + word if current_chunk else word
            
            if len(test_chunk) <= self.max_chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append({
                        'text': current_chunk,
                        'start_char': current_start,
                        'end_char': current_start + len(current_chunk),
                        'is_complete': False
                    })
                    current_start += len(current_chunk)
                
                current_chunk = word
        
        if current_chunk:
            chunks.append({
                'text': current_chunk,
                'start_char': current_start,
                'end_char': current_start + len(current_chunk),
                'is_complete': False
            })
        
        return chunks
    
    def _chunk_simple(self, transcript: str) -> List[Dict[str, str]]:
        """Simple chunking without context preservation."""
        
        chunks = []
        current_pos = 0
        chunk_id = 1
        
        while current_pos < len(transcript):
            end_pos = min(current_pos + self.max_chunk_size, len(transcript))
            
            # Try to end at a sentence boundary
            if end_pos < len(transcript):
                # Look for sentence ending within last 200 characters
                search_start = max(end_pos - 200, current_pos)
                sentence_match = None
                
                for match in re.finditer(self.sentence_endings, transcript[search_start:end_pos]):
                    sentence_match = match
                
                if sentence_match:
                    end_pos = search_start + sentence_match.end()
            
            chunk_text = transcript[current_pos:end_pos].strip()
            
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'start_char': current_pos,
                    'end_char': end_pos,
                    'is_complete': end_pos == len(transcript)
                })
            
            current_pos = end_pos
        
        return chunks
    
    def _add_overlap_to_chunks(self, chunks: List[Dict[str, str]], full_transcript: str) -> List[Dict[str, str]]:
        """Add overlap between consecutive chunks."""
        
        if len(chunks) <= 1 or self.overlap_size <= 0:
            return chunks
        
        overlapped_chunks = [chunks[0]]  # First chunk unchanged
        
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            current_chunk = chunks[i]
            
            # Get overlap text from end of previous chunk
            overlap_start = max(0, len(prev_chunk['text']) - self.overlap_size)
            overlap_text = prev_chunk['text'][overlap_start:]
            
            # Find good break point in overlap
            sentences = re.split(self.sentence_endings, overlap_text)
            if len(sentences) > 1:
                overlap_text = sentences[-1]  # Take last partial sentence
            
            # Combine overlap with current chunk
            combined_text = overlap_text + "\n\n[... continuing ...]\n\n" + current_chunk['text']
            
            overlapped_chunk = {
                'text': combined_text,
                'start_char': current_chunk['start_char'] - len(overlap_text),
                'end_char': current_chunk['end_char'],
                'is_complete': current_chunk['is_complete'],
                'has_overlap': True,
                'overlap_size': len(overlap_text)
            }
            
            overlapped_chunks.append(overlapped_chunk)
        
        return overlapped_chunks
    
    def merge_chunk_analyses(self, chunk_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge analyses from multiple chunks into a cohesive summary.
        
        Args:
            chunk_analyses: List of analysis results from individual chunks
            
        Returns:
            Merged analysis combining insights from all chunks
        """
        try:
            if not chunk_analyses:
                return {}
            
            if len(chunk_analyses) == 1:
                return chunk_analyses[0]['analysis']
            
            logger.info(f"Merging analyses from {len(chunk_analyses)} chunks")
            
            # Initialize merged analysis structure
            merged = {
                'main_alpha': [],
                'key_insights': [],
                'actionable_takeaways': [],
                'key_quotes': [],
                'content_category': 'general',
                'main_topics': [],
                'confidence_score': 0.0
            }
            
            # Collect all insights from chunks
            all_alpha = []
            all_insights = []
            all_takeaways = []
            all_quotes = []
            all_topics = []
            confidence_scores = []
            
            for chunk_analysis in chunk_analyses:
                analysis = chunk_analysis.get('analysis', {})
                
                all_alpha.extend(analysis.get('main_alpha', []))
                all_insights.extend(analysis.get('key_insights', []))
                all_takeaways.extend(analysis.get('actionable_takeaways', []))
                all_quotes.extend(analysis.get('key_quotes', []))
                all_topics.extend(analysis.get('main_topics', []))
                
                if analysis.get('confidence_score', 0) > 0:
                    confidence_scores.append(analysis['confidence_score'])
            
            # Deduplicate and prioritize insights
            merged['main_alpha'] = self._deduplicate_and_rank(all_alpha, max_items=5)
            merged['key_insights'] = self._deduplicate_and_rank(all_insights, max_items=6)
            merged['actionable_takeaways'] = self._deduplicate_and_rank(all_takeaways, max_items=6)
            merged['key_quotes'] = self._deduplicate_and_rank(all_quotes, max_items=4)
            
            # Merge topics and get most common category
            topic_counts = {}
            for topic in all_topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            merged['main_topics'] = sorted(topic_counts.keys(), key=lambda x: topic_counts[x], reverse=True)[:5]
            
            # Calculate average confidence
            if confidence_scores:
                merged['confidence_score'] = sum(confidence_scores) / len(confidence_scores)
            
            # Determine primary content category
            categories = [chunk_analysis.get('analysis', {}).get('content_category', 'general') 
                         for chunk_analysis in chunk_analyses]
            category_counts = {}
            for cat in categories:
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            merged['content_category'] = max(category_counts.keys(), key=lambda x: category_counts[x])
            
            logger.info("Successfully merged chunk analyses")
            return merged
            
        except Exception as e:
            logger.error(f"Error merging chunk analyses: {str(e)}")
            # Return analysis from first chunk as fallback
            return chunk_analyses[0].get('analysis', {}) if chunk_analyses else {}
    
    def _deduplicate_and_rank(self, items: List[str], max_items: int = 5) -> List[str]:
        """Remove duplicates and rank items by quality/relevance."""
        
        if not items:
            return []
        
        # Simple deduplication by lowercased similarity
        unique_items = []
        seen_lower = set()
        
        for item in items:
            item_lower = item.lower().strip()
            # Check for substantial similarity (not just exact match)
            is_duplicate = False
            
            for seen_item in seen_lower:
                # Simple similarity check - if 80%+ of words overlap
                words1 = set(item_lower.split())
                words2 = set(seen_item.split())
                
                if len(words1) > 0 and len(words2) > 0:
                    overlap = len(words1.intersection(words2))
                    similarity = overlap / max(len(words1), len(words2))
                    
                    if similarity > 0.8:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_items.append(item)
                seen_lower.add(item_lower)
        
        # Rank by length and content quality (longer, more specific items first)
        ranked_items = sorted(unique_items, key=lambda x: (len(x.split()), len(x)), reverse=True)
        
        return ranked_items[:max_items]


# Example usage for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    chunker = ContentChunker(max_chunk_size=1000, overlap_size=100)
    
    # Test with sample long transcript
    sample_transcript = """
    This is a sample long transcript that would exceed the maximum chunk size.
    
    In this podcast, we discuss various topics including artificial intelligence,
    business strategy, and investment opportunities. The conversation covers
    multiple insights and actionable takeaways for entrepreneurs and investors.
    
    One key insight is about the importance of specific knowledge and how it
    creates leverage in the modern economy. Naval Ravikant often talks about
    this concept and how wealth is created through assets that earn while you sleep.
    
    Another important topic is the role of technology in disrupting traditional
    industries. We see this happening across sectors from finance to healthcare
    to education. The key is to identify these trends early and position yourself
    accordingly.
    
    From an investment perspective, there are several alpha opportunities in
    emerging technologies. These include areas like AI infrastructure, quantum
    computing, and decentralized finance protocols.
    """ * 10  # Repeat to make it long enough for chunking
    
    # Test chunking
    chunks = chunker.chunk_transcript(sample_transcript, preserve_context=True)
    
    print(f"Original length: {len(sample_transcript)} characters")
    print(f"Number of chunks: {len(chunks)}")
    
    for chunk in chunks[:3]:  # Show first 3 chunks
        print(f"\nChunk {chunk['chunk_id']}:")
        print(f"  Length: {chunk['char_count']} chars, {chunk['word_count']} words")
        print(f"  Complete: {chunk['is_complete']}")
        print(f"  Text preview: {chunk['text'][:100]}...")