from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api import ingest as ingest_router
from app.api import vectorize as vectorize_router
from app.api import milvus_admin as milvus_router

app = FastAPI(title="Embedding System API", version="1.0.0")


@app.get("/healthz", tags=["system"])
async def health_check():
    return JSONResponse({"status": "ok"})

# Domain routers -------------------------------------------------------------
app.include_router(ingest_router.router)
app.include_router(vectorize_router.router)
app.include_router(milvus_router.router)
