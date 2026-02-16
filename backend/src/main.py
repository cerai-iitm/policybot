from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import Path as FastApiPath
import os

from src.api.routers import chat_router, notebooks_router, pdf_router

app = FastAPI(
    title="PolicyBot API",
    version="1.0.0",
    description="AI-powered document processing and RAG (Retrieval-Augmented Generation) API. Organize PDFs into notebooks, process them through AI pipelines, and chat with your documents using natural language.",
    docs_url="/policybot/docs",
    redoc_url="/policybot/redoc",
    openapi_tags=[
        {
            "name": "PDF Processing",
            "description": "Upload, process, and manage PDF documents",
        },
        {
            "name": "Notebooks",
            "description": "Organize PDFs into collections",
        },
        {
            "name": "Chat",
            "description": "Query your documents with AI",
        },
    ],
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API routes with /policybot prefix
app.include_router(pdf_router, prefix="/policybot/api/pdf")
app.include_router(notebooks_router, prefix="/policybot/api")
app.include_router(chat_router, prefix="/policybot/api")


# Mount static files for assets (without html=True to avoid catching API routes)
app.mount(
    "/policybot/assets",
    StaticFiles(directory="/app/static/homepage/assets"),
    name="homepage-assets",
)

# Mount images
app.mount(
    "/policybot/images",
    StaticFiles(directory="/app/static/homepage/images"),
    name="homepage-images",
)

# Mount chat static files - MUST be before the catch-all
app.mount(
    "/policybot/chat",
    StaticFiles(directory="/app/static/chat", html=True),
    name="chat",
)


# Serve index.html for homepage routes only (not chat)
@app.get("/policybot", response_class=HTMLResponse)
@app.get("/policybot/", response_class=HTMLResponse)
@app.get("/policybot/notebook", response_class=HTMLResponse)
@app.get("/policybot/notebook/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    """Serve index.html for homepage routes"""
    index_path = "/app/static/homepage/index.html"
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>PolicyBot</h1><p>Loading...</p>")


@app.get("/policybot/health", tags=["Health"], summary="Health check")
async def health_check():
    """Check if the API is running."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
