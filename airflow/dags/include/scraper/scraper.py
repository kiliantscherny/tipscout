import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import hashlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TipsterScraper:
    base_url = "https://www.tipster.io"

    def __init__(self, main_url):
        self.main_url = main_url
        self.tipsterdeals = []
        logging.info(f"Initialized TipsterScraper with main URL: {self.main_url}")

    def _fetch_main_page(self) -> BeautifulSoup:
        logging.info("Fetching the main page content")
        response = requests.get(self.main_url)
        soup = BeautifulSoup(response.text, "html.parser")
        logging.info("Fetched and parsed the main page content")
        return soup

    def _extract_urls(self, soup) -> list:
        logging.info("Extracting URLs from the main page")
        links = soup.find_all("a", href=True)
        pattern = re.compile(r"^/team/(?!31361)\d+\.html$")
        urls = [link["href"] for link in links if pattern.match(link["href"])]
        logging.info(f"Extracted {len(urls)} URLs from the main page")
        return urls

    def _extract_deal_id(self, url) -> str:
        logging.info(f"Extracting deal ID from URL: {url}")
        match = re.search(r"/team/(\d+)\.html$", url)
        if match:
            deal_id = match.group(1)
            logging.info(f"Extracted deal ID: {deal_id}")
            return deal_id
        logging.warning(f"Failed to extract deal ID from URL: {url}")
        return None

    def _extract_date_from_deal_url(self, url) -> str:
        logging.info(f"Extracting date from deal URL: {url}")
        match = re.search(r"(\d{4})/(\d{4})", url)
        if match:
            year = match.group(1)
            month_day = match.group(2)
            date = f"{year}-{month_day[:2]}-{month_day[2:]}"  # Format: YYYY-MM-DD
            logging.info(f"Extracted date: {date}")
            return date
        logging.warning(f"Failed to extract date from URL: {url}")
        return None

    def _get_status_sold_remaining(self, page_soup) -> tuple:
        logging.info("Extracting status, sold, and remaining information")
        status = "ACTIVE"  # Default status is "ACTIVE"
        deal_status_div = page_soup.find("div", id="dealbuttonclosed")
        if deal_status_div:
            status = "SOLD OUT" if "SOLD OUT" in deal_status_div.text else "EXPIRED"
        sold = (
            page_soup.find("div", id="nowsold").text.strip().split()[0]
            if page_soup.find("div", id="nowsold")
            else None
        )
        remaining = (
            page_soup.find("div", id="nowleft").text.strip().split()[0]
            if page_soup.find("div", id="nowleft")
            else None
        )
        logging.info(f"Status: {status}, Sold: {sold}, Remaining: {remaining}")
        return status, sold, remaining

    def _get_price_info(self, page_soup) -> tuple:
        logging.info("Extracting price information")
        old_price = (
            page_soup.find("span", id="dealpriceold").text.strip()
            if page_soup.find("span", id="dealpriceold")
            else None
        )
        old_currency = (
            page_soup.find("span", class_="money old").text.strip()
            if page_soup.find("span", class_="money old")
            else None
        )
        new_price = (
            page_soup.find("span", id="deal-buy-total-t").text.strip()
            if page_soup.find("span", id="deal-buy-total-t")
            else None
        )
        new_currency = (
            page_soup.find("span", class_="money").text.strip()
            if page_soup.find("span", class_="money")
            else None
        )
        merchant_name = (
            page_soup.find("div", id="teamtoppartner").text.strip()
            if page_soup.find("div", id="teamtoppartner")
            else None
        )
        logging.info(
            f"Merchant: {merchant_name}, Old Price: {old_price} {old_currency}, New Price: {new_price} {new_currency}"
        )
        return merchant_name, old_price, old_currency, new_price, new_currency

    def _get_location_info(self, page_soup) -> str:
        logging.info("Extracting location information")
        where_section = page_soup.find("span", text="+ WHERE")
        locations = []
        if where_section:
            where_content = where_section.find_next("div", class_="accordion__content")
            if where_content and where_content.p:
                raw_html = where_content.p.decode_contents()
                clean_text = re.sub(
                    r"<br/> ", ", ", raw_html
                )  # Replace single <br/> with a comma
                clean_text = re.sub(
                    r"<br/><br/>", "', '", clean_text
                )  # Replace double <br/> with ', '
                clean_text = clean_text.replace("<br>", "")  # Remove any remaining <br>
                raw_locations = clean_text.split("', '")
                locations = [f"'{loc.strip()}'" for loc in raw_locations if loc.strip()]
        location_str = ", ".join(locations)
        logging.info(f"Extracted locations: {location_str}")
        return location_str

    def _get_hours_info(self, page_soup) -> str:
        logging.info("Extracting hours information")
        hours_section = page_soup.find("span", text="+ HOURS")
        hours = "No Hours Found"
        if hours_section:
            hours_content = hours_section.find_next("div", class_="accordion__content")
            if hours_content and hours_content.p:
                hours = hours_content.p.text.strip()
        logging.info(f"Extracted hours: {hours}")
        return hours

    def _retrieve_deal_info(self, url) -> dict:
        logging.info(f"Retrieving deal information from URL: {url}")
        full_url = self.base_url + url
        page_response = requests.get(full_url)
        page_soup = BeautifulSoup(page_response.text, "html.parser")

        deal_description = (
            page_soup.find("h1").text.strip() if page_soup.find("h1") else None
        )
        deal_id = self._extract_deal_id(url)
        date_added = (
            self._extract_date_from_deal_url(
                page_soup.find("meta", property="og:image")["content"]
            )
            if page_soup.find("meta", property="og:image")
            else None
        )
        location = self._get_location_info(page_soup)
        hours = self._get_hours_info(page_soup)
        status, sold, remaining = self._get_status_sold_remaining(page_soup)
        merchant_name, old_price, old_currency, new_price, new_currency = (
            self._get_price_info(page_soup)
        )
        inserted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        surrogate_key = hashlib.md5(f"{url}{inserted_at}".encode()).hexdigest()

        deal_info = {
            "surrogate_key": surrogate_key,
            "deal_id": deal_id,
            "full_url": full_url,
            "status": status,
            "sold": sold,
            "remaining": remaining,
            "deal_description": deal_description,
            "date_added": date_added,
            "location": location,
            "hours": hours,
            "merchant_name": merchant_name,
            "old_price": old_price,
            "old_currency": old_currency,
            "new_price": new_price,
            "new_currency": new_currency,
            "inserted_at": inserted_at,
        }
        logging.info(f"Retrieved deal information: {deal_info}")
        return deal_info

    def scrape(self) -> pd.DataFrame:
        logging.info("Starting the scraping process")
        main_page_soup = self._fetch_main_page()
        filtered_urls = self._extract_urls(main_page_soup)
        total_urls = len(filtered_urls)
        logging.info(f"Total URLs to process: {total_urls}")

        for index, url in enumerate(filtered_urls, start=1):
            logging.info(f"\nProcessing URL {index}/{total_urls}: {url}\n")
            deal_info = self._retrieve_deal_info(url)
            self.tipsterdeals.append(deal_info)

        logging.info("Scraping process completed")
        return pd.DataFrame(self.tipsterdeals)
