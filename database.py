import duckdb
import pandas as pd

# Load the CSV file into a DataFrame
deals_df = pd.read_csv("deals.csv")

# Connect to DuckDB
conn = duckdb.connect("deals.db")

# Check if the table exists
table_exists_query = (
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'deals';"
)
table_exists = (
    conn.execute(table_exists_query).fetchone()[0] > 0
)  # Check if the count is greater than 0
print(table_exists)

if not table_exists:
    # Create the table if it doesn't exist
    create_table_query = """
    CREATE TABLE deals (
        surrogate_key VARCHAR PRIMARY KEY,
        url VARCHAR,
        status VARCHAR,
        sold VARCHAR,
        "left" VARCHAR,
        deal_name VARCHAR,
        date_added DATE,
        location VARCHAR,
        merchant_name VARCHAR,
        old_price VARCHAR,
        old_currency VARCHAR,
        new_price VARCHAR,
        new_currency VARCHAR,
        inserted_at TIMESTAMP
    );
    """
    print("Table 'deals' does not exist. Creating the table...")
    conn.execute(create_table_query)

# Insert data into the table using DuckDB SQL
insert_query = """
INSERT INTO deals (surrogate_key, url, status, sold, "left", deal_name, date_added, location, merchant_name, old_price, old_currency, new_price, new_currency, inserted_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

# Iterate through the DataFrame and execute insertions
for index, row in deals_df.iterrows():
    conn.execute(
        insert_query,
        (
            row["surrogate_key"],
            row["url"],
            row["status"],
            row["sold"],
            row["left"],
            row["deal_name"],
            row["date_added"],
            row["location"],
            row["merchant_name"],
            row["old_price"],
            row["old_currency"],
            row["new_price"],
            row["new_currency"],
            row["inserted_at"],
        ),
    )

rows = conn.execute("SELECT * FROM deals;").fetchall()


# Commit and close the connection
conn.commit()
conn.close()

print("Data has been appended to the DuckDB table successfully.")
