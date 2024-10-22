from airflow.decorators import dag, task
from datetime import datetime
import pandas as pd
from include.scraper.scraper import TipsterScraper
from include.database.database import DuckDBHandler
import logging
import pendulum

local_tz = pendulum.timezone("Europe/Copenhagen")

# Default arguments for the DAG
default_args = {
    "owner": "user",
    "start_date": datetime(2023, 1, 1, tzinfo=local_tz),
    "retries": 1,
}


# Define the DAG using the TaskFlow API
# Set the interval to be at 5 past the hour every 3 hours, starting at 1AM Copenhagen time
# Deals are added at 7:01AM, so checking just after then is best and then every few hours as well
@dag(
    default_args=default_args,
    schedule_interval="5 1,4,7,10,13,16,19,22 * * *",
    catchup=False,
)
def tipster_scraper_dag():

    # Scraping Task
    @task()
    def scrape_data() -> pd.DataFrame:
        scraper = TipsterScraper(main_url="https://www.tipster.io/campaigns")
        logging.info("Scraping data from: %s", scraper.main_url)
        return scraper.scrape()

    # Database Insertion Task
    @task()
    def store_data(deals_df: pd.DataFrame):
        db_path = "/opt/airflow/data/tipsterdeals.duckdb"

        # Log database path for debugging
        logging.info("Database path: %s", db_path)

        db_handler = DuckDBHandler(db_path)

        if not db_handler.table_exists("tipsterdeals"):
            logging.info("Table tipsterdeals does not exist. Creating table.")
            db_handler.create_table()

        logging.info("Inserting data into table tipsterdeals.")
        db_handler.insert_data(deals_df)

        logging.info("Closing database connection.")
        db_handler.close()

    # Workflow: scrape -> store
    deals_df = scrape_data()
    store_data(deals_df)


# Instantiate the DAG
tipster_scraper_dag = tipster_scraper_dag()
