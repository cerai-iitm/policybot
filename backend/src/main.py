from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import cfg

app = FastAPI(title="PolicyBot Backend", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[cfg.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to PolicyBot Backend"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
