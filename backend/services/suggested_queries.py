# services/suggested_queries.py
from typing import List, Optional

from pydantic import BaseModel, Field

from app.logger import get_logger
from app.prompts import (
    FALLBACK_SUGGESTED_QUERIES,
    suggested_queries_system_prompt,
)
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
    system_prompt = suggested_queries_system_prompt(summary)

    try:
        # Use structured output - passes JSON schema to model, gets validated response
        structured_llm = llm.with_structured_output(SuggestedQueriesOutput)
        result = await structured_llm.ainvoke(system_prompt)

        # Ensure exactly 5 queries
        queries = result.queries[:5]

        # Pad with generic queries if needed
        while len(queries) < 5:
            queries.append(FALLBACK_SUGGESTED_QUERIES[len(queries)])

        return queries
    except Exception as e:
        logger.exception(f"Failed to generate suggested queries: {e}")
        return None
