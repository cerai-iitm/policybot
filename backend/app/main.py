from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_config


def create_app():
    app = FastAPI(
        title="PolicyBot API",
        version="1.0.0",
        description="AI-powered document processing and RAG (Retrieval-Augmented Generation) API. Organize PDFs into notebooks, process them through AI pipelines, and chat with your documents using natural language.",
        docs_url="/policybot/docs"
        if get_config().environment == "development"
        else None,
        redoc_url="/policybot/redoc"
        if get_config().environment == "development"
        else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["localhost", "cerai.iitm.ac.in"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
