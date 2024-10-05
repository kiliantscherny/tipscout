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
        self.deals = []

    def fetch_main_page(self):
        response = requests.get(self.main_url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def extract_urls(self, soup):
        links = soup.find_all("a", href=True)
        pattern = re.compile(r"^/team/(?!31361)\d+\.html$")
        return [link["href"] for link in links if pattern.match(link["href"])]

    def extract_date_from_url(self, url):
        match = re.search(r"(\d{4})/(\d{4})", url)
        if match:
            year = match.group(1)
            month_day = match.group(2)
            return f"{year}-{month_day[:2]}-{month_day[2:]}"  # Format: YYYY-MM-DD
        return None

    def check_deal_info(self, url):
        full_url = self.base_url + url
        page_response = requests.get(full_url)
        page_soup = BeautifulSoup(page_response.text, "html.parser")

        # Extract necessary details
        deal_name = (
            page_soup.find("h1").text.strip() if page_soup.find("h1") else "No Name"
        )
        date_added = (
            self.extract_date_from_url(
                page_soup.find("meta", property="og:image")["content"]
            )
            if page_soup.find("meta", property="og:image")
            else "No Date"
        )
        location = (
            page_soup.find("div", class_="accordion__content").p.text.strip()
            if page_soup.find("div", class_="accordion__content")
            and page_soup.find("div", class_="accordion__content").p
            else "No Location"
        )
        status, sold, left = self._get_status_sold_left(page_soup)
        merchant_name, old_price, old_currency, new_price, new_currency = (
            self._get_price_info(page_soup)
        )

        inserted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        surrogate_key = hashlib.md5(f"{url}{inserted_at}".encode()).hexdigest()

        return {
            "surrogate_key": surrogate_key,
            "url": url,
            "status": status,
            "sold": sold,
            "left": left,
            "deal_name": deal_name,
            "date_added": date_added,
            "location": location,
            "merchant_name": merchant_name,
            "old_price": old_price,
            "old_currency": old_currency,
            "new_price": new_price,
            "new_currency": new_currency,
            "inserted_at": inserted_at,
        }

    def _get_status_sold_left(self, page_soup):
        status = "AVAILABLE"
        sold = (
            page_soup.find("div", id="nowsold").text.strip()
            if page_soup.find("div", id="nowsold")
            else "Unknown"
        )
        left = (
            page_soup.find("div", id="nowleft").text.strip()
            if page_soup.find("div", id="nowleft")
            else "Unknown"
        )
        deal_status_div = page_soup.find("div", id="dealbuttonclosed")
        if deal_status_div:
            status = "SOLD OUT" if "SOLD OUT" in deal_status_div.text else "EXPIRED"
        return status, sold, left

    def _get_price_info(self, page_soup):
        old_price = (
            page_soup.find("span", id="dealpriceold").text.strip()
            if page_soup.find("span", id="dealpriceold")
            else "No Old Price"
        )
        old_currency = (
            page_soup.find("span", class_="money old").text.strip()
            if page_soup.find("span", class_="money old")
            else "No Currency"
        )
        new_price = (
            page_soup.find("span", id="deal-buy-total-t").text.strip()
            if page_soup.find("span", id="deal-buy-total-t")
            else "No New Price"
        )
        new_currency = (
            page_soup.find("span", class_="money").text.strip()
            if page_soup.find("span", class_="money")
            else "No Currency"
        )
        merchant_name = (
            page_soup.find("div", id="teamtoppartner").text.strip()
            if page_soup.find("div", id="teamtoppartner")
            else "No Merchant"
        )
        return merchant_name, old_price, old_currency, new_price, new_currency

    def scrape(self):
        main_page_soup = self.fetch_main_page()
        filtered_urls = self.extract_urls(main_page_soup)
        for url in filtered_urls:
            deal_info = self.check_deal_info(url)
            self.deals.append(deal_info)
        return pd.DataFrame(self.deals)
