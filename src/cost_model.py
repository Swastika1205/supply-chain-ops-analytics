"""
Delay-cost model.

This module makes the delay-cost assumption explicit and reproducible,
rather than leaving it as an opaque column in the dataset. It is used both
by `scripts/generate_data.py` (to produce the synthetic dataset) and is
available for recomputation/validation against the shipped CSV.

ASSUMPTION (documented, not claimed as real-world calibrated):
Each shipment has a per-day delay cost derived from its declared shipment
value, plus a small fixed handling surcharge. This reflects the idea that
delaying a higher-value shipment is more expensive (capital tied up,
customer-service risk) than delaying a low-value one. The exact
coefficients below are illustrative for a portfolio project — in a real
engagement they would be calibrated against actual carrier penalty clauses
and customer SLAs, not assumed.
"""
from __future__ import annotations

# Fixed per-shipment daily handling surcharge, independent of value.
BASE_DAILY_HANDLING_COST: float = 5.0

# Fraction of shipment value treated as daily carrying/risk cost while delayed.
VALUE_BASED_DAILY_RATE: float = 0.01


def calculate_cost_per_day_delay(shipment_value: float) -> float:
    """Return the assumed cost of one day of delay for a shipment of this value.

    cost_per_day_delay = BASE_DAILY_HANDLING_COST + (shipment_value * VALUE_BASED_DAILY_RATE)
    """
    return BASE_DAILY_HANDLING_COST + (shipment_value * VALUE_BASED_DAILY_RATE)


def calculate_estimated_delay_cost(shipment_value: float, delay_days: float) -> float:
    """Return the total estimated cost attributable to a shipment's delay.

    estimated_delay_cost = delay_days * cost_per_day_delay(shipment_value)

    Returns 0.0 for on-time shipments (delay_days <= 0).
    """
    if delay_days <= 0:
        return 0.0
    return delay_days * calculate_cost_per_day_delay(shipment_value)
