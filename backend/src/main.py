from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import chat_router, notebooks_router, pdf_router

app = FastAPI(
    title="PolicyBot API",
    version="1.0.0",
    description="AI-powered document processing and RAG (Retrieval-Augmented Generation) API. Organize PDFs into notebooks, process them through AI pipelines, and chat with your documents using natural language.",
    docs_url="/docs",
    redoc_url="/redoc",
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


app.include_router(pdf_router, prefix="/policybot/api/pdf")
app.include_router(notebooks_router, prefix="/policybot/api")
app.include_router(chat_router, prefix="/policybot/api")


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to PolicyBot Backend", "docs": "/docs"}


@app.get("/health", tags=["Health"], summary="Health check")
async def health_check():
    """Check if the API is running."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
