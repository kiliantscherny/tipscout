---
title: tipscout Statistics
---

## Active Deals

```sql active_deals
SELECT
    deal_id,
    merchant_name,
    CASE
        WHEN TRY_CAST(sold AS INTEGER) IS NOT NULL AND TRY_CAST(remaining AS INTEGER) IS NOT NULL
        THEN TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER)
        ELSE NULL
    END AS total_available,
    sold,
    remaining,
    CASE
        WHEN TRY_CAST(sold AS INTEGER) IS NOT NULL AND TRY_CAST(remaining AS INTEGER) IS NOT NULL
             AND (TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER)) > 0
        THEN CAST(TRY_CAST(remaining AS INTEGER) AS FLOAT) / (TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER))
        ELSE NULL
    END AS remaining_percent,
    CASE
        WHEN TRY_CAST(old_price AS FLOAT) IS NOT NULL AND TRY_CAST(new_price AS FLOAT) IS NOT NULL
             AND TRY_CAST(old_price AS FLOAT) > 0
        THEN (TRY_CAST(old_price AS FLOAT) - TRY_CAST(new_price AS FLOAT)) / TRY_CAST(old_price AS FLOAT)
        ELSE NULL
    END AS discount_percent,
    full_url
FROM tipster_data.deals
WHERE status = 'ACTIVE'
ORDER BY remaining_percent ASC NULLS LAST
```

<DataTable data={active_deals} emptySet="warn" emptyMessage="No active deals found at the moment. Check back soon for new opportunities!">
    <Column id="deal_id" title="Deal ID"/>
    <Column id="merchant_name" title="Merchant Name"/>
    <Column id="total_available" title="Total Available"/>
    <Column id="sold" title="Sold"/>
    <Column id="remaining" title="Remaining"/>
    <Column id="remaining_percent" title="Remaining %" fmt="pct2" contentType="colorscale" scaleColor="red" min=0 max=1/>
    <Column id="discount_percent" title="Discount %" fmt="pct2" contentType="colorscale" scaleColor="green" min=0 max=1/>
    <Column id="full_url" title="Deal Link" contentType="link"/>
</DataTable>

## Deal Status Overview

```sql active_deals_count
SELECT COUNT(*) as deal_count
FROM tipster_data.deals
WHERE status = 'ACTIVE'
```

```sql expired_deals_count
SELECT COUNT(*) as deal_count
FROM tipster_data.deals
WHERE status = 'EXPIRED'
```

```sql sold_out_deals_count
SELECT COUNT(*) as deal_count
FROM tipster_data.deals
WHERE status = 'SOLD OUT'
```

<div class="grid grid-cols-3 gap-4 mb-6">
    <BigValue 
        data={active_deals_count} 
        value="deal_count" 
        title="Active Deals"
        fmt="#,##0"
    />
    <BigValue 
        data={expired_deals_count} 
        value="deal_count" 
        title="Expired Deals"
        fmt="#,##0"
    />
    <BigValue 
        data={sold_out_deals_count} 
        value="deal_count" 
        title="Sold Out Deals"
        fmt="#,##0"
    />
</div>

```sql deals_monthly
SELECT
    DATE_TRUNC('month', CAST(date_added AS DATE)) as date_added,
    COUNT(*) as deal_count,
    LAG(COUNT(*), 1) OVER (ORDER BY DATE_TRUNC('month', CAST(date_added AS DATE))) as previous_month_count,
    COUNT(*) - LAG(COUNT(*), 1) OVER (ORDER BY DATE_TRUNC('month', CAST(date_added AS DATE))) as month_over_month_diff,
    AVG(CASE
        WHEN TRY_CAST(old_price AS FLOAT) IS NOT NULL AND TRY_CAST(new_price AS FLOAT) IS NOT NULL
             AND TRY_CAST(old_price AS FLOAT) > 0
        THEN (TRY_CAST(old_price AS FLOAT) - TRY_CAST(new_price AS FLOAT)) / TRY_CAST(old_price AS FLOAT)
        ELSE NULL
    END) as avg_saving_percent,
    LAG(AVG(CASE
        WHEN TRY_CAST(old_price AS FLOAT) IS NOT NULL AND TRY_CAST(new_price AS FLOAT) IS NOT NULL
             AND TRY_CAST(old_price AS FLOAT) > 0
        THEN (TRY_CAST(old_price AS FLOAT) - TRY_CAST(new_price AS FLOAT)) / TRY_CAST(old_price AS FLOAT)
        ELSE NULL
    END), 1) OVER (ORDER BY DATE_TRUNC('month', CAST(date_added AS DATE))) as previous_month_avg_saving,
    AVG(CASE
        WHEN TRY_CAST(old_price AS FLOAT) IS NOT NULL AND TRY_CAST(new_price AS FLOAT) IS NOT NULL
             AND TRY_CAST(old_price AS FLOAT) > 0
        THEN (TRY_CAST(old_price AS FLOAT) - TRY_CAST(new_price AS FLOAT)) / TRY_CAST(old_price AS FLOAT)
        ELSE NULL
    END) - LAG(AVG(CASE
        WHEN TRY_CAST(old_price AS FLOAT) IS NOT NULL AND TRY_CAST(new_price AS FLOAT) IS NOT NULL
             AND TRY_CAST(old_price AS FLOAT) > 0
        THEN (TRY_CAST(old_price AS FLOAT) - TRY_CAST(new_price AS FLOAT)) / TRY_CAST(old_price AS FLOAT)
        ELSE NULL
    END), 1) OVER (ORDER BY DATE_TRUNC('month', CAST(date_added AS DATE))) as saving_mom_diff,
    AVG(TRY_CAST(old_price AS FLOAT)) as avg_old_price,
    LAG(AVG(TRY_CAST(old_price AS FLOAT)), 1) OVER (ORDER BY DATE_TRUNC('month', CAST(date_added AS DATE))) as previous_month_avg_old_price,
    AVG(TRY_CAST(old_price AS FLOAT)) - LAG(AVG(TRY_CAST(old_price AS FLOAT)), 1) OVER (ORDER BY DATE_TRUNC('month', CAST(date_added AS DATE))) as old_price_mom_diff,
    AVG(TRY_CAST(new_price AS FLOAT)) as avg_new_price,
    LAG(AVG(TRY_CAST(new_price AS FLOAT)), 1) OVER (ORDER BY DATE_TRUNC('month', CAST(date_added AS DATE))) as previous_month_avg_new_price,
    AVG(TRY_CAST(new_price AS FLOAT)) - LAG(AVG(TRY_CAST(new_price AS FLOAT)), 1) OVER (ORDER BY DATE_TRUNC('month', CAST(date_added AS DATE))) as new_price_mom_diff,
    SUM(CASE
        WHEN TRY_CAST(sold AS INTEGER) IS NOT NULL AND TRY_CAST(remaining AS INTEGER) IS NOT NULL
        THEN TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER)
        ELSE NULL
    END) as total_vouchers_available,
    LAG(SUM(CASE
        WHEN TRY_CAST(sold AS INTEGER) IS NOT NULL AND TRY_CAST(remaining AS INTEGER) IS NOT NULL
        THEN TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER)
        ELSE NULL
    END), 1) OVER (ORDER BY DATE_TRUNC('month', CAST(date_added AS DATE))) as previous_month_vouchers,
    SUM(CASE
        WHEN TRY_CAST(sold AS INTEGER) IS NOT NULL AND TRY_CAST(remaining AS INTEGER) IS NOT NULL
        THEN TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER)
        ELSE NULL
    END) - LAG(SUM(CASE
        WHEN TRY_CAST(sold AS INTEGER) IS NOT NULL AND TRY_CAST(remaining AS INTEGER) IS NOT NULL
        THEN TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER)
        ELSE NULL
    END), 1) OVER (ORDER BY DATE_TRUNC('month', CAST(date_added AS DATE))) as vouchers_mom_diff
FROM tipster_data.deals
WHERE date_added IS NOT NULL AND date_added != ''
GROUP BY 1
ORDER BY 1 DESC
```

## Key Metrics

<div class="grid grid-cols-5 gap-4 mb-6">
  <BigValue 
    data={deals_monthly} 
    value=deal_count
    title="Total Deals Latest Month"
    sparkline=date_added
    comparison=month_over_month_diff
    comparisonFmt=num1
    comparisonTitle="vs. Last Month"
  />
  
  <BigValue 
    data={deals_monthly} 
    value=avg_saving_percent
    title="Avg Saving Latest Month (%)"
    fmt='pct2'
    sparkline=date_added
    comparison=saving_mom_diff
    comparisonFmt='pct1'
    comparisonTitle="vs. Last Month"
  />
  
  <BigValue 
    data={deals_monthly} 
    value=avg_old_price
    title="Average Old Price"
    fmt='#,##0.00" DKK"'
    sparkline=date_added
    comparison=old_price_mom_diff
    comparisonFmt='#,##0.00" DKK"'
    comparisonTitle="vs. Last Month"
    downIsGood=true
  />
  
  <BigValue 
    data={deals_monthly} 
    value=avg_new_price
    title="Average New Price"
    fmt='#,##0.00" DKK"'
    sparkline=date_added
    comparison=new_price_mom_diff
    comparisonFmt='#,##0.00" DKK"'
    comparisonTitle="vs. Last Month"
    downIsGood=true
  />

<BigValue 
    data={deals_monthly} 
    value=total_vouchers_available
    title="Total Vouchers Available"
    fmt='#,##0'
    sparkline=date_added
    comparison=vouchers_mom_diff
    comparisonFmt='#,##0'
    comparisonTitle="vs. Last Month"
  />

</div>

<!--
```sql current_month_metrics
WITH monthly_data AS (
    SELECT
        DATE_TRUNC('month', CAST(date_added AS DATE)) as month,
        COUNT(DISTINCT deal_id) as unique_deals,
        AVG(CASE
            WHEN TRY_CAST(old_price AS FLOAT) IS NOT NULL AND TRY_CAST(new_price AS FLOAT) IS NOT NULL
                 AND TRY_CAST(old_price AS FLOAT) > 0
            THEN (TRY_CAST(old_price AS FLOAT) - TRY_CAST(new_price AS FLOAT)) / TRY_CAST(old_price AS FLOAT)
            ELSE NULL
        END) as avg_discount_percent,
        AVG(TRY_CAST(old_price AS FLOAT)) as avg_old_price,
        AVG(TRY_CAST(new_price AS FLOAT)) as avg_new_price
    FROM tipster_data.deals
    WHERE date_added IS NOT NULL AND date_added != ''
    GROUP BY DATE_TRUNC('month', CAST(date_added AS DATE))
),
latest_months AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY month DESC) as rn
    FROM monthly_data
)
SELECT
    current.unique_deals as current_unique_deals,
    previous.unique_deals as previous_unique_deals,
    current.unique_deals - previous.unique_deals as deals_delta,
    current.avg_discount_percent as current_avg_discount,
    previous.avg_discount_percent as previous_avg_discount,
    current.avg_discount_percent - previous.avg_discount_percent as discount_delta,
    current.avg_old_price as current_avg_old_price,
    previous.avg_old_price as previous_avg_old_price,
    current.avg_old_price - previous.avg_old_price as old_price_delta,
    current.avg_new_price as current_avg_new_price,
    previous.avg_new_price as previous_avg_new_price,
    current.avg_new_price - previous.avg_new_price as new_price_delta
FROM latest_months current
LEFT JOIN latest_months previous ON previous.rn = current.rn + 1
WHERE current.rn = 1
```

<div class="grid grid-cols-4 gap-4 mb-6">
    <BigValue
        data={current_month_metrics}
        value='current_unique_deals'
        title='Unique Deals Latest Month'
        delta='deals_delta'
        deltaPrecision=0
    />
    <BigValue
        data={current_month_metrics}
        value='current_avg_discount'
        title='Avg Saving Latest Month'
        fmt='pct2'
        delta='discount_delta'
        deltaPrecision=4
        deltaFmt='pct2'
    />
    <BigValue
        data={current_month_metrics}
        value='current_avg_old_price'
        title='Average Old Price'
        fmt='#,##0.00" DKK"'
        delta='old_price_delta'
        deltaPrecision=2
        downIsGood=true
    />
    <BigValue
        data={current_month_metrics}
        value='current_avg_new_price'
        title='Average New Price'
        fmt='#,##0.00" DKK"'
        delta='new_price_delta'
        deltaPrecision=2
        downIsGood=true
    />
</div> -->

## Trends Over Time

```sql monthly_trends
SELECT
    DATE_TRUNC('month', CAST(date_added AS DATE)) as month,
    COUNT(DISTINCT deal_id) as unique_deals,
    AVG(CASE
        WHEN TRY_CAST(old_price AS FLOAT) IS NOT NULL AND TRY_CAST(new_price AS FLOAT) IS NOT NULL
             AND TRY_CAST(old_price AS FLOAT) > 0
        THEN (TRY_CAST(old_price AS FLOAT) - TRY_CAST(new_price AS FLOAT)) / TRY_CAST(old_price AS FLOAT)
        ELSE NULL
    END) as avg_saving_percent
FROM tipster_data.deals
WHERE date_added IS NOT NULL AND date_added != ''
GROUP BY DATE_TRUNC('month', CAST(date_added AS DATE))
ORDER BY month
```

<LineChart 
    data={monthly_trends} 
    x=month
    y=avg_saving_percent
    y2=unique_deals
    y2SeriesType=bar
    title="Monthly Deals Volume & Average Savings"
    yAxisTitle="Average Savings (%)"
    y2AxisTitle="Number of Deals"
    yFmt=pct2
/>

## Daily Deal Activity

```sql deals_by_day
SELECT
    CAST(date_added AS DATE) as day,
    COUNT(DISTINCT deal_id) as deal_count
FROM tipster_data.deals
WHERE date_added IS NOT NULL AND date_added != ''
GROUP BY CAST(date_added AS DATE)
ORDER BY day
```

<CalendarHeatmap 
    data={deals_by_day}
    date=day
    value=deal_count
    title="Daily Deal Activity Calendar"
    subtitle="Number of new deals added each day"
/>

```sql vouchers_by_day
SELECT
    CAST(date_added AS DATE) as day,
    SUM(CASE
        WHEN TRY_CAST(sold AS INTEGER) IS NOT NULL AND TRY_CAST(remaining AS INTEGER) IS NOT NULL
        THEN TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER)
        ELSE NULL
    END) as total_vouchers
FROM tipster_data.deals
WHERE date_added IS NOT NULL AND date_added != ''
GROUP BY CAST(date_added AS DATE)
ORDER BY day
```

<CalendarHeatmap 
    data={vouchers_by_day}
    date=day
    value=total_vouchers
    title="Daily Voucher Volume Calendar"
    subtitle="Total number of vouchers available each day"
/>

## Weekly Voucher Volume & Revenue

```sql weekly_vouchers_and_revenue
SELECT
    DATE_TRUNC('week', CAST(date_added AS DATE)) as week,
    SUM(CASE
        WHEN TRY_CAST(sold AS INTEGER) IS NOT NULL AND TRY_CAST(remaining AS INTEGER) IS NOT NULL
        THEN TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER)
        ELSE NULL
    END) as total_vouchers,
    SUM(
        CASE
            WHEN TRY_CAST(sold AS INTEGER) IS NOT NULL
                 AND TRY_CAST(remaining AS INTEGER) IS NOT NULL
                 AND TRY_CAST(new_price AS FLOAT) IS NOT NULL
            THEN (TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER)) * TRY_CAST(new_price AS FLOAT)
            ELSE NULL
        END
    ) as estimated_revenue
FROM tipster_data.deals
WHERE date_added IS NOT NULL AND date_added != ''
GROUP BY DATE_TRUNC('week', CAST(date_added AS DATE))
ORDER BY week
```

<LineChart 
    data={weekly_vouchers_and_revenue}
    x=week
    y=estimated_revenue
    y2=total_vouchers
    y2SeriesType=bar
    title="Weekly Voucher Volume & Estimated Revenue"
    yAxisTitle="Estimated Revenue (DKK)"
    y2AxisTitle="Total Vouchers"
    yFmt='#,##0" DKK"'
    y2Fmt='#,##0'
/>

## Top Revenue Deals

```sql top_revenue_deals
SELECT
    deal_id,
    merchant_name,
    CASE
        WHEN TRY_CAST(sold AS INTEGER) IS NOT NULL AND TRY_CAST(remaining AS INTEGER) IS NOT NULL
        THEN TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER)
        ELSE NULL
    END AS total_vouchers,
    TRY_CAST(new_price AS FLOAT) as new_price,
    CASE
        WHEN TRY_CAST(sold AS INTEGER) IS NOT NULL
             AND TRY_CAST(remaining AS INTEGER) IS NOT NULL
             AND TRY_CAST(new_price AS FLOAT) IS NOT NULL
        THEN (TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER)) * TRY_CAST(new_price AS FLOAT)
        ELSE NULL
    END as estimated_revenue
FROM tipster_data.deals
WHERE TRY_CAST(sold AS INTEGER) IS NOT NULL
      AND TRY_CAST(remaining AS INTEGER) IS NOT NULL
      AND TRY_CAST(new_price AS FLOAT) IS NOT NULL
ORDER BY estimated_revenue DESC
LIMIT 15
```

<BarChart 
    data={top_revenue_deals}
    x='merchant_name'
    y='estimated_revenue'
    title="Top 15 Revenue-Generating Deals"
    subtitle="Deals ranked by total potential revenue (voucher count × new price)"
    yFmt='#,##0" DKK"'
    swapXY=true
/>

## Top Merchants

```sql top_merchants_by_deals
SELECT
    merchant_name,
    COUNT(DISTINCT deal_id) as deal_count
FROM tipster_data.deals
GROUP BY merchant_name
ORDER BY deal_count DESC
LIMIT 10
```

```sql merchants_by_avg_savings
SELECT
    merchant_name,
    AVG(CASE
        WHEN TRY_CAST(old_price AS FLOAT) IS NOT NULL AND TRY_CAST(new_price AS FLOAT) IS NOT NULL
             AND TRY_CAST(old_price AS FLOAT) > 0
        THEN (TRY_CAST(old_price AS FLOAT) - TRY_CAST(new_price AS FLOAT)) / TRY_CAST(old_price AS FLOAT)
        ELSE NULL
    END) as avg_discount
FROM tipster_data.deals
GROUP BY merchant_name
HAVING COUNT(DISTINCT deal_id) >= 2  -- Only merchants with at least 2 deals
   AND AVG(CASE
        WHEN TRY_CAST(old_price AS FLOAT) IS NOT NULL AND TRY_CAST(new_price AS FLOAT) IS NOT NULL
             AND TRY_CAST(old_price AS FLOAT) > 0
        THEN (TRY_CAST(old_price AS FLOAT) - TRY_CAST(new_price AS FLOAT)) / TRY_CAST(old_price AS FLOAT)
        ELSE NULL
    END) IS NOT NULL
ORDER BY avg_discount DESC
LIMIT 10
```

<div class="grid grid-cols-2 gap-6 mb-6">
<BarChart 
    data={top_merchants_by_deals} 
    x='merchant_name' 
    y='deal_count'
    title="Top Merchants by Number of Deals"
    swapXY=true
/>

<BarChart 
    data={merchants_by_avg_savings} 
    x='merchant_name' 
    y='avg_discount'
    title="Merchants with Highest Average Savings"
    yFmt='pct2'
    swapXY=true
/>

</div>

## All Deals Data

```sql all_deals
SELECT * FROM tipster_data.deals
ORDER BY date_added DESC
```

<DataTable data={all_deals} rows=10 rowShading=true>
    <Column id="deal_id" title="Deal ID"/>
    <Column id="full_url" title="Deal Link" contentType="link" openInNewTab=true linkLabel="View Deal ↗"/>
    <Column id="status" title="Status"/>
    <Column id="merchant_name" title="Merchant"/>
    <Column id="deal_description" title="Description" wrap=true/>
    <Column id="sold" title="Sold"/>
    <Column id="remaining" title="Remaining"/>
    <Column id="total_available" title="Total Available"/>
    <Column id="remaining_percent" title="Remaining %" fmt="pct2"/>
    <Column id="old_price" title="Old Price"/>
    <Column id="old_currency" title="Old Currency"/>
    <Column id="new_price" title="New Price"/>
    <Column id="new_currency" title="New Currency"/>
    <Column id="discount_absolute" title="Discount Amount"/>
    <Column id="discount_percent" title="Discount %" fmt="pct2"/>
    <Column id="date_added" title="Date Added"/>
    <Column id="location" title="Location"/>
    <Column id="hours" title="Hours"/>
    <Column id="inserted_at" title="Inserted At"/>
</DataTable>
