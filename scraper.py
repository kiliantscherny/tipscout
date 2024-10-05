import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import hashlib

# Base URL to append if URLs are relative
base_url = "https://www.tipster.io"

# URL of the page to scrape
main_url = "https://www.tipster.io/"

# Send a request to fetch the main page content
response = requests.get(main_url)
soup = BeautifulSoup(response.text, "html.parser")

# Find all links in the page
links = soup.find_all("a", href=True)

# Regex to match URLs like "/team/{number}.html" but exclude gift card page
pattern = re.compile(r"^/team/(?!31361)\d+\.html$")

# Extract and filter URLs based on the pattern
filtered_urls = [link["href"] for link in links if pattern.match(link["href"])]


# Function to extract date from the image URL
def extract_date_from_url(url):
    match = re.search(r"(\d{4})/(\d{4})", url)
    if match:
        year = match.group(1)
        month_day = match.group(2)
        return f"{year}-{month_day[:2]}-{month_day[2:]}"  # Format: YYYY-MM-DD
    return None


# Function to check status, sold, left, and additional deal info
def check_deal_info(url):
    # Complete the URL if it's relative
    full_url = base_url + url
    page_response = requests.get(full_url)
    page_soup = BeautifulSoup(page_response.text, "html.parser")

    # Look for the specific div with id "dealbuttonclosed"
    deal_status_div = page_soup.find("div", id="dealbuttonclosed")

    # Look for sold and left details
    sold_div = page_soup.find("div", id="nowsold")
    left_div = page_soup.find("div", id="nowleft")

    # Extract sold and left data
    sold = sold_div.text.strip().split()[0] if sold_div else "Unknown"
    left = left_div.text.strip().split()[0] if left_div else "Unknown"

    # Extract additional deal information
    deal_name = page_soup.find("h1").text.strip() if page_soup.find("h1") else "No Name"

    # Extract date from the og:image meta tag
    image_meta = page_soup.find("meta", property="og:image")
    date_added = None
    if image_meta:
        date_added = extract_date_from_url(image_meta["content"])

    date_added = date_added if date_added else "No Date"

    # Extract location from the specified div
    location_div = page_soup.find("div", class_="accordion__content")
    location = (
        location_div.p.text.strip()
        if location_div and location_div.p
        else "No Location"
    )

    # Merchant name extraction
    merchant_name = (
        page_soup.find("div", id="teamtoppartner").text.strip()
        if page_soup.find("div", id="teamtoppartner")
        else "No Merchant"
    )

    # Extract old price and currency
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

    # Extract new price and currency
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

    # Check if the deal is sold out or expired
    status = "AVAILABLE"
    if deal_status_div:
        if "SOLD OUT" in deal_status_div.text:
            status = "SOLD OUT"
        elif "EXPIRED" in deal_status_div.text:
            status = "EXPIRED"

    # Get current timestamp for insertion
    inserted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a hashed surrogate key using url and inserted_at timestamp
    surrogate_key = hashlib.md5(f"{url}{inserted_at}".encode()).hexdigest()

    # Create a dictionary for the deal information
    deal_info = {
        "surrogate_key": surrogate_key,  # Add surrogate key to the dictionary
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
        "inserted_at": inserted_at,  # Add timestamp to the dictionary
    }

    return deal_info


# List to hold all deal information
deals = []

# Check all filtered URLs for status, sold, left, and deal info
for url in filtered_urls:
    deal_info = check_deal_info(url)
    deals.append(deal_info)

# Create a DataFrame from the list of deals
deals_df = pd.DataFrame(deals)

# Save DataFrame to CSV for later use
deals_df.to_csv("deals.csv", index=False)