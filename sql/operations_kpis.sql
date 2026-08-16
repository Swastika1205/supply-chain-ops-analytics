-- KPI names aligned with dashboards/dax_measures.md
-- DAX: Shipment Volume / On-Time Delivery % / SLA Breach Rate /
--      Average Delay Days / Average Shipment Cost / Estimated Delay Cost

SELECT
  COUNT(*) AS shipment_volume,
  AVG(on_time) AS on_time_delivery_pct,
  AVG(sla_breach) AS sla_breach_rate,
  AVG(delay_days) AS average_delay_days,
  AVG(shipment_cost) AS average_shipment_cost,
  SUM(estimated_delay_cost) AS estimated_delay_cost
FROM supply_chain_performance;

-- Carrier view
SELECT
  carrier,
  COUNT(*) AS shipment_volume,
  AVG(on_time) AS on_time_delivery_pct,
  AVG(sla_breach) AS sla_breach_rate,
  AVG(delay_days) AS average_delay_days,
  AVG(shipment_cost) AS average_shipment_cost,
  SUM(estimated_delay_cost) AS estimated_delay_cost
FROM supply_chain_performance
GROUP BY carrier
ORDER BY sla_breach_rate DESC;

-- Regional bottlenecks
SELECT
  region,
  delay_reason,
  COUNT(*) AS shipment_volume,
  AVG(delay_days) AS average_delay_days,
  SUM(estimated_delay_cost) AS estimated_delay_cost
FROM supply_chain_performance
WHERE delay_days > 0
GROUP BY region, delay_reason
ORDER BY estimated_delay_cost DESC;

-- Tier-1 vs Tier-2 service
SELECT
  region_tier,
  COUNT(*) AS shipment_volume,
  AVG(on_time) AS on_time_delivery_pct,
  AVG(sla_breach) AS sla_breach_rate,
  AVG(delay_days) AS average_delay_days
FROM supply_chain_performance
GROUP BY region_tier
ORDER BY sla_breach_rate DESC;

-- Month-over-month change in SLA breach rate per carrier, using LAG()
-- instead of a self-join.
SELECT
  carrier,
  month,
  sla_breach_rate,
  sla_breach_rate - LAG(sla_breach_rate) OVER (
    PARTITION BY carrier ORDER BY month
  ) AS change_vs_prior_month
FROM (
  SELECT
    carrier,
    month,
    AVG(sla_breach) AS sla_breach_rate
  FROM supply_chain_performance
  GROUP BY carrier, month
) monthly
ORDER BY carrier, month;

-- Rank carriers by SLA breach rate within each region (window function),
-- rather than a single global ranking that ignores regional difficulty.
SELECT region, carrier, shipment_volume, sla_breach_rate, rnk
FROM (
  SELECT
    region,
    carrier,
    COUNT(*) AS shipment_volume,
    AVG(sla_breach) AS sla_breach_rate,
    RANK() OVER (
      PARTITION BY region ORDER BY AVG(sla_breach) DESC
    ) AS rnk
  FROM supply_chain_performance
  GROUP BY region, carrier
) ranked
WHERE rnk <= 3
ORDER BY region, rnk;
