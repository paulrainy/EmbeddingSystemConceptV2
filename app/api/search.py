from fastapi import APIRouter, HTTPException
from app.schemas import SearchQuery, SearchResponse
from app.services import embeddings, milvus

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search(query: SearchQuery):
    vec = embeddings.embed(query.query)
    client = milvus._init_client()  # noqa: SLF001  (по-хорошему сделать обёртку)
    try:
        res = client.search(
            collection_name="test_cases",
            data=[vec.tolist()],
            limit=query.top_k,
            search_params={"metric_type": "IP", "params": {"ef": 64}},
            output_fields=["name"],
        )
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(503, detail=str(exc)) from exc

    hits = [
        {
            "id": hit.id,
            "score": hit.distance,
            "snippet": hit.entity.get("name"),
        }
        for hit in res[0]
    ]
    return {"hits": hits}
