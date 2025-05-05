from functions import fetch_html, extract_offers_from_script_in_html, save_offers_to_csv
from constants import base_url

def main():
    filters = {
        "page": 1,
        "location_state": "PARANÁ",
        "make": "LEXUS",
    }

    all_offers = []
    while True:
        html_content = fetch_html(base_url, filters)
        offers = extract_offers_from_script_in_html(html_content)
        if not offers:
            break
        all_offers.extend(offers)
        filters["page"] += 1

    save_offers_to_csv(all_offers, "grupo-barigui-seminovos-offers.csv")

if __name__ == "__main__":
    main()