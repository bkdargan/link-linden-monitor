import json
import re
import requests
from bs4 import BeautifulSoup

URL = "https://www.linklinden.com/floorplans/b1"

headers = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}

response = requests.get(
    URL,
    headers=headers,
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

text = soup.get_text("\n")

matches = re.findall(
    r"Apartment:\s*#\s*(\d+)",
    text
)

available_count = len(matches)

print()
print("=" * 50)
print("LINK LINDEN REPORT")
print("=" * 50)
print()

print(
    f"Available B1 Units: {available_count}"
)

for unit in matches:

    print(
        f"Unit #{unit}"
    )

report = {
    "available_count": available_count,
    "units": matches,
    "url": URL
}

with open(
    "availability_report.json",
    "w"
) as f:

    json.dump(
        report,
        f,
        indent=2
    )
