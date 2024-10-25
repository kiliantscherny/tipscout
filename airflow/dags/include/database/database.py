import duckdb
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DuckDBHandler:
    def __init__(self, db_path):
        self.conn = duckdb.connect(db_path)
        logging.info("DuckDBHandler initialized successfully.")

    def table_exists(self, table_name):
        query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}';"
        result = self.conn.execute(query).fetchone()[0] > 0
        return result

    def create_table(self):
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
        )
        """
        self.conn.execute(create_table_query)
        logging.info("Table 'tipsterdeals' created successfully.")

    def insert_data(self, df):
        self.conn.execute("INSERT INTO tipsterdeals SELECT * FROM df")
        logging.info("Data inserted successfully.")

    def close(self):
        self.conn.close()
        logging.info("DuckDB connection closed successfully.")
