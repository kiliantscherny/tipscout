import duckdb
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DuckDBHandler:
    def __init__(self, db_path):
        self.conn = None
        try:
            self.conn = duckdb.connect(db_path)
            logger.info(f"Connected to database at {db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database at {db_path}: {e}")

    def table_exists(self, table_name):
        try:
            query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}';"
            result = self.conn.execute(query).fetchone()[0] > 0
            logger.info(f"Checked if table {table_name} exists: {result}")
            return result
        except Exception as e:
            logger.error(f"Error checking if table {table_name} exists: {e}")
            return False

    def create_table(self):
        try:
            create_table_query = """
            CREATE TABLE tipsterdeals (
                surrogate_key VARCHAR PRIMARY KEY,
                deal_id VARCHAR,
                full_url VARCHAR,
                status VARCHAR,
                sold INTEGER,
                remaining INTEGER,
                deal_description VARCHAR,
                date_added DATE,
                location VARCHAR,
                hours VARCHAR,
                merchant_name VARCHAR,
                old_price DOUBLE,
                old_currency VARCHAR,
                new_price DOUBLE,
                new_currency VARCHAR,
                inserted_at TIMESTAMP
            );
            """
            self.conn.execute(create_table_query)
            logger.info("Created table tipsterdeals")
        except Exception as e:
            logger.error(f"Error creating table tipsterdeals: {e}")

    def insert_data(self, df):
        try:
            insert_query = """
            INSERT INTO tipsterdeals (surrogate_key, deal_id, full_url, status, sold, remaining, deal_description, date_added, location, hours, merchant_name, old_price, old_currency, new_price, new_currency, inserted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            for _, row in df.iterrows():
                self.conn.execute(insert_query, tuple(row))
            logger.info("Inserted data into table tipsterdeals")
        except Exception as e:
            logger.error(f"Error inserting data into table tipsterdeals: {e}")

    def close(self):
        try:
            if self.conn:
                self.conn.close()
                logger.info("Closed database connection")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
