import duckdb


class DuckDBHandler:
    def __init__(self, db_path):
        self.conn = duckdb.connect(db_path)

    def table_exists(self, table_name):
        query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}';"
        return self.conn.execute(query).fetchone()[0] > 0

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
        );
        """
        self.conn.execute(create_table_query)

    def insert_data(self, df):
        insert_query = """
        INSERT INTO tipsterdeals (surrogate_key, deal_id, full_url, status, sold, remaining, deal_description, date_added, location, hours, merchant_name, old_price, old_currency, new_price, new_currency, inserted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        for _, row in df.iterrows():
            self.conn.execute(insert_query, tuple(row))

    def close(self):
        self.conn.close()
