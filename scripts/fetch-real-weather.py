#!/usr/bin/env python3
"""Real Met Office weather fetcher using API key"""
import json
import os
import sys
import urllib.request

# Load API key from environment variable (set METOFFICE_API_KEY before running)
API_KEY = os.environ.get('METOFFICE_API_KEY', '')
if not API_KEY:
    print("Warning: METOFFICE_API_KEY environment variable not set")
    sys.exit(0)

# Met Office DataPoint API
BASE_URL = "https://api-metoffice.apiconnect.ibmcloud.com/metoffice/production/v0/forecasts/point/daily"

REGIONS = {
    "scotland": {"lat": 57.0, "lon": -4.0},
    "midlands": {"lat": 52.5, "lon": -1.8},  
    "south_west": {"lat": 50.9, "lon": -3.5},
    "east_anglia": {"lat": 52.5, "lon": 0.5},
    "wales": {"lat": 52.1, "lon": -3.7}
}

def fetch_weather(region, lat, lon):
    """Fetch real weather from Met Office"""
    url = f"{BASE_URL}?latitude={lat}&longitude={lon}"
    req = urllib.request.Request(url)
    req.add_header("X-IBM-Client-Id", API_KEY.split('.')[0])
    req.add_header("X-IBM-Client-Secret", API_KEY.split('.')[-1])
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"Error fetching {region}: {e}")
        return None

def main():
    print("Fetching real weather data...")
    for region, coords in REGIONS.items():
        data = fetch_weather(region, coords["lat"], coords["lon"])
        if data:
            print(f"✅ {region}: {data['features'][0]['properties']['timeSeries'][0]['daySignificantWeather']}")
    
    print("\nWeather data ready for farmers")

if __name__ == "__main__":
    main()
