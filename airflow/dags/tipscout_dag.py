from airflow.decorators import dag, task
from datetime import datetime
import pandas as pd
from include.scraper.scraper import TipsterScraper
from include.database.database import DuckDBHandler

# Default arguments for the DAG
default_args = {
    "owner": "user",
    "start_date": datetime(2023, 1, 1),
    "retries": 1,
}


# Define the DAG using the TaskFlow API
@dag(default_args=default_args, schedule_interval="@daily", catchup=False)
def tipster_scraper_dag():

    # Scraping Task
    @task()
    def scrape_data() -> pd.DataFrame:
        scraper = TipsterScraper(main_url="https://www.tipster.io/team")
        return scraper.scrape()

    # Database Insertion Task
    @task()
    def store_data(deals_df: pd.DataFrame):
        db_handler = DuckDBHandler("/opt/airflow/data/deals.duckdb")
        if not db_handler.table_exists("deals"):
            db_handler.create_table()
        db_handler.insert_data(deals_df)
        db_handler.close()

    # Workflow: scrape -> store
    deals_df = scrape_data()
    store_data(deals_df)


# Instantiate the DAG
tipster_scraper_dag = tipster_scraper_dag()
