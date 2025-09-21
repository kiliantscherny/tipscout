# tipscout Statistics

## Deal Status Overview

```sql deal_status_counts
SELECT
    status,
    COUNT(*) as deal_count
FROM tipster_data.deals
GROUP BY status
ORDER BY deal_count DESC
```

<div class="grid grid-cols-3 gap-4 mb-6">
    <BigValue 
        data={deal_status_counts} 
        value='deal_count' 
        title='Active Deals'
        where="status = 'ACTIVE'"
    />
    <BigValue 
        data={deal_status_counts} 
        value='deal_count' 
        title='Expired Deals'
        where="status = 'EXPIRED'"
    />
    <BigValue 
        data={deal_status_counts} 
        value='deal_count' 
        title='Sold Out Deals'
        where="status = 'SOLD OUT'"
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
    AVG(TRY_CAST(new_price AS FLOAT)) - LAG(AVG(TRY_CAST(new_price AS FLOAT)), 1) OVER (ORDER BY DATE_TRUNC('month', CAST(date_added AS DATE))) as new_price_mom_diff
FROM tipster_data.deals
WHERE date_added IS NOT NULL AND date_added != ''
GROUP BY 1
ORDER BY 1 DESC
```

## Key Metrics

<div class="grid grid-cols-4 gap-4 mb-6">
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

<DataTable data={active_deals}>
    <Column id='deal_id' title='Deal ID'/>
    <Column id='merchant_name' title='Merchant Name'/>
    <Column id='total_available' title='Total Available'/>
    <Column id='sold' title='Sold'/>
    <Column id='remaining' title='Remaining'/>
    <Column id='remaining_percent' title='Remaining %' fmt='pct2' 
        contentType='colorscale' 
        scaleColor='red' 
        min=0 max=1/>
    <Column id='discount_percent' title='Discount %' fmt='pct2' 
        contentType='colorscale' 
        scaleColor='green' 
        min=0 max=1/>
    <Column id='full_url' title='Deal Link' contentType='link'/>
</DataTable>

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

## Deal Status Distribution

```sql status_distribution
SELECT
    status,
    COUNT(*) as deal_count
FROM tipster_data.deals
GROUP BY status
ORDER BY deal_count DESC
```

<BarChart 
    data={status_distribution} 
    x='status' 
    y='deal_count'
    title="Current Status of Deals"
/>

## All Deals Data

```sql all_deals
SELECT * FROM tipster_data.deals
ORDER BY inserted_at DESC
```

<DataTable data={all_deals} rows=20/>
