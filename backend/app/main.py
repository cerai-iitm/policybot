from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from .config import get_config
from api.routes.auth import router as auth_router
from api.routes.notebooks import router as notebooks_router
from api.routes.pdfs import router as pdfs_router
from api.routes.chat import router as chat_router


def create_app():
    app = FastAPI(
        title="PolicyBot API",
        version="1.0.0",
        description="AI-powered document processing and RAG API",
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

    # Include routers
    app.include_router(auth_router, prefix="/policybot/api")
    app.include_router(notebooks_router, prefix="/policybot/api")
    app.include_router(pdfs_router, prefix="/policybot/api")
    app.include_router(chat_router, prefix="/policybot/api")

    # Static file serving
    app.mount(
        "/policybot/assets",
        StaticFiles(directory="/app/static/homepage/assets"),
        name="assets",
    )
    app.mount(
        "/policybot/images",
        StaticFiles(directory="/app/static/homepage/assets"),
        name="images",
    )
    app.mount(
        "/policybot/chat",
        StaticFiles(directory="/app/static/chat", html=True),
        name="chat",
    )

    @app.get("/policybot/health", tags=["Health"], summary="Health check")
    async def health_check():
        return {"status": "ok"}

    @app.get("/health")
    async def root_health():
        return {"status": "ok"}

    # SPA catch-all routes
    @app.get("/policybot", response_class=HTMLResponse)
    @app.get("/policybot/", response_class=HTMLResponse)
    @app.get("/policybot/notebook", response_class=HTMLResponse)
    @app.get("/policybot/notebook/", response_class=HTMLResponse)
    async def serve_spa():
        return FileResponse("/app/static/homepage/index.html")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
