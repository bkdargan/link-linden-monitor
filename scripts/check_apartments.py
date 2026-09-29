import json
import re
import requests
from bs4 import BeautifulSoup

URL = "https://www.linklinden.com/floorplans/b1"

response = requests.get(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
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
