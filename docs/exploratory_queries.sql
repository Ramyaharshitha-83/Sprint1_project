-- Total Companies
SELECT COUNT(*) FROM companies;

-- Top 10 Companies by Net Profit
SELECT company_id,
       MAX(net_profit) AS max_profit
FROM profitandloss
GROUP BY company_id
ORDER BY max_profit DESC
LIMIT 10;

-- Sector Distribution
SELECT broad_sector,
       COUNT(*)
FROM sectors
GROUP BY broad_sector
ORDER BY COUNT(*) DESC;

-- Highest Average ROE
SELECT company_id,
       AVG(return_on_equity_pct) AS avg_roe
FROM financial_ratios
GROUP BY company_id
ORDER BY avg_roe DESC
LIMIT 10;

-- Highest Trading Volume
SELECT company_id,
       SUM(volume) AS total_volume
FROM stock_prices
GROUP BY company_id
ORDER BY total_volume DESC
LIMIT 10;