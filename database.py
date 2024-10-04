import duckdb
import pandas as pd

# Load the CSV file into a DataFrame
deals_df = pd.read_csv("deals.csv")

# Connect to DuckDB (this will create the database file if it doesn't exist)
conn = duckdb.connect("deals.db")

# Create a new table or append to it if it already exists
create_table_query = """
CREATE TABLE IF NOT EXISTS deals (
    PRIMARY KEY (surrogate_key),
    surrogate_key VARCHAR,
    url VARCHAR,
    status VARCHAR,
    sold VARCHAR,
    "left" VARCHAR,  -- Use double quotes to avoid syntax error
    deal_name VARCHAR,
    date_added DATE,
    location VARCHAR,
    merchant_name VARCHAR,
    old_price VARCHAR,
    old_currency VARCHAR,
    new_price VARCHAR,
    new_currency VARCHAR,
    inserted_at TIMESTAMP,
);
"""

# Execute the create table query
conn.execute(create_table_query)

# Insert data into the table
# Use if_exists='append' to add new records
deals_df.to_sql("deals", conn, if_exists="append", index=False)

# Commit and close the connection
conn.commit()
conn.close()

print("Data has been appended to the DuckDB table successfully.")
