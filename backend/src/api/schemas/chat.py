from typing import List, Literal, Optional

from pydantic import BaseModel


class QueryClassification(BaseModel):
    query_type: Literal["conversational", "rag_question"]
    conversational_response: Optional[str] = None
    hyde_answer: Optional[str] = None
    rewritten_queries: Optional[List[str]] = None
