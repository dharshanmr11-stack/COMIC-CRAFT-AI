from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import BASE_DIR
from .routes import router


app = FastAPI(
    title="ComicCraft",
    description="AI Comic Story Creator",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(
        directory=str(BASE_DIR / "static")
    ),
    name="static",
)

app.include_router(router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "project": "ComicCraft",
    }