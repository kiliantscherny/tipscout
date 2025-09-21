from scraper import TipsterScraper
from database import DuckDBHandler
import logging


def main():
    """Scrape tipster data and store it in DuckDB database."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Configuration
    main_url = "https://www.tipster.io/drops"
    db_path = "sources/tipster_data/tipsterdeals.duckdb"

    # Scrape data
    logging.info("Starting tipster data scraping...")
    scraper = TipsterScraper(main_url=main_url)
    deals_df = scraper.scrape()

    # Store data
    if deals_df.empty:
        logging.warning("No deals found to store. Skipping database operations.")
    else:
        logging.info(f"Storing {len(deals_df)} deals in DuckDB...")
        db_handler = DuckDBHandler(db_path)

        if not db_handler.table_exists("tipsterdeals"):
            logging.info("Table tipsterdeals does not exist. Creating table.")
            db_handler.create_table()

        logging.info("Inserting data into table tipsterdeals.")
        db_handler.insert_data(deals_df)

        logging.info("Closing database connection.")
        db_handler.close()

    logging.info("Data scraping and storage completed successfully!")


if __name__ == "__main__":
    main()
