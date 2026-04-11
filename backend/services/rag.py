# services/rag.py
from collections import defaultdict
from typing import List

import numpy as np
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel
from qdrant_client.http.models import (
    FieldCondition,
    Filter,
    Fusion,
    MatchAny,
    Prefetch,
    FusionQuery,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_config
from db.models.chat_message import ChatMessage
from db.models.pdf import PDF
from providers.embedding.factory import get_embedding
from providers.llm.factory import get_llm
from providers.reranker.factory import get_reranker
from services.qdrant_client import get_qdrant_client


class QueryClassification(BaseModel):
    query_type: str
    conversational_response: str | None = None


class HYDEQueries(BaseModel):
    hyde_answer: str
    rewritten_queries: List[str]


async def get_pdf_summaries(pdf_ids: List[int], db: AsyncSession) -> str:
    """Get combined summaries from PDF table using pdf_ids."""
    if not pdf_ids:
        return ""

    result = await db.execute(
        select(PDF.original_filename, PDF.summary).where(
            PDF.id.in_(pdf_ids), PDF.summary.isnot(None)
        )
    )
    rows = result.all()

    summaries = []
    for filename, summary in rows:
        if summary:
            summaries.append(f"[{filename}]\n{summary}")

    return "\n\n".join(summaries)


async def classify_query(query: str, pdf_summaries: str) -> QueryClassification:
    """Classify query as conversational or rag_question using LLM with structured output."""
    config = get_config()
    llm = get_llm()

    system_prompt = f"""You are a query classifier. Given the user query and document summaries, determine if the query needs RAG retrieval or is a general conversational query.

Document Summaries:
{pdf_summaries if pdf_summaries else "No documents available."}

User Query: {query}

Classification rules:
- If the query asks about specific information, explanations, or details from the documents → RAG question
- If it's a greeting, general chat, or doesn't require document context → Conversational
- If uncertain, classify as RAG question

Return a JSON object with:
- query_type: "conversational" or "rag_question"
- conversational_response: If conversational, provide a direct response (string)
"""

    try:
        structured_llm = llm.with_structured_output(QueryClassification)
        result = await structured_llm.ainvoke(system_prompt)
        return result
    except Exception as e:
        # Default to RAG on error
        return QueryClassification(
            query_type="rag_question", conversational_response=None
        )


async def generate_hyde_and_queries(query: str, num_queries: int = 5) -> HYDEQueries:
    """Generate HYDE answer + rewritten queries using LLM with structured output."""
    config = get_config()
    llm = get_llm()

    system_prompt = f"""Given the user query, generate:
1. A hypothetical document/answer that would answer this query
2. {num_queries} different phrasings of this query for better semantic search

Original Query: {query}

Return a JSON object with:
- hyde_answer: The hypothetical answer (2-3 sentences)
- rewritten_queries: List of {num_queries} query variations attacking the question from different angles
"""

    try:
        structured_llm = llm.with_structured_output(HYDEQueries)
        result = await structured_llm.ainvoke(system_prompt)

        # Ensure we have exactly num_queries
        if len(result.rewritten_queries) < num_queries:
            # Pad with original query
            result.rewritten_queries = (
                result.rewritten_queries + [query] * num_queries
            )[:num_queries]

        return result
    except Exception as e:
        # Fallback: just use original query
        return HYDEQueries(hyde_answer=query, rewritten_queries=[query])


def _softmax_top_p_filter(scores, items, top_p=0.9, temperature=1.0):
    """Apply softmax and filter by cumulative probability threshold."""
    if not items:
        return []

    scores = np.array(scores)
    exp_scores = np.exp((scores - np.max(scores)) / temperature)
    softmax_scores = exp_scores / exp_scores.sum()

    sorted_indices = np.argsort(-softmax_scores)
    sorted_items = [items[i] for i in sorted_indices]
    sorted_probs = softmax_scores[sorted_indices]

    cumsum = np.cumsum(sorted_probs)
    cutoff = np.searchsorted(cumsum, top_p) + 1

    return sorted_items[:cutoff]


async def retrieve_chunks(
    query: str,
    pdf_ids: List[int],
    hyde_answer: str | None = None,
    rewritten_queries: List[str] | None = None,
    top_k: int = 5,
) -> List[dict]:
    """Retrieve relevant chunks using RRF + reranking + top_p filtering."""
    if not pdf_ids:
        return []

    config = get_config()
    embedder = get_embedding()

    # Build query list: original query + HYDE + rewritten queries
    all_queries = [query]

    if hyde_answer and hyde_answer.strip():
        all_queries.append(hyde_answer.strip())

    if rewritten_queries:
        for q in rewritten_queries:
            if q and q.strip() and q.strip() != query:
                all_queries.append(q.strip())

    # Deduplicate while preserving order
    seen = set()
    unique_queries = []
    for q in all_queries:
        if q not in seen:
            seen.add(q)
            unique_queries.append(q)

    # Embed all queries
    query_embeddings = []
    for q in unique_queries:
        emb = await embedder.aembed_query(q)
        query_embeddings.append(emb)

    # Qdrant RRF with prefetch
    client = get_qdrant_client()
    try:
        filter_ = Filter(
            must=[
                FieldCondition(
                    key="pdf_id",
                    match=MatchAny(values=pdf_ids),
                )
            ]
        )

        # Build prefetch list
        prefetches = [
            Prefetch(
                query=emb,
                filter=filter_,
                limit=config.top_k,
            )
            for emb in query_embeddings
        ]

        # Single query with RRF fusion
        results = await client.query_points(
            collection_name=config.q_collection_name,
            prefetch=prefetches,
            query=FusionQuery(fusion=Fusion.RRF),
            limit=config.top_k,
            with_payload=True,
        )

        if not results.points:
            return []

        # Extract chunks from results
        chunks_with_metadata = []
        for point in results.points:
            chunks_with_metadata.append(
                {
                    "text": point.payload.get("text", ""),
                    "pdf_id": point.payload.get("pdf_id", 0),
                    "page_number": point.payload.get("page_number", 0),
                    "score": point.score,
                    "point_id": point.id,
                }
            )

        if not chunks_with_metadata:
            return []

        # Rerank chunks
        reranker = get_reranker()
        chunk_texts = [c["text"] for c in chunks_with_metadata]

        try:
            reranked_texts, rerank_scores = reranker.rerank(query, chunk_texts)
        except Exception:
            # If reranking fails, keep original order
            reranked_texts = chunk_texts
            rerank_scores = [c["score"] for c in chunks_with_metadata]

        # Apply softmax top_p filter on reranked results
        filtered_texts = _softmax_top_p_filter(
            rerank_scores,
            reranked_texts,
            top_p=config.top_p,
            temperature=config.reranker_temp,
        )

        # Build final response with metadata for filtered chunks
        text_to_metadata = {
            c["text"]: {"pdf_id": c["pdf_id"], "page_number": c["page_number"]}
            for c in chunks_with_metadata
        }

        final_chunks = []
        for text in filtered_texts:
            if text in text_to_metadata:
                final_chunks.append(
                    {
                        "text": text,
                        "pdf_id": text_to_metadata[text]["pdf_id"],
                        "page_number": text_to_metadata[text]["page_number"],
                    }
                )

        return final_chunks[:top_k] if top_k else final_chunks

    finally:
        await client.close()


async def get_chat_history(
    session_id: str, db: AsyncSession, max_turns: int = 3
) -> List:
    """Get chat history and format as LangChain messages."""
    config = get_config()

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .limit(max_turns * 2)
    )
    messages = result.scalars().all()

    langchain_messages = []
    for msg in messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        else:
            langchain_messages.append(AIMessage(content=msg.content))

    return langchain_messages
