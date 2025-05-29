from __future__ import annotations

"""Utility for importing and pre‑processing QA test‑case suites stored in an Excel
workbook before they are embedded and ingested into Milvus.

The logic is a lightly refactored version of the original `import_df` /
`prepare_df` helpers provided in chat. The algorithmic steps and, therefore,
its *output* remain **identical** to the reference implementation – we only
broke the code into a few small private helpers and added type hints, logging
and doc‑strings for better maintainability.
"""

from pathlib import Path
from typing import List
import logging
import math

import pandas as pd
from pandas import DataFrame

logger = logging.getLogger(__name__)


class TestCaseLoader:  # noqa: D101 – docstring provided at class level
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.df: DataFrame | None = None
        self.prepared_df: List[DataFrame] | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def load(self) -> List[DataFrame]:
        """Read *and* prepare the Excel workbook.

        This is a thin convenience wrapper that consecutively calls
        :py:meth:`_import_raw` and :py:meth:`_prepare`. It returns the list of
        per‑test‑case DataFrames so that callers can further process or embed
        them right away.
        """
        self.df = self._import_raw()
        self.prepared_df = self._prepare(self.df)
        return self.prepared_df

    # ------------------------------------------------------------------
    # Implementation details – mirrored one‑to‑one from the original code
    # ------------------------------------------------------------------
    def _import_raw(self) -> DataFrame:  # noqa: D401
        """Load the workbook into a :class:`pandas.DataFrame`."""
        try:
            df = pd.read_excel(self.file_path)
            logger.info("☑  Imported %s rows from %s", len(df), self.file_path)
            return df
        except Exception as exc:  # pylint: disable=broad-except
            raise ValueError(f"Error importing file '{self.file_path}': {exc}") from exc

    # The remaining helpers are a straight port of the three processing blocks
    # from the original `prepare_df` function – split out so they are testable
    # in isolation.
    @staticmethod
    def _remove_useless_columns(df: DataFrame) -> DataFrame:
        # Keep only the columns we actually need and forward‑fill identifiers.
        keeper_cols = [
            "Id",
            "Direction",
            "Section",
            "TestCaseName",
            "Preconditions",
            "Steps",
            "Postconditions",
            "ExpectedResult",
        ]
        out = df[keeper_cols].copy()
        out[["Id", "Direction", "Section", "TestCaseName"]] = out[
            ["Id", "Direction", "Section", "TestCaseName"]
        ].ffill()
        return out

    @staticmethod
    def _split_by_id(df: DataFrame) -> List[DataFrame]:
        return [frame for _, frame in df.groupby("Id")]

    @staticmethod
    def _compact_case(frames: List[DataFrame]) -> List[DataFrame]:
        def _bubble_up(cell_df: DataFrame, column: str) -> DataFrame:
            # Shift each cell value one row up so that the content of row i+1
            # becomes the content of row i. For the terminal row we insert NaN
            # (keeps the overall semantics of the original implementation).
            for i in range(len(cell_df[column])):
                if i == len(cell_df.index) - 1:
                    cell_df.at[cell_df.index[i], column] = math.nan
                else:
                    cell_df.at[cell_df.index[i], column] = cell_df.at[
                        cell_df.index[i + 1], column
                    ]
            return cell_df

        for frame in frames:
            for col in [
                "Preconditions",
                "Steps",
                "Postconditions",
                "ExpectedResult",
            ]:
                frame = _bubble_up(frame, col)

            # Combine multi‑row logical fields the same way the original script
            # did.
            frame["Steps"] = frame["Steps"].fillna(frame["Preconditions"])
            frame["Steps"] = frame["Steps"].fillna(frame["Postconditions"])
            frame.drop(["Preconditions", "Postconditions"], axis=1, inplace=True)

        return frames

    # ------------------------------------------------------------
    # Orchestrator for the three internal steps
    # ------------------------------------------------------------
    def _prepare(self, df: DataFrame) -> List[DataFrame]:
        logger.info("⚙  Preparing data …")
        step1 = self._remove_useless_columns(df)
        logger.debug("  – Useless columns removed")

        step2 = self._split_by_id(step1)
        logger.debug("  – Test‑cases split by Id")

        final = self._compact_case(step2)
        logger.debug("  – Empty cells bubble‑up complete")
        logger.info("☑  Preparation done – %s distinct cases", len(final))
        return final
