"""Milvus helper – singleton client + collection bootstrap.

This module exposes a public :func:`get_client` so that other services (e.g.
Vectorizer) can depend on a stable interface instead of the previously
underscore‑prefixed internal function.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Final, Optional

from pymilvus import DataType, FieldSchema, MilvusClient, CollectionSchema

from app.core.config import get_settings

_SETTINGS = get_settings()
_DEFAULT_DIM: Final[int] = 768


@lru_cache
def _base_client() -> MilvusClient:  # noqa: D401 – factory
    """Create or return a cached Milvus client."""
    return MilvusClient(uri=f"http://{_SETTINGS.milvus_host}:{_SETTINGS.milvus_port}")


def _ensure_collection(client: MilvusClient, name: str, dim: int = _DEFAULT_DIM) -> None:
    """Create collection *name* if it does not yet exist."""
    if client.has_collection(name):
        return

    schema = CollectionSchema(
        fields=[
            FieldSchema(name="idx", dtype=DataType.INT64, is_primary=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="inner_id", dtype=DataType.INT64),
            FieldSchema(name="direction_name", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="section_name", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="test_case_name", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="steps", dtype=DataType.VARCHAR, max_length=8192),
            FieldSchema(name="expected_result", dtype=DataType.VARCHAR, max_length=8192),
        ]
    )

    index_params = client.prepare_index_params()
    index_params.add_index("idx", "STL_SORT")
    index_params.add_index("vector", "IVF_FLAT", metric_type="COSINE", params={"nlist": 128})

    client.create_collection(collection_name=name, schema=schema, index_params=index_params)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_client(collection_name: Optional[str] = None, *, dim: int = _DEFAULT_DIM) -> MilvusClient:  # noqa: D401
    """Return the singleton Milvus client; optionally create *collection_name* if missing."""
    client = _base_client()
    if collection_name is not None:
        _ensure_collection(client, collection_name, dim=dim)
    return client
