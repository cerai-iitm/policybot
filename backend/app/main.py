from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.auth import router as auth_router
from api.routes.chat import router as chat_router
from api.routes.chat_sessions import router as chat_sessions_router
from api.routes.notebooks import router as notebooks_router
from api.routes.pdfs import router as pdfs_router

from .config import get_config
from .logger import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield


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
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "cerai.iitm.ac.in"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth_router, prefix="/policybot/api")
    app.include_router(notebooks_router, prefix="/policybot/api")
    app.include_router(pdfs_router, prefix="/policybot/api")
    app.include_router(chat_router, prefix="/policybot/api")
    app.include_router(chat_sessions_router, prefix="/policybot/api")

    # Mount _next static files at root (for HTML references) - DISABLED
    # app.mount(
    #     "/_next/static",
    #     StaticFiles(directory="/app/static/frontend/_next/static"),
    #     name="next-static",
    # )

    # Mount static files for assets - DISABLED
    # app.mount(
    #     "/policybot/assets",
    #     StaticFiles(directory="/app/static/frontend/_next/static"),
    #     name="assets",
    # )

    # Mount images - DISABLED
    # app.mount(
    #     "/policybot/images",
    #     StaticFiles(directory="/app/static/frontend/_next/static/media"),
    #     name="images",
    # )

    # Mount chat static files - DISABLED
    # app.mount(
    #     "/policybot/chat",
    #     StaticFiles(directory="/app/static/frontend/chat", html=True),
    #     name="chat",
    # )

    # Serve homepage
    # @app.get("/policybot", response_class=HTMLResponse)
    # @app.get("/policybot/", response_class=HTMLResponse)
    # async def serve_homepage():
    #     index_path = "/app/static/frontend/index.html"
    #     if os.path.exists(index_path):
    #         with open(index_path, "r") as f:
    #             return HTMLResponse(content=f.read())
    #     return HTMLResponse(content="<h1>PolicyBot</h1><p>Loading...</p>")

    # Serve notebook page (different from homepage!)
    # @app.get("/policybot/notebook", response_class=HTMLResponse)
    # @app.get("/policybot/notebook/", response_class=HTMLResponse)
    # async def serve_notebook():
    #     notebook_path = "/app/static/frontend/notebook/index.html"
    #     if os.path.exists(notebook_path):
    #         with open(notebook_path, "r") as f:
    #             return HTMLResponse(content=f.read())
    #     return HTMLResponse(content="<h1>Policy Notebooks</h1><p>Loading...</p>")

    # Serve config page
    # @app.get("/policybot/config", response_class=HTMLResponse)
    # @app.get("/policybot/config/", response_class=HTMLResponse)
    # async def serve_config():
    #     config_path = "/app/static/frontend/config/index.html"
    #     if os.path.exists(config_path):
    #         with open(config_path, "r") as f:
    #             return HTMLResponse(content=f.read())
    #     return HTMLResponse(content="<h1>Config</h1><p>Loading...</p>")

    @app.get("/policybot/health", tags=["Health"], summary="Health check")
    async def health_check():
        return {"status": "ok"}

    @app.get("/health")
    async def root_health():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
