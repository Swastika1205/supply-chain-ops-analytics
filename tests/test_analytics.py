import pandas as pd
from src.analytics import build_operations_kpis, bottleneck_analysis

def test_operations_kpis():
    df=pd.DataFrame({
        "shipment_id":["1","2"],
        "shipment_date":pd.to_datetime(["2025-01-01","2025-01-02"]),
        "carrier":["A","A"],"region":["North","North"],"region_tier":["Tier-1","Tier-1"],
        "expected_days":[2,2],"actual_days":[2,4],"delay_days":[0,2],
        "on_time":[1,0],"sla_breach":[0,1],"delay_reason":["On time","Hub congestion"],
        "shipment_cost":[100,120],"status":["Delivered","Delivered"],
        "shipment_value":[500,700],"estimated_delay_cost":[0,15]
    })
    out=build_operations_kpis(df)
    assert len(out)==1
    assert out.iloc[0]["shipments"]==2
    assert out.iloc[0]["sla_breach_rate"]==0.5

def test_bottlenecks():
    df=pd.DataFrame({"delay_reason":["Hub","Hub","Weather"],"delay_days":[2,1,3],"estimated_delay_cost":[10,5,20]})
    out=bottleneck_analysis(df)
    assert out.iloc[0]["delay_reason"]=="Weather"
