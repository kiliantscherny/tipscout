from airflow.decorators import dag, task
from datetime import datetime
import pandas as pd
from include.scraper.scraper import TipsterScraper
from include.database.database import DuckDBHandler
import logging
import pendulum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info("Starting the data scraping task.")
        db_handler = DuckDBHandler("/opt/airflow/data/tipsterdeals.duckdb")
        scraper = TipsterScraper(
            main_url="https://www.tipster.io/campaigns", db_handler=db_handler
        )
        deals_df = scraper.scrape()
        logger.info("Data scraping task completed successfully.")
        logger.debug(f"Scraped data: {deals_df.head()}")
        return deals_df

    # Database Insertion Task
    @task()
    def store_data(deals_df: pd.DataFrame):
        logger.info("Starting the data storage task.")
        db_handler = DuckDBHandler("/opt/airflow/data/tipsterdeals.duckdb")
        if not db_handler.table_exists("tipsterdeals"):
            logger.info("Table 'tipsterdeals' does not exist. Creating table.")
            db_handler.create_table()
        else:
            logger.info("Table 'tipsterdeals' already exists.")
        db_handler.insert_data(deals_df)
        logger.info("Data inserted into 'tipsterdeals' table successfully.")
        db_handler.close()
        logger.info("Data storage task completed successfully.")

    # Workflow: scrape -> store
    deals_df = scrape_data()
    store_data(deals_df)


tipster_scraper_dag = tipster_scraper_dag()
