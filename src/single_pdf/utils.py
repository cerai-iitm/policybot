from typing import List, Dict, Any

def chunk_text(text: str, source_name: str, chunk_size: int, chunk_overlap: int = 100) -> List[Dict[str, Any]]:
    """Split text into chunks with metadata and overlapping content for better context retrieval."""
    words = text.split()
    chunks = []
    chunk_number = 1
    i = 0

    while i < len(words):
        # Calculate end position with overlap
        end_pos = min(i + chunk_size, len(words))
        
        # Create current chunk
        chunk_text = " ".join(words[i:end_pos])
        chunks.append({
            "name": f"{source_name}_chunk_{chunk_number}",
            "column": "Semantic",
            "properties": {
                "content": chunk_text,
                "source": source_name,
                "chunk_number": chunk_number,
            },
            "relationships": {
                "part_of": [source_name],
                "next_chunk": (
                    [f"{source_name}_chunk_{chunk_number + 1}"]
                    if end_pos < len(words)
                    else []
                )
            }
        })
        
        # Move to next chunk with overlap
        i += (chunk_size - chunk_overlap)
        if i < 0:  # Safeguard against potential negative indices
            i = 0
        chunk_number += 1

    return chunks

def is_readable(text: str) -> bool:
    """Check if text is readable (contains valid characters)."""
    if not text:
        return False

    # Count valid characters (letters, numbers, punctuation)
    valid_chars = sum(1 for c in text if c.isalnum() or c.isspace() or c in '.,!?-:;()[]{}')
    total_chars = len(text)

    # Text is readable if at least 80% of characters are valid
    return valid_chars / total_chars >= 0.8 if total_chars > 0 else False