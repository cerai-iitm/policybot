import os
import logging
import math
import re
from typing import List, Dict, Any
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from ..config.settings import settings

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self, collection_name: str = "single_pdf"):
        self.embedding_function = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL_NAME,
            google_api_key=settings.GEMINI_API_KEY
        )

        self.persist_directory = os.path.join(
            settings.VECTOR_STORE_DIR, 
            collection_name
        )

        self.vector_store = self._create_or_load_vector_store()
    
    def _create_or_load_vector_store(self) -> VectorStore:
        try:
            return Chroma(
                collection_name="documents",
                embedding_function=self.embedding_function,
                persist_directory=self.persist_directory
            )
        except Exception as e:
            logger.error(f"Error creating/loading vector store: {str(e)}")

            return Chroma(
                collection_name="documents",
                embedding_function=self.embedding_function
            )
    
    def add_documents(self, documents: List[Document]) -> bool:
        if not documents:
            logger.warning("No documents provided to add to vector store")
            return False
        
        try:
            self.vector_store.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to vector store")
            return True
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            return False
    
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        if not k:
            k = settings.TOP_K_RESULTS
            
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k
            )

            filtered_results = []
            logger.info(f"Raw results count: {len(results)}")
            
            for doc, score in results:
                # Note: Chroma returns distance metrics where lower is better
                # Converting to similarity score where higher is better (1 - distance)
                similarity = 1 - score
                logger.info(f"Document similarity score: {similarity:.4f}, threshold: {settings.SIMILARITY_THRESHOLD}")
                if similarity >= settings.SIMILARITY_THRESHOLD:
                    filtered_results.append(doc)
            
            logger.info(f"Found {len(filtered_results)} relevant documents for query")
            return filtered_results
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def clear(self) -> bool:
        try:
            self.vector_store.delete_collection()
            self.vector_store = self._create_or_load_vector_store()
            logger.info("Vector store cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            return False

    def keyword_search(self, query: str, k: int = None) -> List[Document]:
        """Enhanced keyword search with BM25-inspired scoring."""
        if not k:
            k = settings.TOP_K_RESULTS * 2
        try:
            # Get all documents from the store
            all_docs = self.vector_store.get()
            documents = all_docs["documents"]
            metadatas = all_docs["metadatas"]
            
            # Clean up and tokenize the query
            clean_query = re.sub(r'[^\w\s]', ' ', query.lower())
            query_terms = [term for term in clean_query.split() if len(term) > 2]
            
            # Calculate document frequencies for BM25-inspired weighting
            doc_count = len(documents)
            term_doc_freq = {}
            for term in query_terms:
                term_doc_freq[term] = 0
                for doc in documents:
                    if term in doc.lower():
                        term_doc_freq[term] += 1
            
            scored_docs = []
            for i, doc in enumerate(documents):
                clean_doc = re.sub(r'[^\w\s]', ' ', doc.lower())
                doc_terms = clean_doc.split()
                
                # Basic BM25-inspired scoring
                score = 0
                doc_length = len(doc_terms)
                
                for term in query_terms:
                    term_freq = doc_terms.count(term)
                    if term_freq > 0:
                        # Calculate inverse document frequency component
                        idf = math.log((doc_count - term_doc_freq[term] + 0.5) / 
                                      (term_doc_freq[term] + 0.5) + 1.0)
                        
                        # Calculate term frequency component with normalization
                        tf = (term_freq * 2.2) / (term_freq + 1.2 * (0.25 + 0.75 * (doc_length / 500)))
                        
                        # Add to score
                        score += tf * idf
                
                # Boost scores for documents with section titles matching query terms
                section_title = metadatas[i].get("section_title", "")
                if section_title:
                    clean_title = section_title.lower()
                    for term in query_terms:
                        if term in clean_title:
                            score *= 1.5  # Boost by 50% for each term in the title
                
                # Create Document object with metadata
                document = Document(
                    page_content=doc,
                    metadata=metadatas[i]
                )
                
                if score > 0:
                    scored_docs.append((document, score))
            
            # Sort by score and return top k
            scored_docs.sort(key=lambda x: -x[1])
            return [doc for doc, _ in scored_docs[:k]]
            
        except Exception as e:
            logger.error(f"Error in keyword search: {str(e)}")
            return []

    def hybrid_search(self, query: str, k: int = None) -> List[Document]:
        """Enhanced hybrid search combining vector similarity with BM25-inspired keyword matching."""
        if not k:
            k = settings.TOP_K_RESULTS * 2
            
        vector_results = self.similarity_search(query, k)
        keyword_results = self.keyword_search(query, k)
        
        # Extract query entities for contextual weighting
        entities = self._extract_entities(query)
        
        # Merge, preserving order and uniqueness
        seen = set()
        merged = []
        
        # First add vector results (semantic matching)
        for doc in vector_results:
            doc_id = (doc.metadata.get('source'), doc.metadata.get('page'), doc.metadata.get('chunk_index'))
            if doc_id not in seen:
                merged.append((doc, self._calculate_relevance_score(doc, query, entities)))
                seen.add(doc_id)
                
        # Then add keyword results 
        for doc in keyword_results:
            doc_id = (doc.metadata.get('source'), doc.metadata.get('page'), doc.metadata.get('chunk_index'))
            if doc_id not in seen:
                merged.append((doc, self._calculate_relevance_score(doc, query, entities)))
                seen.add(doc_id)
        
        # Sort by relevance score
        merged.sort(key=lambda x: -x[1])
        
        # Take top k
        return [doc for doc, _ in merged[:settings.TOP_K_RESULTS]]
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract potential entities from the query."""
        # Simple entity extraction based on capitalized words
        return [word for word in re.findall(r'\b[A-Z][a-zA-Z]+\b', query)]
    
    def _calculate_relevance_score(self, doc: Document, query: str, entities: List[str]) -> float:
        """Calculate a relevance score based on multiple factors."""
        text = doc.page_content.lower()
        query_lower = query.lower()
        
        # Basic scores
        exact_match_score = 3.0 if query_lower in text else 0.0
        
        # Token overlap score
        query_tokens = set(re.findall(r'\b\w+\b', query_lower))
        text_tokens = set(re.findall(r'\b\w+\b', text))
        token_overlap = len(query_tokens.intersection(text_tokens)) / len(query_tokens) if query_tokens else 0
        
        # Entity match score
        entity_score = 0.0
        for entity in entities:
            if entity.lower() in text:
                entity_score += 1.0
        
        # Section title relevance
        section_title = doc.metadata.get("section_title", "").lower()
        title_score = 0.0
        if section_title:
            for token in query_tokens:
                if token in section_title:
                    title_score += 0.5
        
        # Combine scores with weights
        final_score = (
            exact_match_score * 1.0 +
            token_overlap * 2.0 +
            entity_score * 1.5 +
            title_score * 2.0
        )
        
        return final_score