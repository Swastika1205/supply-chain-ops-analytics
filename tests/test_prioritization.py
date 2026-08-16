import pandas as pd
from src.prioritization import prioritize_interventions


def test_priority_bands_and_ordering():
    df = pd.DataFrame({
        "shipment_id": ["1", "2", "3", "4"],
        "shipment_date": pd.to_datetime(
            ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"]
        ),
        "carrier": ["A", "A", "B", "B"],
        "region": ["North", "North", "South", "South"],
        "region_tier": ["Tier-1", "Tier-1", "Tier-2", "Tier-2"],
        "expected_days": [2, 2, 2, 2],
        "actual_days": [2, 5, 6, 2],
        "delay_days": [0, 3, 4, 0],
        "on_time": [1, 0, 0, 1],
        "sla_breach": [0, 1, 1, 0],
        "delay_reason": ["On time", "Hub congestion", "Capacity shortage", "On time"],
        "shipment_cost": [100, 120, 130, 100],
        "status": ["Delivered"] * 4,
        "shipment_value": [500, 700, 800, 450],
        "estimated_delay_cost": [0, 22.5, 30, 0],
    })

    result = prioritize_interventions(df, top_n=10)

    assert not result.empty
    assert "priority_score" in result.columns
    assert "priority_band" in result.columns
    assert result["priority_score"].is_monotonic_decreasing
    assert set(result["priority_band"].astype(str)).issubset(
        {"Monitor", "Investigate", "Priority"}
    )
