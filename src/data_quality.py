"""
Data ingestion and quality checks for the supply chain performance dataset.
"""
from __future__ import annotations

from typing import Dict

import pandas as pd

REQUIRED_COLUMNS = {
    "shipment_id", "shipment_date", "carrier", "region", "region_tier",
    "expected_days", "actual_days", "delay_days", "on_time", "sla_breach",
    "delay_reason", "shipment_cost", "status", "shipment_value",
}


def load_data(path: str) -> pd.DataFrame:
    """Load and validate the supply chain performance dataset."""
    df = pd.read_csv(path, parse_dates=["shipment_date"])
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return df


def validate_data(df: pd.DataFrame) -> Dict[str, int]:
    """Run basic data-quality checks and return a summary dict."""
    return {
        "rows": len(df),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_shipments": int(df.duplicated(subset=["shipment_id"]).sum()),
        "negative_delay": int((df["delay_days"] < 0).sum()),
    }
