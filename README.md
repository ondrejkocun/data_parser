# Data Parser

## Project Description
Data Parser is a configurable Python scraper for collecting flyer data from retail pages.  
It parses flyer title, shop name, thumbnail, validity dates, and parse timestamp, then exports the results to JSON.

## Features
- Configurable scraping rules via `ScraperConfig`
- CLI overrides for quick execution
- Optional external config file support (`.json`, `.yaml`, `.yml`)
- JSON output with UTF-8 encoding

## Requirements
- Python 3.9+
- `requests`
- `beautifulsoup4`
- Optional: `PyYAML` (only if using YAML config files)

## Installation
```bash
pip install requests beautifulsoup4
```

If you want to use YAML config files:
```bash
pip install pyyaml
```

## Usage

Run with defaults:
```bash
python /home/runner/work/data_parser/data_parser/data_parser_zadanie.py
```

Set source URL and output file directly:
```bash
python /home/runner/work/data_parser/data_parser/data_parser_zadanie.py \
  --url "https://www.prospektmaschine.de/hypermarkte/" \
  --output "flyers.json"
```

Use external configuration:
```bash
python /home/runner/work/data_parser/data_parser/data_parser_zadanie.py \
  --config "/absolute/path/config.json"
```

CLI precedence:
- `--url` overrides `base_url` from config/defaults
- `--output` overrides `output_file` from config/defaults

## Example Config (`config.json`)
```json
{
  "base_url": "https://www.prospektmaschine.de/hypermarkte/",
  "output_file": "flyers.json",
  "flyer_selector": ".grid-item",
  "description_selector": ".letak-description",
  "title_selector": "p.grid-item-content strong",
  "shop_name_selector": "a[title]",
  "thumbnail_selector": "div.img-container img",
  "date_selector": "small",
  "shop_name_regex": "Geschäftes\\s+([^-|]+)",
  "date_range_regex": "(\\d{2}\\.\\d{2}\\.\\d{4})\\s*-\\s*(\\d{2}\\.\\d{2}\\.\\d{4})",
  "single_date_regex": "(\\d{2}\\.\\d{2}\\.\\d{4})",
  "input_date_format": "%d.%m.%Y",
  "output_date_format": "%Y-%m-%d",
  "output_time_format": "%Y-%m-%d %H:%M:%S",
  "missing_value": "N/A"
}
```
