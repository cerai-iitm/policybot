import os
import logging
from typing import List
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from ..config.settings import settings

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self, collection_name: str = "single_pdf"):
        genai.configure(api_key=settings.GEMINI_API_KEY)

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
            self.vector_store.persist()
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
            for doc, score in results:
                # Note: Chroma returns distance metrics where lower is better
                # Converting to similarity score where higher is better (1 - distance)
                similarity = 1 - score
                if similarity >= settings.SIMILARITY_THRESHOLD:
                    filtered_results.append(doc)
            
            logger.info(f"Found {len(filtered_results)} relevant documents for query")
            return filtered_results
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def clear(self) -> bool:
        """Clear all documents from the vector store"""
        try:
            self.vector_store.delete_collection()
            self.vector_store = self._create_or_load_vector_store()
            logger.info("Vector store cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            return False