from __future__ import annotations

"""Endpoint for ingesting QA test‑cases from an Excel workbook into the
vector‑store.

The route can be called from the front end right after a manager uploads a new
spreadsheet :

```ts
await api.post('/ingest', { filename: 'docs/test_cases.xlsx' })
```

The server will read & pre‑process the file via :class:`TestCaseLoader` and
(optionally) feed embeddings into Milvus in a later step.  For now we return a
simple JSON payload with the number of extracted test‑cases.
"""

import uuid
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.case_loader import TestCaseLoader
from app.services import cache


router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestRequest(BaseModel):
    filename: str = Field(..., description="Relative path to the Excel file, e.g. 'docs/test_cases.xlsx'.")


class IngestResponse(BaseModel):
    imported: int = Field(..., description="Сколько тест-кейсов найдено")
    job_id: str = Field(..., description="ID, под которым JSON лежит в Redis")
    ttl: int = Field(..., description="Время жизни записи, сек")


@router.post("", response_model=IngestResponse)
async def ingest(req: IngestRequest):  # noqa: D401 – simple wrapper
    """Read the workbook and return how many cases we have just imported."""
    try:
        abs_path = Path(req.filename).resolve()
        loader = TestCaseLoader(abs_path)
        cases = loader.load()
        # 2. Сериализация в JSON (records - самый универсальный)
        df_all = pd.concat(cases, ignore_index=True)
        df_cases = (
            df_all
            .groupby("Id", as_index=False)
            .agg({
                "Direction":    "first",
                "Section":      "first",
                "TestCaseName": "first",
                "Steps":        lambda s: " ".join(s.dropna()),
                "ExpectedResult": "first",
            })
        )
        payload = df_cases.to_json(orient="records")

        # 3. Сохранение в Redis
        job_id = uuid.uuid4().hex
        ttl = cache.DEFAULT_TTL
        await cache.set_json(job_id, payload, ttl=ttl)

        return {"imported": len(cases), "job_id": job_id, "ttl": ttl}

    except FileNotFoundError as exc:
        raise HTTPException(404, detail=f"File not found: {exc}") from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(422, detail=str(exc)) from exc