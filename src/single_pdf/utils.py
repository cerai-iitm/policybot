from typing import List, Dict, Any
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.documents import Document
from langchain.embeddings import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)

# Original chunking function (commented out)
# def chunk_text(text: str, source_name: str, chunk_size: int, chunk_overlap: int = 100) -> List[Dict[str, Any]]:
#     """Split text into chunks with metadata and overlapping content for better context retrieval."""
#     words = text.split()
#     chunks = []
#     chunk_number = 1
#     i = 0
# 
#     while i < len(words):
#         # Calculate end position with overlap
#         end_pos = min(i + chunk_size, len(words))
#         
#         # Create current chunk
#         chunk_text = " ".join(words[i:end_pos])
#         chunks.append({
#             "name": f"{source_name}_chunk_{chunk_number}",
#             "column": "Semantic",
#             "properties": {
#                 "content": chunk_text,
#                 "source": source_name,
#                 "chunk_number": chunk_number,
#             },
#             "relationships": {
#                 "part_of": [source_name],
#                 "next_chunk": (
#                     [f"{source_name}_chunk_{chunk_number + 1}"]
#                     if end_pos < len(words)
#                     else []
#                 )
#             }
#         })
#         
#         # Move to next chunk with overlap
#         i += (chunk_size - chunk_overlap)
#         if i < 0:  # Safeguard against potential negative indices
#             i = 0
#         chunk_number += 1
# 
#     return chunks

def chunk_text(text: str, source_name: str, chunk_size: int = 500, chunk_overlap: int = 75) -> List[Dict[str, Any]]:
    """Split text into semantic chunks with metadata for better context retrieval.
    
    Uses SemanticChunker to break text into semantically coherent pieces.
    """
    try:
        # Convert to a Document for semantic chunking
        doc = Document(page_content=text, metadata={"source": source_name})
        
        # Use HuggingFace embeddings model
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en")
        
        # Create semantic text splitter
        text_splitter = SemanticChunker(
            embeddings=embeddings,
            buffer_size=2,
            add_start_index=True,
            breakpoint_threshold_type="gradient",
            breakpoint_threshold_amount=0.8,
            sentence_split_regex=r"(?<=[.!?])\s+"
        )
        
        # Split the document
        split_docs = text_splitter.split_documents([doc])
        
        # Create chunks in the expected format
        chunks = []
        for i, split_doc in enumerate(split_docs, 1):
            chunks.append({
                "name": f"{source_name}_chunk_{i}",
                "column": "Semantic",
                "properties": {
                    "content": split_doc.page_content,
                    "source": source_name,
                    "chunk_number": i,
                },
                "relationships": {
                    "part_of": [source_name],
                    "next_chunk": (
                        [f"{source_name}_chunk_{i + 1}"]
                        if i < len(split_docs)
                        else []
                    )
                }
            })
        
        logger.info(f"Created {len(chunks)} semantic chunks from document {source_name}")
        return chunks
    
    except Exception as e:
        logger.error(f"Error in semantic chunking: {str(e)}")
        
        # Fallback to simple chunking if semantic chunking fails
        words = text.split()
        chunks = []
        chunk_number = 1
        i = 0
        
        # Target size of 500 words with 75 words overlap
        chunk_size_fallback = 500 if chunk_size < 400 or chunk_size > 600 else chunk_size
        chunk_overlap_fallback = 75 if chunk_overlap < 50 or chunk_overlap > 100 else chunk_overlap
        
        logger.warning(f"Falling back to simple chunking with size={chunk_size_fallback}, overlap={chunk_overlap_fallback}")

        while i < len(words):
            # Calculate end position with overlap
            end_pos = min(i + chunk_size_fallback, len(words))
            
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
            i += (chunk_size_fallback - chunk_overlap_fallback)
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