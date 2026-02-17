from typing import List, Optional
from difflib import SequenceMatcher
from sqlalchemy import text

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.documents import Document
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import cfg, logger
from src.db import get_db
from src.db.crud import (
    add_overall_summary,
    get_all_source_summaries,
    get_notebook_by_notebook_id,
    get_overall_summary,
    get_pdf_by_filename_and_notebook,
    get_random_suggested_questions,
    insert_suggested_question,
)
from src.services import ChatManager, LLM_Interface, Retriever

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    pdfs: Optional[List[str]] = None
    session_id: str
    model_name: Optional[str] = None
    notebook_id: str


@router.post("/query")
async def query_endpoint(request: QueryRequest, db: AsyncSession = Depends(get_db)):
    """
    Query endpoint with per-request model selection and notebook scoping.

    - request.model_name omitted/None: Uses backend default cfg.MODEL_NAME (regular users)
    - request.model_name provided: Uses specified model (admin users)
    """
    # Validate notebook exists
    notebook = await get_notebook_by_notebook_id(db, request.notebook_id.strip())
    if not notebook:
        raise HTTPException(
            status_code=404, detail=f"Notebook '{request.notebook_id}' not found."
        )

    # Resolve model: use provided model_name or default
    resolved_model = request.model_name or cfg.MODEL_NAME
    logger.info(
        f"Query endpoint - notebook: {request.notebook_id}, session: {request.session_id[:8]}..., "
        f"model: {resolved_model}, "
        f"pdfs: {len(request.pdfs or [])}"
    )

    chat_manager = ChatManager()
    # Pass resolved model to LLM_Interface (per-request model selection)
    llm_interface = LLM_Interface(model_name=resolved_model)
    retriever = Retriever(interface=llm_interface)
    session_id = request.session_id

    valid_pdfs = []
    logger.info(
        f"Validating PDFs for notebook {request.notebook_id} (DB id={notebook.id})"
    )
    for fname in request.pdfs or []:
        if not fname.lower().endswith(".pdf"):
            fname = f"{fname}.pdf"
        # Check existence in database and verify processing status
        logger.info(f"Looking for PDF: '{fname}' in notebook_id={notebook.id}")
        pdf_record = await get_pdf_by_filename_and_notebook(db, fname, notebook.id)
        if pdf_record:
            logger.info(
                f"Found PDF '{fname}': id={pdf_record.id}, status='{pdf_record.processing_status}'"
            )
        else:
            logger.warning(
                f"PDF '{fname}' NOT FOUND in database for notebook {notebook.id}"
            )
        if pdf_record and pdf_record.processing_status == "complete":
            valid_pdfs.append(fname)
            logger.info(f"PDF '{fname}' added to valid_pdfs")
        else:
            status = pdf_record.processing_status if pdf_record else "not found"
            logger.warning(
                f"PDF '{fname}' skipped in notebook {request.notebook_id}: status='{status}'"
            )
    logger.info(
        f"Valid PDFs for the query in notebook {request.notebook_id}: {len(valid_pdfs)}"
    )

    if not valid_pdfs:
        raise HTTPException(
            status_code=400,
            detail="No valid PDFs found in the specified notebook.",
        )

    # Pass DB session into retriever so it can load source summaries when available.
    context_chunks, chunk_metadata = await retriever.retrieve(
        query=request.query, pdfs=valid_pdfs, db=db
    )
    logger.info(f"Retrieved {len(context_chunks)} chunks for the query in chat.py")
    logger.info(f"Returning {len(context_chunks)} context chunks in response.")

    async def _get_suggested_example(
        db_session: AsyncSession,
        notebook_identifier: str,
        query_text: str,
        filename: Optional[str] = None,
        min_ratio: float = 0.90,
    ) -> Optional[dict]:
        """Return best example_answer for `query_text` within a notebook.

        Returns dict {"example_answer","matched_question","score"} or None.
        """
        q = (query_text or "").strip().lower()

        # Prefer filename-specific matches when a filename is provided.
        if filename:
            # 1a) exact match among questions for that filename
            exact_sql_fn = text(
                "SELECT sq.question AS suggested_text, sqe.example_answer AS example_answer "
                "FROM suggested_questions sq "
                "JOIN suggested_question_examples sqe ON sq.id = sqe.suggested_question_id "
                "WHERE lower(sq.question)=:q AND sq.notebook_id = :nb AND sq.filename = :fn LIMIT 1"
            )
            res = await db_session.execute(
                exact_sql_fn, {"q": q, "nb": notebook_identifier, "fn": filename}
            )
            row = res.first()
            if row:
                return {"example_answer": row[1], "matched_question": row[0], "score": 1.0}

            # 1b) fuzzy match among questions for that filename
            sql_fn = text(
                "SELECT sq.question AS suggested_text, sqe.example_answer AS example_answer "
                "FROM suggested_questions sq "
                "JOIN suggested_question_examples sqe ON sq.id = sqe.suggested_question_id "
                "WHERE sq.notebook_id = :nb AND sq.filename = :fn"
            )
            res = await db_session.execute(sql_fn, {"nb": notebook_identifier, "fn": filename})
            rows = res.mappings().all()
            best = None
            best_score = 0.0
            matched = None
            if rows:
                for r in rows:
                    s_text = (r["suggested_text"] or "").lower()
                    if not s_text:
                        continue
                    score = SequenceMatcher(None, q, s_text).ratio()
                    if score > best_score:
                        best_score = score
                        best = r["example_answer"]
                        matched = r["suggested_text"]
                if best_score >= min_ratio:
                    return {"example_answer": best, "matched_question": matched, "score": best_score}

        # 2) exact match shortcut (case-insensitive) across notebook (general)
        exact_sql = text(
            "SELECT sq.question AS suggested_text, sqe.example_answer AS example_answer "
            "FROM suggested_questions sq "
            "JOIN suggested_question_examples sqe ON sq.id = sqe.suggested_question_id "
            "WHERE lower(sq.question)=:q AND sq.notebook_id = :nb LIMIT 1"
        )
        res = await db_session.execute(exact_sql, {"q": q, "nb": notebook_identifier})
        row = res.first()
        if row:
            return {"example_answer": row[1], "matched_question": row[0], "score": 1.0}

        # 3) fuzzy match across all suggested questions for the notebook
        sql = text(
            "SELECT sq.question AS suggested_text, sqe.example_answer AS example_answer "
            "FROM suggested_questions sq "
            "JOIN suggested_question_examples sqe ON sq.id = sqe.suggested_question_id "
            "WHERE sq.notebook_id = :nb"
        )
        res = await db_session.execute(sql, {"nb": notebook_identifier})
        rows = res.mappings().all()
        if not rows:
            return None

        if not rows:
            return None

        best = None
        best_score = 0.0
        matched = None
        for r in rows:
            s_text = (r["suggested_text"] or "").lower()
            if not s_text:
                continue
            score = SequenceMatcher(None, q, s_text).ratio()
            if score > best_score:
                best_score = score
                best = r["example_answer"]
                matched = r["suggested_text"]

        if best_score >= min_ratio:
            return {"example_answer": best, "matched_question": matched, "score": best_score}
        return None

    try:
        # Use the async LLM API to avoid blocking the event loop.
        response = await llm_interface.agenerate_response(
            session_id, chat_manager, context_chunks, request.query
        )
        logger.info("Generated full response for query.")

        # If LLM returned an error marker or empty response, try fallback
        if not response or (isinstance(response, str) and "[LLM Error" in response):
            logger.warning("LLM returned no usable content; attempting suggested-example fallback")
            fallback = await _get_suggested_example(
                db, notebook.notebook_id, request.query, filename=valid_pdfs[0] if valid_pdfs else None
            )
            if fallback:
                chunks_with_metadata = [
                    {
                        "text": context_chunks[i],
                        "source": chunk_metadata[i]["source"],
                        "page_number": chunk_metadata[i]["page_number"],
                    }
                    for i in range(len(context_chunks))
                ]
                return {
                    "response": fallback["example_answer"],
                    "source": "suggested_example_fallback",
                    "matched_question": fallback["matched_question"],
                    "score": fallback["score"],
                    "context_chunks": chunks_with_metadata,
                }

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

        # Try fallback when an exception occurs
        fallback = await _get_suggested_example(
            db, notebook.notebook_id, request.query, filename=valid_pdfs[0] if valid_pdfs else None
        )
        chunks_with_metadata = [
            {
                "text": context_chunks[i],
                "source": chunk_metadata[i]["source"],
                "page_number": chunk_metadata[i]["page_number"],
            }
            for i in range(len(context_chunks))
        ]

        if fallback:
            return {
                "response": fallback["example_answer"],
                "source": "suggested_example_fallback",
                "matched_question": fallback["matched_question"],
                "score": fallback["score"],
                "context_chunks": chunks_with_metadata,
            }

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
    notebook_id: str
    selected_filenames: Optional[List[str]] = None


@router.post("/suggested-queries")
async def suggested_queries_endpoint(
    request: SuggestedQueriesRequest, db: AsyncSession = Depends(get_db)
):
    """
    Get random suggested questions for a notebook, filtered by selected filenames.

    - Validates notebook exists using notebook_id
    - Filters questions by selected_filenames (general questions + file-specific questions)
    - Returns up to 3 random questions from the DB for the notebook
    """
    notebook = await get_notebook_by_notebook_id(db, request.notebook_id.strip())
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")

    questions = await get_random_suggested_questions(
        db, notebook.notebook_id, selected_filenames=request.selected_filenames, limit=3
    )

    return {"suggested_queries": questions}


class SuggestedQueryUploadRequest(BaseModel):
    notebook_id: str
    question: str
    filename: Optional[str] = None


@router.post("/suggested-queries/upload")
async def upload_suggested_query(
    req: SuggestedQueryUploadRequest, db: AsyncSession = Depends(get_db)
):
    """
    Upload a new suggested question for a notebook.

    - Validates notebook exists
    - Inserts question into DB
    - Returns success response
    """
    notebook = await get_notebook_by_notebook_id(db, req.notebook_id.strip())
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")

    await insert_suggested_question(
        db,
        notebook.notebook_id,
        req.question,
        filename=req.filename,
    )

    return {"ok": True}


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
