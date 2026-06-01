from ics import Calendar
from datetime import datetime, timedelta
import requests
import locale

# =========================
# FRANÇAIS
# =========================

locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

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
        month_name = start.strftime("%B %Y").capitalize()

        date_key = start.strftime("%Y-%m-%d")

        pretty_date = (
            start.strftime("%A %d/%m")
            .capitalize()
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
# GENERATION HTML
# =========================

last_update = datetime.now().strftime("%d/%m/%Y à %H:%M")

html = f"""

<div style="
font-family: Arial, sans-serif;
">

<h1 style="
color:#C32B49;
margin-bottom:8px;
">
Disponibilités des studios LaScam
</h1>

<p style="
color:#777;
font-size:13px;
margin-top:0;
margin-bottom:40px;
">
Dernière mise à jour : {last_update}
</p>

"""

for month_key in sorted(months_data.keys()):

    month = months_data[month_key]

    html += f"""

    <h2 style="
    color:#C32B49;
    margin-top:40px;
    margin-bottom:18px;
    ">
    {month['name']}
    </h2>

    <table style="
    border-collapse: collapse;
    font-size: 14px;
    min-width: 700px;
    margin-bottom: 40px;
    ">

    <tr>

    <th style="
    border:1px solid #ddd;
    padding:10px;
    background:#f3f3f3;
    text-align:left;
    ">
    Date
    </th>

    <th style="
    border:1px solid #ddd;
    padding:10px;
    background:#eef8f1;
    color:#2e8b57;
    text-align:left;
    ">
    Studio image
    </th>

    <th style="
    border:1px solid #ddd;
    padding:10px;
    background:#fff4ea;
    color:#e67e22;
    text-align:left;
    ">
    Studio son
    </th>

    </tr>
    """

    for date_key in sorted(month["dates"].keys()):

        row = month["dates"][date_key]

        html += f"""

        <tr>

        <td style="
        border:1px solid #ddd;
        padding:10px;
        ">
        {row['pretty']}
        </td>

        <td style="
        border:1px solid #ddd;
        padding:10px;
        ">
        {row['Studio image']}
        </td>

        <td style="
        border:1px solid #ddd;
        padding:10px;
        ">
        {row['Studio son']}
        </td>

        </tr>
        """

    html += "</table>"

html += "</div>"

# =========================
# EXPORT HTML
# =========================

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html généré")