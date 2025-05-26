from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Embedding System API", version="1.0.0")


@app.get("/healthz", tags=["system"])
async def health_check():
    return JSONResponse({"status": "ok"})