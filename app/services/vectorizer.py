from __future__ import annotations

"""Vectorisation (embedding) service.

Loads a *prepared* DataFrame from Redis (see :pyfile:`app/services/cache.py`),
computes sentence‐level embeddings with **Sentence‑Transformers** and returns the
vectors ready for insertion into Milvus.  The class deliberately contains no
FastAPI‑specific logic so that it can be reused from a CLI, background worker
or unit tests.
"""
from io import StringIO
from typing import List

import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer

from app.services import cache
from app.services.milvus import get_client as get_milvus_client  # thin helper assumed


class Vectorizer:
    """High‑level facade for «load → embed → insert» workflow."""

    MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

    def __init__(self, job_id: str, *, device: str | None = None) -> None:
        self.job_id = job_id
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model: SentenceTransformer | None = None
        self.df: pd.DataFrame | None = None
        self.embeddings: np.ndarray | None = None

    # ---------------------------------------------------------------------
    # Pipeline – public entry point
    # ---------------------------------------------------------------------
    async def run(self, collection: str) -> int:
        """End‑to‑end execution → returns number of vectors inserted."""
        self.df = await self._load_dataframe()
        self.embeddings = self._encode(self.df)
        inserted = self._insert_into_milvus(collection)
        return inserted

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    async def _load_dataframe(self) -> pd.DataFrame:
        raw = await cache.get_json(self.job_id)
        if raw is None:
            raise KeyError(f"job_id '{self.job_id}' not found or expired in Redis")
        return pd.read_json(StringIO(raw.decode()), orient="records")

    # ------------------------------------------------------------
    def _encode(self, df: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            self.model = SentenceTransformer(self.MODEL_NAME, device=self.device)
            self.model.max_seq_length = 512  # safety cap

        # Glue relevant fields into a single text per row
        sentences: List[str] = (
            df["Direction"].fillna("")
            + " | "
            + df["TestCaseName"].fillna("")
            + " | "
            + df["Steps"].fillna("")
            + " | "
            + df["ExpectedResult"].fillna("")
        ).tolist()

        with torch.inference_mode():
            embeds = self.model.encode(
                sentences,
                batch_size=32,
                normalize_embeddings=True,
                convert_to_numpy=True,
                device=self.device,
                show_progress_bar=False,
            )
        return embeds  # shape (N, 768)

    # ------------------------------------------------------------
    def _insert_into_milvus(self, collection: str) -> int:
        client = get_milvus_client(
            collection_name=collection,
            dim=self.embeddings.shape[1]
        )

        # Build rows for bulk insert
        rows = []
        for i, (emb, row) in enumerate(zip(self.embeddings, self.df.itertuples())):
            rows.append({
                "idx": i,
                "vector": emb,
                "inner_id": int(row.Id),
                "direction_name": str(row.Direction),
                "section_name": str(row.Section),
                "test_case_name": str(row.TestCaseName),
                "steps": str(row.Steps).replace("\n", " "),
                "expected_result": str(row.ExpectedResult).replace("\n", " "),
            })

        client.insert(collection_name=collection, data=rows)
        return len(rows)
