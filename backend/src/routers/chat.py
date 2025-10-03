import os
from typing import Dict, List, Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.config import cfg
from src.rag import ChatManager, LLM_Interface, Retriever

router = APIRouter()

llm_interface = LLM_Interface()
chat_manager = ChatManager()  # Initialize if needed
retriever = Retriever(interface=llm_interface)


class QueryRequest(BaseModel):
    query: str
    pdfs: Optional[List[str]] = None


@router.post("/query")
async def query_endpoint(request: QueryRequest):
    session_id = "default_session"

    valid_pdfs = []
    for fname in request.pdfs or []:
        if not fname.lower().endswith(".pdf"):
            fname = f"{fname}.pdf"
        if os.path.exists(os.path.join(cfg.DATA_DIR, fname)):
            valid_pdfs.append(fname)
    print(f"PDFs are {request.pdfs}, valid PDFs are {valid_pdfs}")
    context_chunks = await retriever.retrieve(query=request.query, pdfs=valid_pdfs)

    async def generate():
        async for chunk in llm_interface.generate_streaming_response(
            session_id, chat_manager, context_chunks, request.query
        ):
            yield f'data: {{"partial": "{chunk}", "done": false}}\n\n'
        yield 'data: {"partial": "", "done": true}\n\n'

    return StreamingResponse(generate(), media_type="text/event-stream")
