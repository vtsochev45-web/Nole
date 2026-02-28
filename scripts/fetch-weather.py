#!/usr/bin/env python3
"""Weather fetcher for GitHub Actions using Open-Meteo API (free, no key required)"""
import json
import os
import urllib.request
from datetime import datetime

BASE_URL = "https://api.open-meteo.com/v1/forecast"

REGIONS = {
    "scotland": {"lat": 57.0, "lon": -4.0, "name": "Scotland Highlands"},
    "midlands": {"lat": 52.5, "lon": -1.8, "name": "Midlands"},
    "south_west": {"lat": 50.9, "lon": -3.5, "name": "South West"},
    "east_anglia": {"lat": 52.5, "lon": 0.5, "name": "East Anglia"},
    "wales": {"lat": 52.1, "lon": -3.7, "name": "Wales"}
}

def fetch_weather(region_key, lat, lon):
    """Fetch weather from Open-Meteo (free, no API key required)"""
    params = (
        f"latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode"
        "&forecast_days=1&timezone=Europe%2FLondon"
    )
    url = f"{BASE_URL}?{params}"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
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
                daily = data['daily']
                weather_data["regions"][region_key] = {
                    "name": coords["name"],
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "dayMaxScreenTemperature": daily['temperature_2m_max'][0],
                    "nightMinScreenTemperature": daily['temperature_2m_min'][0],
                    "dayProbabilityOfRain": daily['precipitation_probability_max'][0],
                    "weather": daily['weathercode'][0]
                }
                print(f"  ✅ {coords['name']}: {daily['temperature_2m_max'][0]}°C")
            except (KeyError, IndexError) as e:
                print(f"  ⚠️ Parse error: {e}")

    output_path = 'data/weather/latest.json'
    with open(output_path, 'w') as f:
        json.dump(weather_data, f, indent=2)

    print(f"\n✅ Weather data saved to {output_path}")
    print(f"   Regions: {len(weather_data['regions'])}")

if __name__ == "__main__":
    main()
