import json
import os
import re
import smtplib
from datetime import datetime
from email.message import EmailMessage

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/128.0 Safari/537.36"
    )
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


def send_text(message):

    try:

        msg = EmailMessage()

        msg["Subject"] = ""

        msg["From"] = os.environ["GMAIL_USER"]

        msg["To"] = "9198100874@vtext.com"

        msg.set_content(message)

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as smtp:

            smtp.login(
                os.environ["GMAIL_USER"],
                os.environ["GMAIL_APP_PASSWORD"]
            )

            smtp.send_message(msg)

        print("✅ Text Sent")

    except Exception as e:

        print(f"❌ Text Failed: {e}")


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

    except Exception as e:

        print(f"ERROR: {e}")

        all_results.append(
            {
                "floorplan": plan_name,
                "url": url,
                "bedrooms": details["bedrooms"],
                "bathrooms": details["bathrooms"],
                "count": 0,
                "apartments": []
            }
        )


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


grand_total = 0

print()
print("=" * 70)
print("LINK LINDEN AVAILABILITY REPORT")
print("=" * 70)

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

    for apartment in plan["apartments"]:

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

print()
print("=" * 70)
print(
    f"TOTAL AVAILABLE APARTMENTS: {grand_total}"
)
print("=" * 70)

current_total = grand_total

previous_total = None

try:

    with open(
        "previous_ount.json",
        "r"
    ) as f:

        previous_total = (
            json.load(f)
            .get("available_count")
        )

except Exception:
    pass


report_text = ""
report_text += "🏠 Link Linden Update\n\n"
report_text += f"Total Available: {current_total}\n\n"

for plan in all_results:

    report_text += (
        f"{plan['floorplan']} "
        f"({plan['bedrooms']}bd/"
        f"{plan['bathrooms']}ba)"
        f": {plan['count']}\n"
    )

report_text += (
    "\nQuick Check:\n"
    "https://www.linklinden.com/floorplans/b1"
)

#
# TEST MODE
# SEND TEXT EVERY RUN
#

send_text(report_text)

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
