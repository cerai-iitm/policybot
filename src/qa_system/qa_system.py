import logging
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

from ..config.settings import settings

logger = logging.getLogger(__name__)

class QASystem:   
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL_NAME,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.1, 
            top_p=0.95,
            top_k=40,
            max_output_tokens=4096,
        )
        self.qa_prompt = PromptTemplate(
            input_variables=["system_prompt", "context", "question"],
            template=settings.QA_PROMPT_TEMPLATE,
        )
    
    def format_context(self, documents: List[Document]) -> str:
        if not documents:
            return "No relevant information found."
        
        # Sort documents by source, page, hierarchy level, and chunk index for better context flow
        sorted_docs = sorted(documents, key=lambda x: (
            x.metadata.get("source", ""), 
            x.metadata.get("page", 0),
            x.metadata.get("hierarchy_level", 999),  # Sort by hierarchy level if available
            x.metadata.get("chunk_index", 0)
        ))

        context_parts = []
        for doc in sorted_docs:
            source = doc.metadata.get("source", "Unknown Source")
            page = doc.metadata.get("page", "Unknown Page")
            section_title = doc.metadata.get("section_title", "")
            
            # Include section title in the context
            header_parts = [f"Document: {source}", f"Page: {page}"]
            if section_title:
                header_parts.append(f"Section: {section_title}")
                
            context_part = f"[{', '.join(header_parts)}]\n{doc.page_content}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def answer_question(self, question: str, documents: List[Document]) -> Dict[str, Any]:
        if not question or not documents:
            return {
                "answer": "I don't have enough information to answer this question.",
                "sources": []
            }
        
        try:
            context = self.format_context(documents)
            
            prompt_value = self.qa_prompt.format(
                system_prompt=settings.SYSTEM_PROMPT,
                context=context,
                question=question
            )
            
            response = self.llm.invoke(prompt_value)
            answer = response.content
            
            sources = []
            for doc in documents:
                source = {
                    "title": doc.metadata.get("source", "Unknown"),
                    "page": doc.metadata.get("page", "Unknown")
                }
                if source not in sources:
                    sources.append(source)
            
            logger.info(f"Generated answer with {len(sources)} sources\n{'#'*100}\n")
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                "answer": "I encountered an error while trying to answer your question.",
                "sources": []
            }