# api/routes/chat.py
import json
import secrets
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import trim_messages
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_strict_user
from api.schemas.chat import ChatHistoryResponse, ChatQueryRequest
from app.config import get_config
from app.prompts import (
    RAG_CHAT_SYSTEM_MESSAGE,
    RAG_CHAT_PROMPT,
)
from db.models.chat_message import ChatMessage
from db.models.chat_session import ChatSession
from db.models.notebook import Notebook
from db.models.pdf import PDF
from db.models.user import User
from db.session import AsyncSessionLocal, get_db
from providers.llm.factory import get_llm
from services.rag import (
    classify_query,
    generate_hyde_and_queries,
    get_chat_history,
    get_pdf_summaries,
    retrieve_chunks,
)

router = APIRouter(prefix="/chat", tags=["Chat"])

config = get_config()
logger = logging.getLogger(__name__)


async def get_or_create_active_session(
    notebook_id: str, user_id: int, db: AsyncSession, session_id: str | None = None
) -> tuple[ChatSession, str]:
    result = await db.execute(
        select(Notebook).where(
            and_(Notebook.notebook_id == notebook_id, Notebook.user_id == user_id)
        )
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")

    if session_id:
        result = await db.execute(
            select(ChatSession).where(
                and_(
                    ChatSession.session_id == session_id,
                    ChatSession.user_id == user_id,
                    ChatSession.notebook_id == notebook.id,
                )
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session, notebook.notebook_id

    result = await db.execute(
        select(ChatSession).where(
            and_(
                ChatSession.notebook_id == notebook.id,
                ChatSession.is_active == True,
            )
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        session = ChatSession(
            session_id=f"session_{secrets.token_hex(8)}",
            notebook_id=notebook.id,
            user_id=user_id,
            is_active=True,
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    return session, notebook.notebook_id


async def get_notebook_pdfs(
    notebook_id: str, user_id: int, stored_filenames: list[str] | None, db: AsyncSession
) -> tuple[list[str], Notebook]:
    """Resolve notebook by external notebook_id (string) and return stored_filenames and Notebook.
    Returns (stored_filenames, notebook).
    """
    result = await db.execute(
        select(Notebook).where(
            and_(Notebook.notebook_id == notebook_id, Notebook.user_id == user_id)
        )
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")

    # Query PDFs using numeric notebook.id FK
    query = select(PDF).where(
        and_(PDF.notebook_id == notebook.id, PDF.processing_status == "complete")
    )

    if stored_filenames:
        query = query.where(PDF.stored_filename.in_(stored_filenames))

    result = await db.execute(query)
    pdfs = result.scalars().all()

    if stored_filenames and len(pdfs) != len(stored_filenames):
        raise HTTPException(
            status_code=400, detail="One or more PDFs not found or not complete"
        )

    return [pdf.stored_filename for pdf in pdfs], notebook


@router.post("/query")
async def chat_query(
    request: ChatQueryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    is_demo = getattr(user, "is_demo_user", False)

    if is_demo:
        result = await db.execute(
            select(Notebook).where(
                and_(
                    Notebook.notebook_id == request.notebook_id,
                    Notebook.user_id == user.id,
                )
            )
        )
        notebook = result.scalar_one_or_none()
        if not notebook:
            raise HTTPException(status_code=404, detail="Notebook not found")

        session_id = request.session_id or f"session_{secrets.token_hex(8)}"
        notebook_id = notebook.notebook_id
    else:
        session, notebook_id = await get_or_create_active_session(
            request.notebook_id, user.id, db, request.session_id
        )
        session_id = session.session_id

        result = await db.execute(
            select(Notebook).where(
                and_(
                    Notebook.notebook_id == request.notebook_id,
                    Notebook.user_id == user.id,
                )
            )
        )
        notebook = result.scalar_one_or_none()

    pdf_ids, notebook = await get_notebook_pdfs(
        request.notebook_id, user.id, request.pdf_ids, db
    )

    if not pdf_ids:
        raise HTTPException(
            status_code=400,
            detail="No completed PDFs found in the specified notebook",
        )

    # 2. Get PDF summaries for classification
    pdf_summaries = await get_pdf_summaries(pdf_ids, db)

    # 3. Get chat history for better classification
    previous_conversation = ""
    if not is_demo:
        history_msgs = await get_chat_history(session.id, db, max_turns=3)
        # convert LangChain message objects to a formatted string for the classifier
        if history_msgs:
            formatted_parts = []
            for msg in history_msgs:
                cls_name = msg.__class__.__name__
                if cls_name == "HumanMessage":
                    formatted_parts.append(f"Q: {msg.content}")
                else:
                    formatted_parts.append(f"A: {msg.content}")

            history_text = "\n".join(formatted_parts)
            previous_conversation = f"Previous conversation:\n{history_text}"

    # 4. Classify query (conversational vs RAG)
    classification = await classify_query(
        request.query, pdf_summaries, previous_conversation
    )

    # 4. If conversational, stream response via SSE
    if (
        classification.query_type == "conversational"
        and classification.conversational_response
    ):
        if not is_demo:
            user_message = ChatMessage(
                user_id=user.id,
                notebook_id=notebook.id,
                session_id=session.id,
                role="user",
                content=request.query,
            )
            db.add(user_message)
            await db.commit()

        response_text = classification.conversational_response

        async def generate():
            # Stream conversational response defensively (preserve spacing between chunks)
            full = ""
            for i in range(0, len(response_text), 10):
                chunk = response_text[i : i + 10]

                # Debug log
                if getattr(config, "debug_stream_chunks", False):
                    logger.debug("CONV CHUNK: %r", chunk)

                # Prevent glue across boundaries
                if (
                    full
                    and not full.endswith((" ", "\n"))
                    and not chunk.startswith(
                        (" ", "\n", ".", ",", ":", ";", "?", "!", '"', "'")
                    )
                ):
                    full += " "

                full += chunk
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            if not is_demo:
                async with AsyncSessionLocal() as db_session:
                    assistant_message = ChatMessage(
                        user_id=user.id,
                        notebook_id=notebook.id,
                        session_id=session.id,
                        role="assistant",
                        content=full,
                    )
                    db_session.add(assistant_message)
                    await db_session.commit()

            yield 'data: {"context_chunks": []}\n\n'
            yield 'data: {"done": true}\n\n'

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    # 5. If RAG, generate HYDE + rewritten queries
    hyde_result = await generate_hyde_and_queries(request.query, pdf_summaries)

    # 6. Retrieve chunks using RRF
    context_chunks = await retrieve_chunks(
        query=request.query,
        stored_filenames=pdf_ids,
        hyde_answer=hyde_result.hyde_answer,
        rewritten_queries=hyde_result.rewritten_queries,
        top_k=5,
    )

    if not context_chunks:
        raise HTTPException(status_code=400, detail="No relevant context found")

    # Build context text
    context_text = "\n\n".join(
        [
            f"[Source PDF: {chunk.get('stored_filename', 'unknown')} (page {chunk['page_number']})]\n{chunk['text']}"
            for chunk in context_chunks
        ]
    )

    # Get chat history
    if is_demo:
        history = []
    else:
        history = await get_chat_history(session.id, db, config.max_history_messages)

    # Persist user message using numeric notebook FK
    if not is_demo:
        user_message = ChatMessage(
            user_id=user.id,
            notebook_id=notebook.id,
            session_id=session.id,
            role="user",
            content=request.query,
        )
        db.add(user_message)
        await db.commit()

    # Use the structured RAG prompt
    prompt = RAG_CHAT_PROMPT

    async def generate():
        llm = get_llm()

        # Trim history to a token budget to avoid pushing the model into truncation.
        # Reserve ~40% for system + context + answer; use actual model context.
        MODEL_TOKEN_WINDOW = config.num_ctx
        RESERVED_FOR_CONTEXT_AND_ANSWER = int(config.num_ctx * 0.4)
        token_budget_for_history = MODEL_TOKEN_WINDOW - RESERVED_FOR_CONTEXT_AND_ANSWER

        try:
            trimmed_history = trim_messages(
                history,
                max_tokens=token_budget_for_history,
                strategy="last",
                token_counter=llm,
                include_system=True,
            )
        except Exception:
            # Fallback: keep recent turns (each turn is one user+assistant pair)
            trimmed_history = history[-(config.max_history_messages * 2) :]

        chain = prompt | llm
        full_response = ""

        try:
            async for chunk in chain.astream(
                {
                    "history": trimmed_history,
                    "context": context_text,
                    "question": request.query,
                }
            ):
                content = chunk.content or ""

                # Debug-log raw chunk content if enabled
                if getattr(config, "debug_stream_chunks", False):
                    logger.debug("STREAM CHUNK: %r", content)

                # Defensive spacing to avoid accidental glue like "scores.The..."
                if (
                    full_response
                    and not full_response.endswith((" ", "\n"))
                    and not content.startswith(
                        (" ", "\n", ".", ",", ":", ";", "?", "!", '"', "'")
                    )
                ):
                    full_response += " "

                if content:
                    full_response += content
                    yield f"data: {json.dumps({'content': content})}\n\n"

            stored_filenames_list = list(
                set(c["stored_filename"] for c in context_chunks)
            )
            filename_map = {}

            if is_demo:
                for c in context_chunks:
                    filename_map[c["stored_filename"]] = c["stored_filename"]
            else:
                async with AsyncSessionLocal() as db_session:
                    if stored_filenames_list:
                        pdf_result = await db_session.execute(
                            select(PDF.stored_filename, PDF.original_filename).where(
                                PDF.stored_filename.in_(stored_filenames_list)
                            )
                        )
                        filename_map = dict(pdf_result.all())

                    source_chunks_for_db = [
                        {
                            "stored_filename": c["stored_filename"],
                            "original_filename": filename_map.get(
                                c["stored_filename"], c["stored_filename"]
                            ),
                            "page_number": c["page_number"],
                            "text": c["text"],
                        }
                        for c in context_chunks
                    ]

                    assistant_message = ChatMessage(
                        user_id=user.id,
                        notebook_id=notebook.id,
                        session_id=session.id,
                        role="assistant",
                        content=full_response,
                        source_chunks=source_chunks_for_db,
                    )
                    db_session.add(assistant_message)
                    await db_session.commit()

            context_for_client = [
                {
                    "original_filename": filename_map.get(
                        c["stored_filename"], c["stored_filename"]
                    ),
                    "page_number": c["page_number"],
                    "text": c["text"],
                }
                for c in context_chunks
            ]
            yield f"data: {json.dumps({'context_chunks': context_for_client})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        yield 'data: {"done": true}\n\n'

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history_endpoint(
    session_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session_result = await db.execute(
        select(ChatSession).where(
            and_(ChatSession.session_id == session_id, ChatSession.user_id == user.id)
        )
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(
        select(ChatMessage)
        .where(
            and_(ChatMessage.session_id == session.id, ChatMessage.user_id == user.id)
        )
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()

    return ChatHistoryResponse(
        session_id=session_id,
        messages=[
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "source_chunks": m.source_chunks,
                "created_at": m.created_at,
            }
            for m in messages
        ],
    )


@router.delete("/history")
async def clear_chat_history(
    session_id: str = Query(...),
    user: User = Depends(get_strict_user),
    db: AsyncSession = Depends(get_db),
):
    session_result = await db.execute(
        select(ChatSession).where(
            and_(ChatSession.session_id == session_id, ChatSession.user_id == user.id)
        )
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(
        select(ChatMessage).where(
            and_(ChatMessage.session_id == session.id, ChatMessage.user_id == user.id)
        )
    )
    messages = result.scalars().all()

    for message in messages:
        await db.delete(message)

    await db.commit()

    return {"message": f"Cleared {len(messages)} messages"}
