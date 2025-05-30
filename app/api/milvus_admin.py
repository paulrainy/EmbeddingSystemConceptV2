from __future__ import annotations

"""
Milvus — административные и поисковые операции.

•   GET    /milvus/{collection}/dump        — печатает содержимое коллекции в консоль
•   POST   /milvus/search                   — поиск по idx / inner_id / векторному запросу
•   DELETE /milvus/{collection}             — полное удаление коллекции
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, conlist
import numpy as np
from typing import Any, List, Dict

from app.services.milvus import get_client

router = APIRouter(prefix="/milvus", tags=["milvus"])


# -------------------------------------------------------------------------#
#                                 helpers                                 #
# -------------------------------------------------------------------------#

_OUT_FIELDS = [
    "idx",
    "vector",
    "inner_id",
    "direction_name",
    "section_name",
    "test_case_name",
]


def _collection_or_404(client, name: str):
    if not client.has_collection(name):
        raise HTTPException(status_code=404, detail=f"Collection '{name}' not found")
    return name


# -------------------------------------------------------------------------#
#                          списoк коллекций                                #
# -------------------------------------------------------------------------#

class CollectionsResponse(BaseModel):
    collections: List[str]

@router.get("/collections", response_model=CollectionsResponse)
def list_collections():
    """
    Возвращает список всех коллекций, доступных в Milvus.
    """
    client = get_client()
    return {"collections": client.list_collections()}


# -------------------------------------------------------------------------#
#                               dump (JSON)                                #
# -------------------------------------------------------------------------#

def _to_py(obj: Any) -> Any:
    """Рекурсивно превращает объекты NumPy в чистые Python-типы,
    оставляя обычные int/float без изменений."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):          # np.float32, np.int64 и др.
        return obj.item()
    if isinstance(obj, list):
        return [_to_py(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _to_py(v) for k, v in obj.items()}
    return obj                                # обычные int/float/str остаются как есть

class DumpResponse(BaseModel):
    rows: List[Dict[str, Any]]

@router.get("/{collection}/dump", response_model=DumpResponse)
def dump_collection(collection: str, limit: int = 1000):
    client = get_client()
    _collection_or_404(client, collection)

    raw_rows = client.query(
        collection_name=collection,
        filter="idx >= 0",
        limit=limit,
        output_fields=_OUT_FIELDS,
    )
    safe_rows = [_to_py(row) for row in raw_rows]
    return {"rows": safe_rows}



# -------------------------------------------------------------------------#
#                                   search                                 #
# -------------------------------------------------------------------------#


Vector768 = conlist(float, min_length=768, max_length=768)

class SearchRequest(BaseModel):
    collection: str = Field(..., description="Имя коллекции Milvus")
    mode: str = Field(
        ...,
        description="Режим поиска: idx | inner_id | semantic",
        pattern="^(idx|inner_id|semantic)$",
    )
    idx: Optional[List[int]] = Field(None, description="Список первичных id (mode=idx)")
    inner_id: Optional[int] = Field(None, description="Внутренний id тест-кейса")
    vector: Optional[Vector768] = Field( # type: ignore[valid-type]
        None, description="Нормированный эмбеддинг длиной 768 (mode=semantic)"
    )
    limit: int = Field(10, ge=1, le=128, description="Сколько результатов вернуть")

class SearchResponse(BaseModel):
    results: List[dict]


@router.post(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Поиск в Milvus",
)
def search(request: SearchRequest):
    client = get_client()
    _collection_or_404(client, request.collection)

    if request.mode == "idx":
        if not request.idx:
            raise HTTPException(422, detail="Поле 'idx' обязательно при mode=idx")
        rows = client.get(
            collection_name=request.collection, ids=request.idx, output_fields=_OUT_FIELDS
        )
        return {"results": rows}

    if request.mode == "inner_id":
        if request.inner_id is None:
            raise HTTPException(
                422, detail="Поле 'inner_id' обязательно при mode=inner_id"
            )
        rows = client.query(
            collection_name=request.collection,
            filter=f"inner_id == {request.inner_id}",
            output_fields=_OUT_FIELDS,
        )
        return {"results": rows}

    if request.mode == "semantic":
        if request.vector is None:
            raise HTTPException(
                422, detail="Поле 'vector' обязательно при mode=semantic"
            )
        hits = client.search(
            collection_name=request.collection,
            anns_field="vector",
            data=[request.vector],
            limit=request.limit,
            output_fields=_OUT_FIELDS,
            search_params={"metric_type": "COSINE", "params": {}},
        )
        return {"results": hits[0]}

    raise HTTPException(422, "Неподдерживаемый режим поиска")


# -------------------------------------------------------------------------#
#                                drop / clean                              #
# -------------------------------------------------------------------------#


class DropResponse(BaseModel):
    dropped: str


@router.delete("/{collection}", response_model=DropResponse, status_code=200)
def drop_collection(collection: str):
    """
    Полностью удаляет коллекцию Milvus.
    """
    client = get_client()
    _collection_or_404(client, collection)

    client.drop_collection(collection_name=collection)
    return {"dropped": collection}

