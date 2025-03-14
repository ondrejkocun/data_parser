import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

class ProspektScraper:
    BASE_URL = "https://www.prospektmaschine.de/hypermarkte/"

    def __init__(self):
        self.session = requests.Session()

    def fetch_page(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException:
            return None

    def parse_page(self, html):
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        flyer_elements = soup.select(".grid-item")

        flyers = []
        for flyer in flyer_elements:
            description = flyer.select_one(".letak-description")
            if not description:
                continue

            title_tag = description.select_one("p.grid-item-content strong")
            title = title_tag.text.strip() if title_tag else "N/A"

            shop_name_tag = description.select_one("a[title]")
            shop_name = self.extract_shop_name(shop_name_tag["title"]) if shop_name_tag else "N/A"

            thumbnail = self.extract_thumbnail(flyer)
            valid_from, valid_to = self.extract_validity_dates(description)
            parsed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            flyers.append({
                "title": title,
                "thumbnail": thumbnail,
                "shop_name": shop_name,
                "valid_from": valid_from,
                "valid_to": valid_to,
                "parsed_time": parsed_time
            })

        return flyers

    def extract_shop_name(self, title):
        match = re.search(r"Geschäftes (\w+)", title)
        return match.group(1) if match else "N/A"

    def extract_thumbnail(self, flyer):
        img_tag = flyer.select_one("div.img-container img")
        if img_tag:
            return img_tag.get("src") or img_tag.get("data-src") or "N/A"
        return "N/A"

    def extract_validity_dates(self, flyer):
        date_elements = flyer.select("small")
        if not date_elements:
            return "N/A", "N/A"

        date_text = date_elements[0].text.strip()
        match = re.search(r"(\d{2}\.\d{2}\.\d{4}) - (\d{2}\.\d{2}\.\d{4})", date_text)
        if match:
            return self.format_date(match.group(1)), self.format_date(match.group(2))

        match = re.search(r"(\d{2}\.\d{2}\.\d{4})", date_text)
        if match:
            return self.format_date(match.group(1)), self.format_date(match.group(1))

        return "N/A", "N/A"

    def format_date(self, date_text):
        try:
            return datetime.strptime(date_text, "%d.%m.%Y").strftime("%Y-%m-%d")
        except ValueError:
            return "N/A"

    def save_to_json(self, data, filename="flyers.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def run(self):
        html = self.fetch_page(self.BASE_URL)
        if html:
            flyers = self.parse_page(html)
            self.save_to_json(flyers)

if __name__ == "__main__":
    scraper = ProspektScraper()
    scraper.run()
