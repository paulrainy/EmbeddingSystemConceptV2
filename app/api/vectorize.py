from __future__ import annotations

"""API‑эндпоинт, инициирующий процесс «из Redis → Sentence‑Transformers → Milvus».

POST /vectorize
--------------
Request JSON:
    { "job_id": "<uuid>", "collection": "testcases_v1" }

Response JSON:
    { "inserted": 64, "collection": "testcases_v1" }
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.vectorizer import Vectorizer

router = APIRouter(prefix="/vectorize", tags=["vectorize"])


class VectorizeRequest(BaseModel):
    job_id: str = Field(..., description="ID, под которым набор хранится в Redis")
    collection: str = Field(..., description="Имя целевой коллекции Milvus")


class VectorizeResponse(BaseModel):
    inserted: int
    collection: str


@router.post("", response_model=VectorizeResponse, status_code=status.HTTP_202_ACCEPTED)
async def vectorize(req: VectorizeRequest):
    """Асинхронный хэндлер: извлекает подготовленный датасет, строит эмбеддинги и сохраняет их."""
    try:
        svc = Vectorizer(req.job_id)
        inserted = await svc.run(req.collection)
        return {"inserted": inserted, "collection": req.collection}
    except KeyError as exc:  # job_id не найден / устарел
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 – все прочие ошибки
        raise HTTPException(status_code=422, detail=str(exc)) from exc
