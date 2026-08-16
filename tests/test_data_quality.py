import pandas as pd
from src.data_quality import validate_data

def test_quality():
    df=pd.DataFrame({"shipment_id":["1","1"],"delay_days":[0,-1]})
    result=validate_data(df)
    assert result["duplicate_shipments"]==1
    assert result["negative_delay"]==1
