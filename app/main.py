from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api import search as search_router
from app.api import ingest as ingest_router

app = FastAPI(title="Embedding System API", version="1.0.0")


@app.get("/healthz", tags=["system"])
async def health_check():
    return JSONResponse({"status": "ok"})

# Domain routers -------------------------------------------------------------
app.include_router(search_router.router)
app.include_router(ingest_router.router)