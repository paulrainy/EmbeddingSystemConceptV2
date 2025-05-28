import numpy as np
from sentence_transformers import SentenceTransformer

_MODEL: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _MODEL  # noqa: PLW0603
    if _MODEL is None:
        _MODEL = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    return _MODEL


def embed(text: str) -> np.ndarray:
    model = get_model()
    return model.encode([text])[0]  # shape (768,)
