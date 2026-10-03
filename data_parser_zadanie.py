import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup


@dataclass
class ScraperConfig:
    base_url: str = "https://www.prospektmaschine.de/hypermarkte/"
    output_file: str = "flyers.json"
    flyer_selector: str = ".grid-item"
    description_selector: str = ".letak-description"
    title_selector: str = "p.grid-item-content strong"
    shop_name_selector: str = "a[title]"
    thumbnail_selector: str = "div.img-container img"
    date_selector: str = "small"
    shop_name_regex: str = r"Geschäftes\s+([^-|]+)"
    date_range_regex: str = r"(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})"
    single_date_regex: str = r"(\d{2}\.\d{2}\.\d{4})"
    input_date_format: str = "%d.%m.%Y"
    output_date_format: str = "%Y-%m-%d"
    output_time_format: str = "%Y-%m-%d %H:%M:%S"
    missing_value: str = "N/A"


class GenericFlyerScraper:
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.session = requests.Session()

    def fetch_page(self, url: str) -> Optional[str]:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException:
            return None

    def parse_page(self, html: Optional[str]):
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        flyer_elements = soup.select(self.config.flyer_selector)

        flyers = []
        for flyer in flyer_elements:
            description = flyer.select_one(self.config.description_selector)
            if not description:
                continue

            title = self._extract_text(description, self.config.title_selector)
            shop_name_title = self._extract_attribute(
                description, self.config.shop_name_selector, "title"
            )
            shop_name = self.extract_shop_name(shop_name_title)

            thumbnail = self.extract_thumbnail(flyer)
            valid_from, valid_to = self.extract_validity_dates(description)
            parsed_time = datetime.now().strftime(self.config.output_time_format)

            flyers.append(
                {
                    "title": title,
                    "thumbnail": thumbnail,
                    "shop_name": shop_name,
                    "valid_from": valid_from,
                    "valid_to": valid_to,
                    "parsed_time": parsed_time,
                }
            )

        return flyers

    def _extract_text(self, root, selector: str) -> str:
        element = root.select_one(selector)
        if not element:
            return self.config.missing_value
        text = element.get_text(strip=True)
        return text if text else self.config.missing_value

    def _extract_attribute(self, root, selector: str, attr_name: str) -> str:
        element = root.select_one(selector)
        if not element:
            return self.config.missing_value
        return element.get(attr_name, self.config.missing_value)

    def extract_shop_name(self, title: str) -> str:
        if not title or title == self.config.missing_value:
            return self.config.missing_value

        match = re.search(self.config.shop_name_regex, title)
        if match:
            return match.group(1).strip()
        return title.strip()

    def extract_thumbnail(self, flyer) -> str:
        img_tag = flyer.select_one(self.config.thumbnail_selector)
        if img_tag:
            return (
                img_tag.get("src")
                or img_tag.get("data-src")
                or self.config.missing_value
            )
        return self.config.missing_value

    def extract_validity_dates(self, flyer):
        date_elements = flyer.select(self.config.date_selector)
        if not date_elements:
            return self.config.missing_value, self.config.missing_value

        date_text = date_elements[0].get_text(strip=True)
        match = re.search(self.config.date_range_regex, date_text)
        if match:
            return self.format_date(match.group(1)), self.format_date(match.group(2))

        match = re.search(self.config.single_date_regex, date_text)
        if match:
            single = self.format_date(match.group(1))
            return single, single

        return self.config.missing_value, self.config.missing_value

    def format_date(self, date_text: str) -> str:
        try:
            return datetime.strptime(
                date_text, self.config.input_date_format
            ).strftime(self.config.output_date_format)
        except ValueError:
            return self.config.missing_value

    def save_to_json(self, data, filename: Optional[str] = None):
        target_file = filename or self.config.output_file
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def run(self):
        html = self.fetch_page(self.config.base_url)
        if html:
            flyers = self.parse_page(html)
            self.save_to_json(flyers)


def parse_args():
    parser = argparse.ArgumentParser(description="Generic flyer parser")
    parser.add_argument("--url", default=ScraperConfig.base_url)
    parser.add_argument("--output", default=ScraperConfig.output_file)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    scraper = GenericFlyerScraper(
        ScraperConfig(base_url=args.url, output_file=args.output)
    )
    scraper.run()
