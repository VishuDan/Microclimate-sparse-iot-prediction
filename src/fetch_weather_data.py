"""
fetch_weather_data.py

Pulls historical hourly weather data from the Open-Meteo Archive API for a
given bounding area (a grid of lat/lon points around a campus/farm), and
saves it as a CSV. This acts as the backup / simulated dataset for the
microclimate prediction pipeline, and as the source for creating synthetic
"sparse sensor network" experiments by subsampling grid points.

No API key required.

Usage:
    python fetch_weather_data.py \
        --center_lat 30.27247519898127 --center_lon 78.0012824465569 \
        --start_date 2026-08-01 --end_date 2026-08-24 \
        --grid_size 5 --spacing_km 0.3 \
        --out data/raw/weather_grid.csv
"""

import argparse
import time
import requests
import pandas as pd

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

HOURLY_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "soil_moisture_0_to_7cm",
    "shortwave_radiation",
    "surface_pressure",
]


def make_grid(center_lat, center_lon, grid_size, spacing_km):
    """Generate a grid_size x grid_size lat/lon grid centered on a point.
    Roughly converts km spacing to degrees (approximation, fine for small areas)."""
    deg_per_km = 1 / 111.0  # ~111km per degree latitude
    offset = (grid_size - 1) / 2
    points = []
    for i in range(grid_size):
        for j in range(grid_size):
            lat = center_lat + (i - offset) * spacing_km * deg_per_km
            lon = center_lon + (j - offset) * spacing_km * deg_per_km
            points.append((round(lat, 6), round(lon, 6), f"node_{i}_{j}"))
    return points


def fetch_point(lat, lon, start_date, end_date):
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(HOURLY_VARS),
        "timezone": "auto",
    }
    resp = requests.get(ARCHIVE_URL, params=params, timeout=30)
    if resp.status_code != 200:
        try:
            reason = resp.json().get("reason", resp.text)
        except ValueError:
            reason = resp.text
        raise requests.exceptions.HTTPError(f"{resp.status_code} error: {reason}")
    data = resp.json()
    
    df = pd.DataFrame(data["hourly"])
    df["latitude"] = lat
    df["longitude"] = lon
    return df


def main():
    parser = argparse.ArgumentParser(description="Fetch Open-Meteo historical grid data")
    parser.add_argument("--center_lat", type=float, required=True)
    parser.add_argument("--center_lon", type=float, required=True)
    parser.add_argument("--start_date", type=str, required=True, help="YYYY-MM-DD")
    parser.add_argument("--end_date", type=str, required=True, help="YYYY-MM-DD")
    parser.add_argument("--grid_size", type=int, default=5, help="NxN grid of pseudo-sensor points")
    parser.add_argument("--spacing_km", type=float, default=0.3, help="Spacing between grid points in km")
    parser.add_argument("--out", type=str, default="data/raw/weather_grid.csv")
    args = parser.parse_args()

    points = make_grid(args.center_lat, args.center_lon, args.grid_size, args.spacing_km)
    print(f"Fetching data for {len(points)} grid points from {args.start_date} to {args.end_date}...")

    all_dfs = []
    for lat, lon, node_id in points:
        try:
            df = fetch_point(lat, lon, args.start_date, args.end_date)
            df["node_id"] = node_id
            all_dfs.append(df)
            print(f"  fetched {node_id} ({lat}, {lon}) — {len(df)} rows")
        except requests.exceptions.RequestException as e:
            print(f"  failed for {node_id} ({lat}, {lon}): {e}")
        time.sleep(0.5)  # be polite to the free API

    if not all_dfs:
        raise RuntimeError("No data fetched — check your dates/coordinates and internet connection.")

    combined = pd.concat(all_dfs, ignore_index=True)
    combined.to_csv(args.out, index=False)
    print(f"\nSaved {len(combined)} rows to {args.out}")


if __name__ == "__main__":
    main()
