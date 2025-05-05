import requests
import time
from bs4 import BeautifulSoup
import warnings
import json
import csv

def fetch_html(base_url, filters):
    print("🔎 Starting request to:", base_url)
    start_time = time.time()
    try:
        response = requests.get(base_url, params=filters)
        response.raise_for_status()
        elapsed = time.time() - start_time
        print(f"✅ Request completed in {elapsed:.2f} seconds")
        return response.text
    except requests.RequestException as e:
        elapsed = time.time() - start_time
        print(f"❌ Request failed after {elapsed:.2f} seconds: {e}")
        return None
    
def extract_offers_from_script_in_html(html_content):
    """
    Extracts all car offers from a <script type="application/ld+json"> structure in the HTML.
    Returns a list of offer dictionaries, or an empty list if not found.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and 'offers' in data and isinstance(data['offers'], list):
                return data['offers']
        except (json.JSONDecodeError, TypeError):
            continue
    return []

def save_offers_to_csv(offers, filename):
    """
    Saves a list of offer dictionaries to a CSV file.
    Each offer is expected to follow the structure from the JSON-LD 'offers' array.
    """
    if not offers:
        print("No offers to save.")
        return

    # Define CSV columns
    fieldnames = [
        'price', 'priceCurrency',
        'car_name', 'brand', 'model', 'vehicleConfiguration',
        'mileage', 'mileage_unit', 'fuelType', 'year',
        'seller_name', 'seller_url'
    ]

    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for offer in offers:
            item = offer.get('itemOffered', {})
            mileage = item.get('mileageFromOdometer', {})
            seller = offer.get('seller', {})
            row = {
                'price': offer.get('price'),
                'priceCurrency': offer.get('priceCurrency'),
                'car_name': item.get('name'),
                'brand': item.get('brand', {}).get('name') if isinstance(item.get('brand'), dict) else item.get('brand'),
                'model': item.get('model'),
                'vehicleConfiguration': item.get('vehicleConfiguration'),
                'mileage': mileage.get('value'),
                'mileage_unit': mileage.get('unitCode'),
                'fuelType': item.get('fuelType'),
                'year': None,
                'seller_name': seller.get('name'),
                'seller_url': seller.get('url'),
            }
            # Extract year from dateVehicleFirstRegistered if available
            date_registered = item.get('dateVehicleFirstRegistered')
            if date_registered and isinstance(date_registered, str) and len(date_registered) >= 4:
                row['year'] = date_registered[:4]
            writer.writerow(row)
    print(f"✅ Saved {len(offers)} offers to {filename}")

def parse_car_offers_from_html(html_content):
    """
    Deprecated: This function is deprecated and may be removed in future versions.

    Parses the HTML content and extracts all car offer information from divs with class 'card-stock'.
    Returns a list of dictionaries with car details.
    """
    warnings.warn(
        "parse_car_offers_from_html is deprecated and may be removed in future versions.",
        DeprecationWarning,
        stacklevel=2
    )
    print("🧩 Parsing HTML content for car offers...")
    soup = BeautifulSoup(html_content, 'html.parser')
    offers = []
    cards = soup.find_all('div', class_='card-stock')
    print(f"🔍 Found {len(cards)} car offer cards.")
    for idx, card in enumerate(cards, 1):
        # Title
        title_tag = card.find('h3')
        title = title_tag.get_text(strip=True) if title_tag else None
        # Link
        link_tag = card.find('a', class_='btn-primary')
        link = link_tag['href'] if link_tag and link_tag.has_attr('href') else None
        # Price (not in card, but can be found in JS variable in HTML)
        price = None
        # Board (hidden input)
        board_tag = card.find('input', {'id': 'board'})
        board = board_tag['value'] if board_tag and board_tag.has_attr('value') else None
        offers.append({
            'title': title,
            'link': link,
            'board': board,
            'price': price,  # price can be filled by cross-referencing JS if needed
        })
    print(f"✅ Finished parsing. Total offers extracted: {len(offers)}")
    return offers
