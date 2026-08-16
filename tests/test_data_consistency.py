"""
Consistency checks between the shipped dataset and the code that explains
it. These specifically guard against the gap this project used to have:
`estimated_delay_cost` sitting in the CSV with no verifiable formula behind
it (and, on inspection, not even internally consistent with the
`cost_per_day_delay` column shipped alongside it).
"""
from src.cost_model import calculate_cost_per_day_delay, calculate_estimated_delay_cost
from src.data_quality import load_data

DATA_PATH = "data/supply_chain_performance.csv"


def test_shipped_cost_per_day_delay_matches_cost_model():
    df = load_data(DATA_PATH).sample(n=300, random_state=1)
    recomputed = df["shipment_value"].apply(calculate_cost_per_day_delay)
    assert (abs(recomputed.values - df["cost_per_day_delay"].values) < 0.01).all()


def test_shipped_estimated_delay_cost_matches_cost_model():
    df = load_data(DATA_PATH).sample(n=300, random_state=1)
    recomputed = df.apply(
        lambda row: calculate_estimated_delay_cost(row["shipment_value"], row["delay_days"]),
        axis=1,
    )
    assert (abs(recomputed.values - df["estimated_delay_cost"].values) < 0.05).all()


def test_estimated_delay_cost_is_zero_when_on_time():
    df = load_data(DATA_PATH)
    on_time = df[df["delay_days"] == 0]
    assert (on_time["estimated_delay_cost"] == 0).all()


def test_worst_carrier_has_higher_breach_rate_than_best_carrier():
    """Sanity check that carrier performance bias in the generator actually
    produces a measurable spread, rather than assuming it does.
    """
    df = load_data(DATA_PATH)
    breach_by_carrier = df.groupby("carrier")["sla_breach"].mean()
    assert breach_by_carrier.max() - breach_by_carrier.min() > 0.05
