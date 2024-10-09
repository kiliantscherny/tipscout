import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import hashlib


class TipsterScraper:
    base_url = "https://www.tipster.io"

    def __init__(self, main_url):
        self.main_url = main_url
        self.tipsterdeals = []

    def _fetch_main_page(self) -> BeautifulSoup:
        """Fetch the content of the main page of the website

        :return: BeautifulSoup object of the main page
        """
        response = requests.get(self.main_url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def _extract_urls(self, soup) -> list:
        """Extract the URLs of all the current deals from the main page.
        Note: this excludes URL with team ID 31361, which is the Gift Card.

        :param soup: BeautifulSoup object of the main page
        :return: List of URLs of the current deals
        """
        links = soup.find_all("a", href=True)
        pattern = re.compile(r"^/team/(?!31361)\d+\.html$")
        return [link["href"] for link in links if pattern.match(link["href"])]

    def _extract_deal_id(self, url) -> str:
        """Extract the deal ID from the deal's URL

        :param url: URL of the deal
        :return: String of the deal ID
        """
        match = re.search(r"/team/(\d+)\.html$", url)
        if match:
            deal_id = match.group(1)
            return deal_id
        return None

    def _extract_date_from_deal_url(self, url) -> str:
        """Extract the date from the deal's URL

        :param url: URL of the deal
        :return: String of the date the deal was added, in the format YYYY-MM-DD, extracted from the image URL
        """
        match = re.search(r"(\d{4})/(\d{4})", url)
        if match:
            year = match.group(1)
            month_day = match.group(2)
            return f"{year}-{month_day[:2]}-{month_day[2:]}"  # Format: YYYY-MM-DD
        return None

    def _get_status_sold_remaining(self, page_soup) -> tuple:
        """Extract the status, sold, and remaining information of the deal

        :param page_soup: BeautifulSoup object of the deal's page
        :return: Tuple containing the status, sold, and remaining information of the deal
        """
        status = "AVAILABLE"  # Default status is "AVAILABLE"
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
        return status, sold, remaining

    def _get_price_info(self, page_soup) -> tuple:
        """Extract the price information of the deal

        :param page_soup: BeautifulSoup object of the deal's page
        :return: Tuple containing the merchant name, old price, old currency, new price, and new currency
        """
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
        return merchant_name, old_price, old_currency, new_price, new_currency

    def _get_location_info(self, page_soup) -> str:
        """Extract the location information of the deal as a string.

        :param page_soup: BeautifulSoup object of the deal's page
        :return: Comma-separated, quote-encased string of locations
        """
        # Find the accordion item for "WHERE"
        where_section = page_soup.find("span", text="+ WHERE")
        locations = []
        if where_section:
            where_content = where_section.find_next("div", class_="accordion__content")
            if where_content and where_content.p:
                # Get the raw HTML text
                raw_html = where_content.p.decode_contents()
                # Use regex to clean up the HTML
                clean_text = re.sub(
                    r"<br/> ", ", ", raw_html
                )  # Replace single <br/> with a comma
                clean_text = re.sub(
                    r"<br/><br/>", "', '", clean_text
                )  # Replace double <br/> with ', '
                clean_text = clean_text.replace("<br>", "")  # Remove any remaining <br>
                # Remove HTML tags and split by comma
                raw_locations = clean_text.split("', '")
                # Strip whitespace and format each address
                locations = [f"'{loc.strip()}'" for loc in raw_locations if loc.strip()]

        # Create a comma-separated string of locations
        return ", ".join(locations)

    def _get_hours_info(self, page_soup) -> str:
        """Extract the hours information of the deal

        :param page_soup: BeautifulSoup object of the deal's page
        :return: String of the hours of the deal
        """
        # Find the accordion item for "HOURS"
        hours_section = page_soup.find("span", text="+ HOURS")
        hours = "No Hours Found"
        if hours_section:
            hours_content = hours_section.find_next("div", class_="accordion__content")
            if hours_content and hours_content.p:
                hours = hours_content.p.text.strip()
        return hours

    def _retrieve_deal_info(self, url) -> dict:
        """Retrieves all of the details of a deal from its URL

        :param url: URL of the deal
        :return: Dictionary containing the details of the deal
        """
        full_url = self.base_url + url
        page_response = requests.get(full_url)
        page_soup = BeautifulSoup(page_response.text, "html.parser")

        # Extract necessary details
        # Get the deal's name
        deal_description = (
            page_soup.find("h1").text.strip() if page_soup.find("h1") else None
        )
        deal_id = self._extract_deal_id(url)
        # Get the date the deal was added
        date_added = (
            self._extract_date_from_deal_url(
                page_soup.find("meta", property="og:image")["content"]
            )
            if page_soup.find("meta", property="og:image")
            else None
        )
        # Get the location of the deal
        location = self._get_location_info(page_soup)
        # Get the hours of the deal
        hours = self._get_hours_info(page_soup)
        # Get the status, sold, and remaining information of the deal
        status, sold, remaining = self._get_status_sold_remaining(page_soup)
        # Get the price information of the deal
        merchant_name, old_price, old_currency, new_price, new_currency = (
            self._get_price_info(page_soup)
        )
        # Get the current timestamp to indicate when the deal was scraped
        inserted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Generate a surrogate key for the deal
        surrogate_key = hashlib.md5(f"{url}{inserted_at}".encode()).hexdigest()

        return {
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

    def scrape(self) -> pd.DataFrame:
        """Scrape the website for all the current deals and return them in a DataFrame

        :return: DataFrame containing all the current deals
        """
        main_page_soup = self._fetch_main_page()
        filtered_urls = self._extract_urls(main_page_soup)
        for url in filtered_urls:
            deal_info = self._retrieve_deal_info(url)
            self.tipsterdeals.append(deal_info)
        return pd.DataFrame(self.tipsterdeals)
