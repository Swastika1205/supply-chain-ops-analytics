"""
Generate the synthetic supply chain / carrier performance dataset.

This is the piece that was previously missing: earlier versions of this
project shipped `cost_per_day_delay` and `estimated_delay_cost` as
pre-existing CSV columns with no code showing how they were produced (and,
on inspection, they weren't even internally consistent with each other).
This script is the single source of truth for both now, via
`src/cost_model.py`, so the shipped CSV and the analysis code are
guaranteed to agree.

Usage:
    python scripts/generate_data.py
    python scripts/generate_data.py --rows 7865 --seed 7 --out data/supply_chain_performance.csv
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.cost_model import calculate_cost_per_day_delay, calculate_estimated_delay_cost  # noqa: E402

START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)

REGION_TIER = {"North": "Tier-1", "South": "Tier-2", "East": "Tier-2", "West": "Tier-1"}

# Per-carrier on-time probability and delay-severity bias. These are
# illustrative synthetic archetypes chosen to produce a clear, explainable
# performance spread across carriers — not derived from any real carrier.
CARRIER_PROFILES = {
    "Rapidor Shipping":   dict(code="RAP", on_time_prob=0.94, delay_severity=1.0),
    "SwiftHaul":          dict(code="SWI", on_time_prob=0.90, delay_severity=1.2),
    "BlueDartX":          dict(code="BDX", on_time_prob=0.88, delay_severity=1.3),
    "MeridianRoute":      dict(code="MER", on_time_prob=0.88, delay_severity=1.4),
    "Northarc Logistics": dict(code="NOR", on_time_prob=0.85, delay_severity=1.6),
    "TransAxis":          dict(code="TRA", on_time_prob=0.84, delay_severity=1.7),
}

DELAY_REASONS = ["Hub congestion", "Address issue", "Linehaul delay", "Capacity shortage", "Weather"]
DELAY_REASON_WEIGHTS = [0.36, 0.18, 0.16, 0.14, 0.16]


def _random_date(rng: np.random.Generator) -> date:
    span = (END_DATE - START_DATE).days
    return START_DATE + timedelta(days=int(rng.integers(0, span + 1)))


def generate(n_rows: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    carriers = list(CARRIER_PROFILES.keys())
    regions = list(REGION_TIER.keys())

    rows = []
    carrier_seq = {c: 0 for c in carriers}

    for _ in range(n_rows):
        carrier = rng.choice(carriers)
        profile = CARRIER_PROFILES[carrier]
        region = rng.choice(regions)
        region_tier = REGION_TIER[region]
        shipment_date = _random_date(rng)
        carrier_seq[carrier] += 1

        shipment_id = f"SC-{shipment_date.month:02d}-{profile['code']}-{carrier_seq[carrier]:05d}"

        expected_days = int(rng.choice([2, 3, 4, 5]))
        shipment_value = max(15.0, round(rng.normal(180, 90), 2))
        shipment_cost = round(max(10.0, rng.normal(90, 30)), 2)

        on_time_prob = profile["on_time_prob"]
        if region_tier == "Tier-2":
            on_time_prob -= 0.05  # Tier-2 regions are modestly harder to service on time
        on_time_prob = float(np.clip(on_time_prob, 0.05, 0.98))

        is_on_time = rng.random() < on_time_prob

        if is_on_time:
            actual_days = expected_days
            delay_days = 0
            delay_reason = "On time"
            sla_breach = 0
        else:
            base_delay = rng.gamma(shape=2.0, scale=profile["delay_severity"])
            delay_days = max(1, round(base_delay))
            actual_days = expected_days + delay_days
            delay_reason = str(rng.choice(DELAY_REASONS, p=DELAY_REASON_WEIGHTS))
            sla_breach = 1

        status = "In Transit" if shipment_date > (END_DATE - timedelta(days=5)) else "Delivered"

        cost_per_day_delay = round(calculate_cost_per_day_delay(shipment_value), 3)
        estimated_delay_cost = round(calculate_estimated_delay_cost(shipment_value, delay_days), 2)

        rows.append(
            {
                "shipment_id": shipment_id,
                "shipment_date": shipment_date.isoformat(),
                "carrier": carrier,
                "region": region,
                "region_tier": region_tier,
                "expected_days": expected_days,
                "actual_days": actual_days,
                "delay_days": delay_days,
                "on_time": int(is_on_time),
                "sla_breach": sla_breach,
                "delay_reason": delay_reason,
                "shipment_cost": shipment_cost,
                "status": status,
                "shipment_value": shipment_value,
                "month": shipment_date.month,
                "cost_per_day_delay": cost_per_day_delay,
                "estimated_delay_cost": estimated_delay_cost,
            }
        )

    df = pd.DataFrame(rows)
    column_order = [
        "shipment_id", "shipment_date", "carrier", "region", "region_tier",
        "expected_days", "actual_days", "delay_days", "on_time", "sla_breach",
        "delay_reason", "shipment_cost", "status", "shipment_value", "month",
        "cost_per_day_delay", "estimated_delay_cost",
    ]
    return df[column_order]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the synthetic supply chain performance dataset.")
    parser.add_argument("--rows", type=int, default=7865)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", type=str, default="data/supply_chain_performance.csv")
    args = parser.parse_args()

    df = generate(args.rows, args.seed)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} rows to {args.out}")
    print(df.groupby("carrier")["sla_breach"].mean().sort_values().to_string())
    print(f"Overall on-time rate: {df['on_time'].mean():.2%}")


if __name__ == "__main__":
    main()
