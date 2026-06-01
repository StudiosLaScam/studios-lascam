from ics import Calendar
from datetime import datetime, timedelta
import requests

# =========================
# CONFIGURATION
# =========================

CALENDARS = {

    "Studio image":
    "https://outlook.office365.com/owa/calendar/6714a0f86ead44b280f0f20fbec7c7e8@lascam.fr/f79c90a8ed194c32a17994039be42f251899749353559877707/calendar.ics",

    "Studio son":
    "https://outlook.office365.com/owa/calendar/6714a0f86ead44b280f0f20fbec7c7e8@lascam.fr/a706e01e72734e548f7b6c7280ff356415769568704837581163/calendar.ics"
}

# =========================
# TRADUCTIONS FR
# =========================

MOIS = {
    "January": "Janvier",
    "February": "Février",
    "March": "Mars",
    "April": "Avril",
    "May": "Mai",
    "June": "Juin",
    "July": "Juillet",
    "August": "Août",
    "September": "Septembre",
    "October": "Octobre",
    "November": "Novembre",
    "December": "Décembre"
}

JOURS = {
    "Monday": "Lun",
    "Tuesday": "Mar",
    "Wednesday": "Mer",
    "Thursday": "Jeu",
    "Friday": "Ven",
    "Saturday": "Sam",
    "Sunday": "Dim"
}

# =========================
# PERIODE
# =========================

TODAY = datetime.today()

END_DATE = TODAY + timedelta(days=61)

# =========================
# DETECTION CRENEAUX
# =========================

def get_slot(start, end):

    start_hour = start.hour
    end_hour = end.hour

    # Journée complète
    if start_hour <= 10 and end_hour >= 18:
        return "Matin + après-midi"

    # Matin
    if start_hour <= 10 and end_hour <= 13:
        return "Matin"

    # Après-midi
    if start_hour >= 14:
        return "Après-midi"

    return None

# =========================
# STOCKAGE GLOBAL
# =========================

months_data = {}

# =========================
# ANALYSE CALENDRIERS
# =========================

for studio_name, url in CALENDARS.items():

    response = requests.get(url)

    calendar = Calendar(response.text)

    events = sorted(
        calendar.events,
        key=lambda e: e.begin
    )

    for event in events:

        start = (
            event.begin
            .datetime
            .replace(tzinfo=None)
        )

        end = (
            event.end
            .datetime
            .replace(tzinfo=None)
        )

        # Filtre période
        if (
            start.date() < TODAY.date() or
            start.date() > END_DATE.date()
        ):
            continue

        # Exclure weekends
        if start.weekday() >= 5:
            continue

        slot = get_slot(start, end)

        if not slot:
            continue
            
        month_key = start.strftime("%Y-%m")

        month_name = (
            f"{MOIS[start.strftime('%B')]} "
            f"{start.strftime('%Y')}"
        )

        date_key = start.strftime("%Y-%m-%d")

        pretty_date = (
            f"{JOURS[start.strftime('%A')]} "
            f"{start.strftime('%d/%m')}"
        )

        if month_key not in months_data:

            months_data[month_key] = {
                "name": month_name,
                "dates": {}
            }

        if date_key not in months_data[month_key]["dates"]:

            months_data[month_key]["dates"][date_key] = {
                "pretty": pretty_date,
                "Studio image": "—",
                "Studio son": "—"
            }

        current = (
            months_data[month_key]
            ["dates"][date_key]
            [studio_name]
        )

        # Fusion matin + après-midi
        if current == "Matin" and slot == "Après-midi":

            months_data[month_key]["dates"][date_key][studio_name] = "Matin + Après-midi"

        elif current == "Après-midi" and slot == "Matin":

            months_data[month_key]["dates"][date_key][studio_name] = "Matin + Après-midi"

        elif current == "—":

            months_data[month_key]["dates"][date_key][studio_name] = slot

# =========================
# EXPORT JSON
# =========================

import json

with open("disponibilites.json", "w", encoding="utf-8") as f:
    json.dump(
        months_data,
        f,
        ensure_ascii=False,
        indent=2
    )

print("disponibilites.json généré")
