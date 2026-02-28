#!/usr/bin/env python3
"""Met Office DataHub weather fetcher for GitHub Actions"""
import json
import os
import sys
import urllib.request
from datetime import datetime

API_KEY = os.environ.get('METOFFICE_API_KEY', '')
if not API_KEY:
    print("Error: METOFFICE_API_KEY not set")
    sys.exit(1)

BASE_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/daily"

REGIONS = {
    "scotland": {"lat": 57.0, "lon": -4.0, "name": "Scotland Highlands"},
    "midlands": {"lat": 52.5, "lon": -1.8, "name": "Midlands"},
    "south_west": {"lat": 50.9, "lon": -3.5, "name": "South West"},
    "east_anglia": {"lat": 52.5, "lon": 0.5, "name": "East Anglia"},
    "wales": {"lat": 52.1, "lon": -3.7, "name": "Wales"}
}

def fetch_weather(region_key, lat, lon):
    """Fetch weather from Met Office DataHub"""
    url = f"{BASE_URL}?latitude={lat}&longitude={lon}"
    req = urllib.request.Request(url)
    req.add_header("apikey", API_KEY)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"Error fetching {region_key}: {e}")
        return None

def main():
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/weather', exist_ok=True)

    weather_data = {"updated": datetime.now().isoformat(), "regions": {}}

    for region_key, coords in REGIONS.items():
        print(f"Fetching {region_key}...")
        data = fetch_weather(region_key, coords["lat"], coords["lon"])
        if data:
            try:
                series = data['features'][0]['properties']['timeSeries'][0]
                weather_data["regions"][region_key] = {
                    "name": coords["name"],
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "dayMaxScreenTemperature": series.get('dayMaxScreenTemperature', 'N/A'),
                    "nightMinScreenTemperature": series.get('nightMinScreenTemperature', 'N/A'),
                    "dayProbabilityOfRain": series.get('dayProbabilityOfRain', 'N/A'),
                    "weather": series.get('daySignificantWeather', 'Unknown')
                }
                print(f"  ✅ {coords['name']}: {series.get('dayMaxScreenTemperature', 'N/A')}°C")
            except (KeyError, IndexError) as e:
                print(f"  ⚠️ Parse error: {e}")

    output_path = 'data/weather/latest.json'
    with open(output_path, 'w') as f:
        json.dump(weather_data, f, indent=2)

    print(f"\n✅ Weather data saved to {output_path}")
    print(f"   Regions: {len(weather_data['regions'])}")

if __name__ == "__main__":
    main()
