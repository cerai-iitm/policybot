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
    session_id: str
    model_name: Optional[str] = None


@router.post("/query")
async def query_endpoint(request: QueryRequest, db: AsyncSession = Depends(get_db)):
    """
    Query endpoint with per-request model selection.

    - request.model_name omitted/None: Uses backend default cfg.MODEL_NAME (regular users)
    - request.model_name provided: Uses specified model (admin users)
    """
    # Resolve model: use provided model_name or default
    resolved_model = request.model_name or cfg.MODEL_NAME
    logger.info(
        f"Query endpoint - session: {request.session_id[:8]}..., "
        f"model: {resolved_model}, "
        f"pdfs: {len(request.pdfs or [])}"
    )

    chat_manager = ChatManager()
    # Pass resolved model to LLM_Interface (per-request model selection)
    llm_interface = LLM_Interface(model_name=resolved_model)
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
    context_chunks, chunk_metadata = await retriever.retrieve(
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

        # Merge chunks with their metadata for the response
        chunks_with_metadata = [
            {
                "text": context_chunks[i],
                "source": chunk_metadata[i]["source"],
                "page_number": chunk_metadata[i]["page_number"],
            }
            for i in range(len(context_chunks))
        ]

        return {"response": response, "context_chunks": chunks_with_metadata}
    except Exception as e:
        logger.error(f"Error generating response: {e}")

        # Merge chunks with their metadata for error response too
        chunks_with_metadata = [
            {
                "text": context_chunks[i],
                "source": chunk_metadata[i]["source"],
                "page_number": chunk_metadata[i]["page_number"],
            }
            for i in range(len(context_chunks))
        ]

        return {
            "error": "Failed to generate response.",
            "context_chunks": chunks_with_metadata,
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
    # llm_interface = LLM_Interface()
    # # 1. Get all source summaries and filenames
    # all_sources = await get_all_source_summaries(db)
    # if not all_sources:
    #     raise HTTPException(status_code=404, detail="No sources found.")
    # filenames = [str(s.source_name) for s in all_sources]
    #
    # overall = await get_overall_summary(db, filenames)
    # summary = overall.summary if overall else None
    # if not overall:
    #     summaries = [s.summary for s in all_sources]
    #     summary_str = [str(summary) for summary in summaries]
    #
    #     docs = [Document(page_content=s, metadata={}) for s in summary_str]
    #     summary = await llm_interface.summarize_with_stuff_chain(
    #         docs, max_words=cfg.OVERALL_SUMMARY_MAX_WORDS
    #     )
    #     await add_overall_summary(db, filenames, summary)
    #
    # queries = await llm_interface.generate_suggested_queries(
    #     str(summary), session_id=request.session_id
    # )
    #
    # # 5. Return as JSON
    # return {"suggested_queries": queries}
    return {"suggested_queries": []}


@router.get("/default-model")
def get_default_model():
    """
    Returns the backend default model and list of supported models.

    Frontend uses this to:
    - Initialize ModelSelector with current default
    - Display available models for admin users

    Regular users at /policybot always use the default.
    Admin users at /config can override per-request.
    """
    logger.info(f"Default model requested: {cfg.MODEL_NAME}")
    return {
        "model_name": cfg.MODEL_NAME,
        "provider": cfg.LLM_PROVIDER,
        "supported_models": cfg.SUPPORTED_MODELS,  # Returns full list with id and name
    }
