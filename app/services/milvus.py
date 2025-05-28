from pymilvus import (
    MilvusClient,
    DataType,
    FieldSchema,
    CollectionSchema,
)
from app.core.config import get_settings

settings = get_settings()

_CLIENT: MilvusClient | None = None
_COLLECTION_NAME = "test_cases"
_DIMENSION = 768


def _init_client() -> MilvusClient:
    global _CLIENT  # pylint: disable=global-statement
    if _CLIENT is None:
        _CLIENT = MilvusClient(
            uri=f"{settings.milvus_host}:{settings.milvus_port}"
        )
        if _COLLECTION_NAME not in _CLIENT.list_collections():
            _create_collection()
    return _CLIENT


def _create_collection() -> None:
    schema = CollectionSchema(
        fields=[
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True,
            ),
            FieldSchema(
                name="vector",
                dtype=DataType.FLOAT_VECTOR,
                dim=_DIMENSION,
            ),
            FieldSchema(name="direction", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="section", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=256),
        ]
    )
    _CLIENT.create_collection(collection_name=_COLLECTION_NAME, schema=schema)
    _CLIENT.create_index(
        collection_name=_COLLECTION_NAME,
        field_name="vector",
        index_type="HNSW",
        metric_type="IP",
        params={"M": 16, "efConstruction": 64},
    )

