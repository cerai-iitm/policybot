# services/suggested_queries.py
from typing import List, Optional

from pydantic import BaseModel, Field

from app.logger import get_logger
from providers.llm.factory import get_llm

logger = get_logger(__name__)


class SuggestedQueriesOutput(BaseModel):
    """Structured output for LLM - generates JSON schema automatically."""

    queries: List[str] = Field(
        description="List of 5 suggested questions for RAG based on the document summary",
        min_items=5,
        max_items=5,
    )


async def generate_suggested_queries(summary: str) -> Optional[List[str]]:
    """
    Generate 5 suggested RAG queries based on PDF summary using structured output.

    Args:
        summary: The PDF summary generated during processing

    Returns:
        List of 5 query strings or None on failure
    """
    llm = get_llm()

    system_prompt = f"""Based on the following document summary, generate 5 diverse suggested queries that a user might ask to retrieve information from this document.

The queries should:
- Be specific questions that would require RAG retrieval to answer
- Cover different aspects: overview, details, relationships, implications
- Be natural questions someone would type
- Require the actual document content to answer (not general knowledge)

Document Summary:
{summary}

Return exactly 5 queries in the JSON format specified."""

    try:
        # Use structured output - passes JSON schema to model, gets validated response
        structured_llm = llm.with_structured_output(SuggestedQueriesOutput)
        result = await structured_llm.ainvoke(system_prompt)

        # Ensure exactly 5 queries
        queries = result.queries[:5]

        # Pad with generic queries if needed
        fallback_queries = [
            "What are the main points discussed in this document?",
            "What are the key findings or conclusions?",
            "What specific data or evidence is presented?",
            "What are the implications of this document?",
            "What questions does this document answer?",
        ]
        while len(queries) < 5:
            queries.append(fallback_queries[len(queries)])

        return queries
    except Exception as e:
        logger.exception(f"Failed to generate suggested queries: {e}")
        return None
