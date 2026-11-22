import json
import re
import urllib.request
from datetime import datetime, timezone

POOLS = {
    "Kombibad Gropiusstadt Hallenbad Mitte": "https://www.berlinerbaeder.de/baeder/detail/kombibad-gropiusstadt-hallenbad/#Badausstattung/",
    "Schwimmhalle Landsberger Allee": "https://www.berlinerbaeder.de/baeder/detail/schwimm-und-sprunghalle-im-europasportpark-sse/"
}

def fetch_pool_data():
    results = []
    headers = {'User-Agent': 'BerlinPoolWidgetBot/1.0'}
    
    for name, url in POOLS.items():
        try:
            req = urllib.request.Request(url, headers=headers)
            html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
            
            # Extract water temperatures (e.g., "Schwimmerbecken: 26,0°C")
            temps = re.findall(r'(Schwimmerbecken|Nichtschwimmerbecken):\s*([\d,]+°C)', html)
            temp_str = ", ".join([f"{t[0][:3]}: {t[1]}" for t in temps]) if temps else "Keine Temp."
            
            results.append({
                "name": name,
                "temp": temp_str,
                "url": url
            })
        except Exception as e:
            results.append({"name": name, "temp": "Fehler beim Laden", "url": url})

    output = {
        "updated_utc": datetime.now(timezone.utc).strftime("%H:%M UTC"),
        "pools": results
    }
    
    with open("pools.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fetch_pool_data()
