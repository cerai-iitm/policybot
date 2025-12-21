import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.documents import Document
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import cfg
from src.logger import logger
from src.rag import ChatManager, LLM_Interface, Retriever
from src.schema.db import get_db
from src.schema.overall_summaries_crud import add_overall_summary, get_overall_summary
from src.schema.source_summaries_crud import get_all_source_summaries

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    pdfs: Optional[List[str]] = None
    session_id: str  # <-- Add this line


@router.post("/query")
async def query_endpoint(request: QueryRequest, db: AsyncSession = Depends(get_db)):
    chat_manager = ChatManager()
    llm_interface = LLM_Interface()
    retriever = Retriever(interface=llm_interface)
    session_id = request.session_id

    valid_pdfs = []
    for fname in request.pdfs or []:
        if not fname.lower().endswith(".pdf"):
            fname = f"{fname}.pdf"
        if os.path.exists(os.path.join(cfg.DATA_DIR, fname)):
            valid_pdfs.append(fname)
    logger.info(f"Valid PDFs for the query: {len(valid_pdfs)}")

    # Pass DB session into retriever so it can load source summaries when available.
    context_chunks = await retriever.retrieve(
        query=request.query, pdfs=valid_pdfs, db=db
    )
    logger.info(f"Retrieved {len(context_chunks)} chunks for the query in chat.py")
    logger.info(f"Returning {len(context_chunks)} context chunks in response.")

    try:
        # Use the async LLM API to avoid blocking the event loop.
        response = await llm_interface.agenerate_response(
            session_id, chat_manager, context_chunks, request.query
        )
        logger.info("Generated full response for query.")
        return {"response": response, "context_chunks": context_chunks}
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return {
            "error": "Failed to generate response.",
            "context_chunks": context_chunks,
        }


class OverallSummaryRequest(BaseModel):
    pdf_files: List[str]


@router.get("/overall-summary")
async def overall_summary_endpoint(db: AsyncSession = Depends(get_db)):
    llm_interface = LLM_Interface()
    all_sources = await get_all_source_summaries(db)
    if not all_sources:
        raise HTTPException(status_code=404, detail="No sources found.")

    filenames = [str(s.source_name) for s in all_sources]
    summaries = [s.summary for s in all_sources]
    summary_str = [str(summary) for summary in summaries]

    docs = [Document(page_content=s, metadata={}) for s in summary_str]
    overall = await get_overall_summary(db, filenames)
    if overall:
        return {"summary": overall.summary, "files": sorted(filenames)}

    overall_summary = await llm_interface.summarize_with_stuff_chain(
        docs, max_words=cfg.OVERALL_SUMMARY_MAX_WORDS
    )

    await add_overall_summary(db, filenames, overall_summary)

    return {"summary": overall_summary, "files": sorted(filenames)}


class SuggestedQueriesRequest(BaseModel):
    session_id: str


@router.post("/suggested-queries")
async def suggested_queries_endpoint(
    request: SuggestedQueriesRequest, db: AsyncSession = Depends(get_db)
):
    llm_interface = LLM_Interface()
    # 1. Get all source summaries and filenames
    all_sources = await get_all_source_summaries(db)
    if not all_sources:
        raise HTTPException(status_code=404, detail="No sources found.")
    filenames = [str(s.source_name) for s in all_sources]

    overall = await get_overall_summary(db, filenames)
    summary = overall.summary if overall else None
    if not overall:
        summaries = [s.summary for s in all_sources]
        summary_str = [str(summary) for summary in summaries]

        docs = [Document(page_content=s, metadata={}) for s in summary_str]
        summary = await llm_interface.summarize_with_stuff_chain(
            docs, max_words=cfg.OVERALL_SUMMARY_MAX_WORDS
        )
        await add_overall_summary(db, filenames, summary)

    queries = await llm_interface.generate_suggested_queries(
        str(summary), session_id=request.session_id
    )

    # 5. Return as JSON
    return {"suggested_queries": queries}
