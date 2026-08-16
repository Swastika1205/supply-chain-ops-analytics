"""
Core supply chain operations KPI aggregation.

Loads the shipment dataset and rolls it up into carrier/region performance
summaries and delay-reason bottleneck analysis, used by the SQL views,
notebook, and the intervention-prioritization layer (`prioritization.py`).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .data_quality import load_data


def build_operations_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Return carrier x region performance KPIs, including a priority_score.

    priority_score blends SLA breach rate (50%), delay severity relative to
    the worst-performing carrier/region pair (30%), and delay cost relative
    to the worst pair (20%). Weights are hand-set and documented here, not
    fitted to any outcome data.
    """
    x = df.copy()
    x["sla_breach_flag"] = ((x["delay_days"] > 0) | (x["sla_breach"] == 1)).astype(int)

    summary = x.groupby(["carrier", "region"], as_index=False).agg(
        shipments=("shipment_id", "count"),
        on_time_rate=("on_time", "mean"),
        sla_breach_rate=("sla_breach_flag", "mean"),
        avg_delay_days=("delay_days", "mean"),
        avg_shipment_cost=("shipment_cost", "mean"),
        estimated_delay_cost=("estimated_delay_cost", "sum"),
        shipment_value=("shipment_value", "sum"),
    )

    max_delay = summary["avg_delay_days"].max() or 1.0
    max_cost = summary["estimated_delay_cost"].max() or 1.0
    summary["priority_score"] = (
        summary["sla_breach_rate"] * 0.5
        + (summary["avg_delay_days"] / max_delay) * 0.3
        + (summary["estimated_delay_cost"] / max_cost) * 0.2
    )
    return summary.sort_values("priority_score", ascending=False)


def bottleneck_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Return delay-reason rollup (shipment count, avg delay, total cost),
    ranked by total estimated delay cost.
    """
    grouped = df.groupby("delay_reason", as_index=False)
    out = grouped.agg(
        avg_delay_days=("delay_days", "mean"),
        estimated_delay_cost=("estimated_delay_cost", "sum"),
    )
    out["shipments"] = grouped.size()["size"].to_numpy()
    return out.sort_values("estimated_delay_cost", ascending=False)


def monthly_sla_breach_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Return the overall SLA breach rate by month, for trend reporting."""
    out = df.groupby("month", as_index=False).agg(
        shipments=("shipment_id", "count"),
        sla_breach_rate=("sla_breach", "mean"),
    )
    return out.sort_values("month")


if __name__ == "__main__":
    data_path = Path(__file__).resolve().parents[1] / "data" / "supply_chain_performance.csv"
    dataset = load_data(str(data_path))
    print(build_operations_kpis(dataset).head(10).to_string(index=False))
    print("\nBottlenecks:")
    print(bottleneck_analysis(dataset).to_string(index=False))
