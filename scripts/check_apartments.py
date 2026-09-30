import json
import os
import re
import smtplib
from datetime import datetime
from email.message import EmailMessage

import requests
from bs4 import BeautifulSoup

def send_email(subject, message):

    msg = EmailMessage()

    msg["Subject"] = subject

    msg["From"] = os.environ["GMAIL_USER"]

    msg["To"] = "bkdargan@gmail.com"

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

    print("✅ Email Sent")


def send_text(message):

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
previous_units = []

try:
    with open("previous_units.json", "r") as f:
        previous_data = json.load(f)

    previous_total = previous_data.get("available_count")
    previous_units = previous_data.get("units", [])

except Exception:
    pass


report_text = ""

report_text += (
    "LINK LINDEN AVAILABILITY REPORT\n"
)

report_text += (
    "=============================\n\n"
)

for plan in all_results:

    report_text += (
        f"{plan['floorplan']} "
        f"({plan['bedrooms']} Bed / "
        f"{plan['bathrooms']} Bath)\n"
    )

    report_text += (
        f"Available Units: {plan['count']}\n"
    )

    report_text += (
        f"URL: {plan['url']}\n"
    )

    for apartment in plan["apartments"]:

        report_text += (
            f"\nUnit #{apartment['unit']}\n"
        )

        report_text += (
            f"{apartment['availability']}\n"
        )

        report_text += (
            f"${apartment['rent']}\n"
        )

    report_text += "\n"

report_text += (
    f"\nTOTAL AVAILABLE APARTMENTS: "
    f"{current_total}\n"
)

if previous_total is not None:

    report_text += (
        f"\nPrevious Total: {previous_total}\n"
    )

    report_text += (
        f"Current Total: {current_total}\n"
    )

    delta = current_total - previous_total

if added_units:

    report_text += "\n🚨 NEWLY ADDED UNITS\n"

    for unit in sorted(added_units):
        floorplan, unit_num = unit.split(":")
        report_text += (
            f"  + {floorplan} Unit #{unit_num}\n"
        )

if removed_units:

    report_text += "\n📉 REMOVED UNITS\n"

    for unit in sorted(removed_units):
        floorplan, unit_num = unit.split(":")
        report_text += (
            f"  - {floorplan} Unit #{unit_num}\n"
        )

if not added_units and not removed_units:

    report_text += "\n✅ NO CHANGE\n"
    current_unit_set = {
        f"{u['floorplan']}:{u['unit']}"
        for u in current_units
    }

    previous_unit_set = {
        f"{u['floorplan']}:{u['unit']}"
        for u in previous_units
    }

added_units = current_unit_set - previous_unit_set
removed_units = previous_unit_set - current_unit_set
#
# TEST MODE
# SEND TEXT EVERY RUN
#

send_email(
    f"Link Linden Availability - {current_total} Available",
    report_text
)

send_text(
    f"🏠 Link Linden Update\n\n"
    f"Total Available: {current_total}\n\n"
    f"See email for full report."
)

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
