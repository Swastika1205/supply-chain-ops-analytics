# DAX Measure Catalog

Example measures for a Power BI implementation.

```DAX
Shipment Volume = COUNTROWS(FinSightOps)

On-Time Delivery % = DIVIDE(
    CALCULATE([Shipment Volume], FinSightOps[on_time] = 1),
    [Shipment Volume],
    0
)

SLA Breach Rate = DIVIDE(
    CALCULATE([Shipment Volume], FinSightOps[sla_breach] = 1),
    [Shipment Volume],
    0
)

Average Delay Days = AVERAGE(FinSightOps[delay_days])

Average Shipment Cost = AVERAGE(FinSightOps[shipment_cost])

Estimated Delay Cost = SUM(FinSightOps[estimated_delay_cost])
```

For a date table:

```DAX
Shipments PY =
CALCULATE(
    [Shipment Volume],
    SAMEPERIODLASTYEAR('Calendar'[Date])
)

Shipment YoY % =
DIVIDE([Shipment Volume] - [Shipments PY], [Shipments PY], 0)
```
