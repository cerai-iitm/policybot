from sentence_transformers import CrossEncoder
from rank_bm25 import BM25Okapi
import numpy as np
from typing import List
from langchain_core.documents import Document
from langchain_ollama import OllamaLLM
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from ..config.settings import MODEL_NAME, MIN_SIMILARITY_SCORE

model = OllamaLLM(model=MODEL_NAME)

def create_document_map(documents):
    """Create a mapping of document content to their index"""
    return {doc.page_content: (i, doc) for i, doc in enumerate(documents)}

def calculate_similarity(query: str, doc_text: str) -> float:
    """Calculate semantic similarity between query and document"""
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([query, doc_text])
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except:
        return 0.0

def filter_relevant_context(query: str, documents: list) -> list:
    """Filter and rank documents by relevance to query"""
    scored_docs = []
    for doc in documents:
        # Calculate semantic similarity
        semantic_score = calculate_similarity(query, doc.page_content)
        # Calculate keyword overlap
        query_words = set(query.lower().split())
        doc_words = set(doc.page_content.lower().split())
        keyword_score = len(query_words & doc_words) / len(query_words) if query_words else 0
        # Combine scores
        combined_score = (semantic_score + keyword_score) / 2
        if combined_score >= MIN_SIMILARITY_SCORE:
            scored_docs.append((combined_score, doc))
    
    return [doc for score, doc in sorted(scored_docs, reverse=True)]

def hybrid_search(query: str, documents: List[Document], vectorstore, alpha: float = 0.5):
    """Modified hybrid search that works with InMemoryVectorStore"""
    # Create document mapping
    doc_map = create_document_map(documents)
    
    # Get embeddings directly from the embeddings model
    query_embedding = vectorstore.embeddings.embed_query(query)
    
    # Semantic search using regular similarity search
    semantic_results = vectorstore.similarity_search(query, k=15)  # Increased from 10
    
    # Calculate semantic scores using embeddings
    doc_embeddings = [
        vectorstore.embeddings.embed_query(doc.page_content) 
        for doc in semantic_results
    ]
    
    # Convert to numpy arrays for cosine similarity
    query_embedding = np.array(query_embedding).reshape(1, -1)
    doc_embeddings = np.array(doc_embeddings)
    
    # Calculate cosine similarity
    semantic_scores = np.dot(query_embedding, doc_embeddings.T)[0]
    semantic_scores = (semantic_scores + 1) / 2  # Normalize to 0-1 range
    
    # BM25 search
    text_corpus = [doc.page_content for doc in documents]
    tokenized_corpus = [text.lower().split() for text in text_corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    
    # Normalize BM25 scores to 0-1 range
    if len(bm25_scores) > 0:
        bm25_scores = (bm25_scores - np.min(bm25_scores)) / (np.max(bm25_scores) - np.min(bm25_scores) + 1e-6)
    
    # Get BM25 scores for semantic results using document content mapping
    semantic_indices = []
    filtered_semantic_results = []
    filtered_semantic_scores = []
    
    for doc, score in zip(semantic_results, semantic_scores):
        if doc.page_content in doc_map:
            idx, original_doc = doc_map[doc.page_content]
            semantic_indices.append(idx)
            filtered_semantic_results.append(original_doc)
            filtered_semantic_scores.append(score)
    
    if not semantic_indices:  # Fallback if no matches found
        return [(doc, 0.0) for doc in semantic_results[:5]]
    
    bm25_scores_filtered = bm25_scores[semantic_indices]
    
    # Combine scores
    combined_scores = alpha * np.array(filtered_semantic_scores) + (1 - alpha) * bm25_scores_filtered
    
    # Create document-score pairs and sort
    doc_score_pairs = list(zip(filtered_semantic_results, combined_scores))
    return sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)

def rerank_with_cross_encoder(query: str, documents: List[Document], top_k: int = 5):
    """Rerank documents using cross-encoder"""
    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    pairs = [[query, doc.page_content] for doc in documents]
    scores = cross_encoder.predict(pairs)
    doc_score_pairs = list(zip(documents, scores))
    return sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)[:top_k]

def query_expansion(query: str) -> List[str]:
    """Expand query using LLM"""
    prompt = f"""Generate 3 alternative versions of this query that capture the same meaning but using different words. Format as a python list.
    Query: {query}
    Alternative queries:"""
    
    response = model.invoke(prompt)
    try:
        expanded_queries = eval(response)
        return [query] + expanded_queries
    except:
        return [query]

def sliding_window_reranker(documents: List[Document], query: str, window_size: int = 5):  # Increased from 3
    """Rerank using sliding window approach with larger windows"""
    if len(documents) < window_size:
        return documents
    
    # Create windows with more context
    windows = []
    for i in range(len(documents) - window_size + 1):
        window_docs = documents[i:i + window_size]
        # Get previous and next documents for additional context
        prev_doc = documents[i-1] if i > 0 else None
        next_doc = documents[i+window_size] if i+window_size < len(documents) else None
        
        # Combine text with additional context
        texts = []
        if prev_doc:
            texts.append(prev_doc.page_content)
        texts.extend([doc.page_content for doc in window_docs])
        if next_doc:
            texts.append(next_doc.page_content)
            
        combined_text = " ".join(texts)
        
        windows.append({
            'text': combined_text,
            'docs': window_docs,
            'center_doc': window_docs[window_size // 2]
        })
    
    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    pairs = [[query, window['text']] for window in windows]
    scores = cross_encoder.predict(pairs)
    
    seen_contents = set()
    ranked_docs = []
    for score, window in sorted(zip(scores, windows), reverse=True):
        center_doc = window['center_doc']
        if center_doc.page_content not in seen_contents:
            seen_contents.add(center_doc.page_content)
            ranked_docs.append(center_doc)
    
    return ranked_docs