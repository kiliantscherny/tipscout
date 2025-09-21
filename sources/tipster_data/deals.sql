SELECT
    surrogate_key,
    deal_id,
    full_url,
    status,
    sold,
    remaining,
    deal_description,
    date_added,
    location,
    hours,
    merchant_name,
    old_price,
    old_currency,
    new_price,
    new_currency,
    inserted_at,
    -- Handle non-numeric values in sold/remaining columns
    CASE 
        WHEN TRY_CAST(sold AS INTEGER) IS NOT NULL AND TRY_CAST(remaining AS INTEGER) IS NOT NULL 
        THEN TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER)
        ELSE NULL
    END AS total_available,
    
    CASE 
        WHEN TRY_CAST(sold AS INTEGER) IS NOT NULL AND TRY_CAST(remaining AS INTEGER) IS NOT NULL 
             AND (TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER)) > 0 
        THEN CAST(TRY_CAST(remaining AS INTEGER) AS FLOAT) / (TRY_CAST(sold AS INTEGER) + TRY_CAST(remaining AS INTEGER))
        ELSE NULL
    END AS remaining_percent,
    
    -- Handle non-numeric values in price columns
    CASE 
        WHEN TRY_CAST(old_price AS FLOAT) IS NOT NULL AND TRY_CAST(new_price AS FLOAT) IS NOT NULL 
        THEN TRY_CAST(old_price AS FLOAT) - TRY_CAST(new_price AS FLOAT)
        ELSE NULL
    END AS discount_absolute,
    
    CASE 
        WHEN TRY_CAST(old_price AS FLOAT) IS NOT NULL AND TRY_CAST(new_price AS FLOAT) IS NOT NULL 
             AND TRY_CAST(old_price AS FLOAT) > 0 
        THEN (TRY_CAST(old_price AS FLOAT) - TRY_CAST(new_price AS FLOAT)) / TRY_CAST(old_price AS FLOAT)
        ELSE NULL
    END AS discount_percent
FROM 
    tipsterdeals
QUALIFY ROW_NUMBER() OVER (PARTITION BY deal_id ORDER BY inserted_at DESC) = 1