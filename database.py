import duckdb
import pandas as pd
import logging
import os


class DuckDBHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        logging.info(f"Initialized DuckDBHandler with database path: {self.db_path}")

    def connect(self):
        if self.connection is None:
            self.connection = duckdb.connect(self.db_path)
            logging.info(f"Connected to DuckDB database at {self.db_path}")
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            logging.info("Closed DuckDB connection")

    def table_exists(self, table_name: str) -> bool:
        conn = self.connect()
        try:
            result = conn.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?",
                [table_name]
            ).fetchone()
            exists = result[0] > 0
            logging.info(f"Table '{table_name}' exists: {exists}")
            return exists
        except Exception as e:
            logging.error(f"Error checking if table exists: {e}")
            return False

    def create_table(self):
        conn = self.connect()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tipsterdeals (
                    surrogate_key VARCHAR PRIMARY KEY,
                    deal_id VARCHAR,
                    full_url VARCHAR,
                    status VARCHAR,
                    sold VARCHAR,
                    remaining VARCHAR,
                    deal_description VARCHAR,
                    date_added VARCHAR,
                    location VARCHAR,
                    hours VARCHAR,
                    merchant_name VARCHAR,
                    old_price VARCHAR,
                    old_currency VARCHAR,
                    new_price VARCHAR,
                    new_currency VARCHAR,
                    inserted_at TIMESTAMP
                )
            """)
            logging.info("Created tipsterdeals table")
        except Exception as e:
            logging.error(f"Error creating table: {e}")
            raise

    def insert_data(self, df: pd.DataFrame):
        conn = self.connect()
        try:
            # Register the DataFrame with DuckDB
            conn.register("temp_df", df)

            # Get count before insert
            count_before = conn.execute("SELECT COUNT(*) FROM tipsterdeals").fetchone()[0]

            # Insert data using ON CONFLICT to handle duplicates
            conn.execute("""
                INSERT INTO tipsterdeals
                SELECT * FROM temp_df
                ON CONFLICT (surrogate_key) DO NOTHING
            """)

            # Get count after insert
            count_after = conn.execute("SELECT COUNT(*) FROM tipsterdeals").fetchone()[0]
            rows_inserted = count_after - count_before

            logging.info(f"Inserted {rows_inserted} new rows into tipsterdeals table")

        except Exception as e:
            logging.error(f"Error inserting data: {e}")
            raise