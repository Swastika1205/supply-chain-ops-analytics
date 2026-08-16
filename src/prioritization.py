"""
Intervention prioritization.

Bands carrier/region pairs into Monitor / Investigate / Priority tiers
based on the priority_score computed in `analytics.py`, for use by
operations teams deciding where to focus first.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .analytics import build_operations_kpis
from .data_quality import load_data

PRIORITY_BINS = [-float("inf"), 0.25, 0.5, float("inf")]
PRIORITY_LABELS = ["Monitor", "Investigate", "Priority"]


def prioritize_interventions(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Return the top_n carrier/region pairs ranked by priority_score, with a priority_band."""
    summary = build_operations_kpis(df).copy()
    summary["priority_band"] = pd.cut(
        summary["priority_score"], bins=PRIORITY_BINS, labels=PRIORITY_LABELS
    )
    return summary.sort_values("priority_score", ascending=False).head(top_n)


if __name__ == "__main__":
    data_path = Path(__file__).resolve().parents[1] / "data" / "supply_chain_performance.csv"
    dataset = load_data(str(data_path))
    print(prioritize_interventions(dataset).to_string(index=False))
