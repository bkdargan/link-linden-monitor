import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

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

FLOORPLANS = {
    "B1": {
        "url": "https://www.linklinden.com/floorplans/b1",
        "bedrooms": 2,
        "bathrooms": 2
    },
    "B2": {
        "url": "https://www.linklinden.com/floorplans/b2",
        "bedrooms": 2,
        "bathrooms": 2
    },
    "B3": {
        "url": "https://www.linklinden.com/floorplans/b3",
        "bedrooms": 2,
        "bathrooms": 2
    },
    "B1-A": {
        "url": "https://www.linklinden.com/floorplans/b1-a",
        "bedrooms": 2,
        "bathrooms": 2
    }
}

all_results = []

for plan_name, details in FLOORPLANS.items():

    url = details["url"]

    print()
    print("=" * 60)
    print(f"CHECKING {plan_name}")
    print("=" * 60)

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

    except Exception as e:

        print(f"ERROR: {e}")

        all_results.append({
            "floorplan": plan_name,
            "url": url,
            "bedrooms": details["bedrooms"],
            "bathrooms": details["bathrooms"],
            "count": 0,
            "apartments": []
        })

        continue

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    text = soup.get_text("\n")

    apartments = []

    pattern = re.compile(
        r"Apartment:\s*#\s*(\d+).*?"
        r"(Available Now|Date Available:\s*[^\n]+).*?"
        r"Starting at:\s*\$([0-9,\.]+)",
        re.DOTALL
    )

    for match in pattern.finditer(text):

        apartments.append(
            {
                "unit": match.group(1),
                "availability": match.group(2).strip(),
                "rent": match.group(3).strip()
            }
        )

    all_results.append(
        {
            "floorplan": plan_name,
            "url": url,
            "bedrooms": details["bedrooms"],
            "bathrooms": details["bathrooms"],
            "count": len(apartments),
            "apartments": apartments
        }
    )

#
# SAVE JSON REPORT
#

report = {
    "timestamp": datetime.now().isoformat(),
    "floorplans": all_results
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
print("=" * 70)
print("LINK LINDEN AVAILABILITY REPORT")
print("=" * 70)

grand_total = 0

for plan in all_results:

    grand_total += plan["count"]

    print()
    print(
        f"🏠 {plan['floorplan']} "
        f"({plan['bedrooms']} Bed / "
        f"{plan['bathrooms']} Bath)"
    )

    print(
        f"Available Units: {plan['count']}"
    )

    print(
        f"Quick Check: {plan['url']}"
    )

    print()

    for apartment in plan["apartments"\]:

        print(
            f"  Unit #{apartment['unit']}"
        )

        print(
            f"  Availability: "
            f"{apartment['availability']}"
        )

        print(
            f"  Rent: "
            f"${apartment['rent']}"
        )

        print()

print("=" * 70)
print(
    f"TOTAL AVAILABLE APARTMENTS: {grand_total}"
)
print("=" * 70)

#
# TRACK CHANGES
#

current_total = grand_total

previous_total = None

try:

    with open(
        "previous_count.json",
        "r"
    ) as f:

        previous_total = json.load(f).get(
            "available_count"
        )

except Exception:
    pass

if previous_total is not None:

    print()
    print(
        f"Previous Total: {previous_total}"
    )

    print(
        f"Current Total: {current_total}"
    )

    delta = current_total - previous_total

    if delta > 0:

        print(
            f"🚨 {delta} NEW APARTMENT(S) AVAILABLE"
        )

    elif delta < 0:

        print(
            f"📉 {abs(delta)} APARTMENT(S) NO LONGER AVAILABLE"
        )

    else:

        print("✅ No Change")

with open(
    "previous_count.json",
    "w"
) as f:

    json.dump(
        {
            "available_count": current_total
        },
        f,
        indent=2
    )
