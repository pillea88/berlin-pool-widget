import html as html_lib
import json
import re
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

POOLS = {
    "Stadtbad Mitte": "https://www.berlinerbaeder.de/baeder/detail/stadtbad-mitte-james-simon/",
    "Schwimmhalle Zingster Str.": "https://www.berlinerbaeder.de/baeder/detail/schwimmhalle-zingster-strasse/"
}

WEEKDAYS_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

def fetch_pool_data():
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; BerlinPoolWidget/1.0)'}
    berlin_now = datetime.now(ZoneInfo("Europe/Berlin"))
    today_de = WEEKDAYS_DE[berlin_now.weekday()]

    for name, url in POOLS.items():
        try:
            req = urllib.request.Request(url, headers=headers)
            raw_html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')

            # Strip all HTML tags and decode entities (&nbsp;, &deg;, etc.) into clean text
            clean_text = html_lib.unescape(re.sub(r'<[^>]+>', ' ', raw_html))
            clean_text = re.sub(r'\s+', ' ', clean_text)

            # 1. Extract all basin temperatures (Schwimmerbecken, Nichtschwimmerbecken, Sprungbecken, etc.)
            temps = re.findall(
                r'(Schwimmerbecken|Nichtschwimmerbecken|Sprungbecken|Lehrzwimmbecken|Warmbecken)\s*:?\s*(\d{2},\d)\s*°?\s*C',
                clean_text
            )
            if temps:
                # Deduplicate while preserving order
                seen = set()
                temp_parts = []
                for basin, val in temps:
                    if basin not in seen:
                        seen.add(basin)
                        temp_parts.append(f"{basin[:3]}: {val}°C")
                temp_str = ", ".join(temp_parts)
            else:
                temp_str = "Keine Temp."

            # 2. Extract today's public swimming opening times (e.g., "Montag 06:30 - 08:00 ... öffentl.")
            hours_matches = re.findall(
                rf'{today_de}\s+(\d{{2}}:\d{{2}}\s*-\s*\d{{2}}:\d{{2}})(?:\s*Uhr)?\s*(öffentl\.|Geschlossen)',
                clean_text
            )
            if hours_matches:
                hours_str = ", ".join([f"{t} ({status})" for t, status in hours_matches])
            elif f"{today_de} Geschlossen" in clean_text:
                hours_str = "Geschlossen"
            else:
                hours_str = "Siehe Website"

            results.append({
                "name": name,
                "temp": temp_str,
                "hours": hours_str,
                "url": url
            })
        except Exception:
            results.append({
                "name": name,
                "temp": "Fehler beim Laden",
                "hours": "",
                "url": url
            })

    output = {
        "updated_berlin": berlin_now.strftime("%H:%M Uhr"),
        "weekday": today_de,
        "pools": results
    }

    with open("pools.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fetch_pool_data()
