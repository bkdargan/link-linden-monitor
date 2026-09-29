import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.linklinden.com/floorplans/b1"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/128.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/"
}

response = requests.get(
    URL,
    headers=HEADERS,
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

text = soup.get_text("\n")

#
# SAVE RAW TEXT FOR DEBUGGING
#

with open(
    "page_dump.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(text)

#
# FIND APARTMENTS
#

apartments = []

pattern = re.compile(
    r"Apartment:\s*#\s*(\d+).*?"
    r"(Available Now|Date Available:\s*[^\n]+).*?"
    r"Starting at:\s*\$([0-9,\.]+)",
    re.DOTALL
)

for match in pattern.finditer(text):

    apartments.append({
        "unit": match.group(1),
        "availability": match.group(2).strip(),
        "rent": match.group(3).strip()
    })

#
# REPORT
#

report = {
    "timestamp": datetime.now().isoformat(),
    "available_count": len(apartments),
    "url": URL,
    "apartments": apartments
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

#
# CONSOLE REPORT
#

print()
print("=" * 60)
print("LINK LINDEN B1 REPORT")
print("=" * 60)

print()
print(f"Available Units: {len(apartments)}")
print()

for unit in apartments:

    print(f"🏠 Unit #{unit['unit']}")
    print(f"📅 {unit['availability']}")
    print(f"💲 {unit['rent']}")
    print()

print("Quick Check:")
print(URL)
print()

#
# CHANGE DETECTION
#

previous_count = None

try:

    with open(
        "previous_count.json",
        "r"
    ) as f:

        previous = json.load(f)

        previous_count = previous.get(
            "available_count"
        )

except Exception:
    pass

if previous_count is not None:

    delta = (
        len(apartments)
        - previous_count
    )

    print(
        f"Previous Count: {previous_count}"
    )

    print(
        f"Current Count: {len(apartments)}"
    )

    if delta > 0:

        print(
            f"🚨 {delta} NEW UNIT(S) AVAILABLE"
        )

    elif delta < 0:

        print(
            f"📉 {abs(delta)} UNIT(S) REMOVED"
        )

    else:

        print(
            "✅ No Change"
        )

with open(
    "previous_count.json",
    "w"
) as f:

    json.dump(
        {
            "available_count": len(apartments)
        },
        f,
        indent=2
    )
