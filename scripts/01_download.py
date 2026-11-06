"""
01_download.py
Pull every pavement-related layer from Tempe's ArcGIS REST services at row level
and save them under data/raw/. Run from the repo root:

    python scripts/01_download.py

Each layer caps responses at 2,000 records, so we page with resultOffset until
the server says there are no more rows. Geometry is requested as GeoJSON so the
polylines can be mapped later; the detail table has no geometry and is saved as CSV.
"""

import json
import time
from pathlib import Path

import requests

RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)

ORG = "https://services.arcgis.com/lQySeXwbBg53XWDi/arcgis/rest/services"

# name -> (query URL, has_geometry)
LAYERS = {
    "pqi_segments_current": (
        f"{ORG}/Pavement_Quality_Index_Segment/FeatureServer/7/query", True),
    "pqi_segment_detail": (
        f"{ORG}/1_22_PQI_Road_Segment_(detail)/FeatureServer/0/query", False),
    "planned_resurfacings": (
        f"{ORG}/Planned_Road_Resurfacings/FeatureServer/0/query", True),
    "traffic_count_segments": (
        "https://gis.tempe.gov/arcgis/rest/services/Open_Data/TrafficCountSegment/FeatureServer/0/query", True),
}

PAGE = 2000


def fetch_all(url: str, has_geometry: bool) -> list:
    """Return every feature from an ArcGIS layer by paging through it."""
    features = []
    offset = 0
    while True:
        params = {
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "true" if has_geometry else "false",
            "outSR": "4326",            # WGS84 lat/lon for mapping
            "f": "geojson" if has_geometry else "json",
            "resultOffset": offset,
            "resultRecordCount": PAGE,
        }
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        batch = data.get("features", [])
        features.extend(batch)
        print(f"  offset {offset}: {len(batch)} rows")
        # GeoJSON responses signal more pages with exceededTransferLimit in
        # properties; plain JSON uses the top-level key. Stop when the batch is short.
        if len(batch) < PAGE:
            break
        offset += PAGE
        time.sleep(0.5)       # be polite to the City's server
    return features


def save(name: str, features: list, has_geometry: bool) -> None:
    if has_geometry:
        out = RAW / f"{name}.geojson"
        out.write_text(json.dumps(
            {"type": "FeatureCollection", "features": features}))
    else:
        import csv
        rows = [f["attributes"] for f in features]
        out = RAW / f"{name}.csv"
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    print(f"  saved {out} ({len(features)} rows)")


if __name__ == "__main__":
    failed = []
    for name, (url, geom) in LAYERS.items():
        print(f"\n{name}")
        try:
            feats = fetch_all(url, geom)
        except Exception as exc:
            # Some City servers reject geojson output; retry once as plain json.
            print(f"  first attempt failed ({exc}); retrying without geojson")
            try:
                feats = fetch_all(url, False)
                geom = False
            except Exception as exc2:
                print(f"  SKIPPED: {exc2}")
                failed.append(name)
                continue
        save(name, feats, geom)

    # Citywide yearly summary (15 rows). Service name confirmed via the Hub search API.
    print("\npqi_citywide_summary")
    summary_url = f"{ORG}/1.22_PQI_Average_Citywide_(summary)_-_OD/FeatureServer/0/query"
    try:
        feats = fetch_all(summary_url, False)
        save("pqi_citywide_summary", feats, False)
    except Exception as exc:    # fall back to the hub CSV download
        print(f"  REST query failed ({exc}); downloading hub CSV instead")
        csv_url = ("https://data.tempe.gov/api/download/v1/items/"
                   "9048488c2150415b8c9d1ebf1861ebf9/csv?layers=0")
        try:
            r = requests.get(csv_url, timeout=60)
            r.raise_for_status()
            (RAW / "pqi_citywide_summary.csv").write_bytes(r.content)
            print("  saved data/raw/pqi_citywide_summary.csv")
        except Exception as exc2:
            print(f"  SKIPPED: {exc2}")
            failed.append("pqi_citywide_summary")

    print("\nDone. Expected row counts on 2026-10-19: current segments 5,127; "
          "detail 5,312; planned resurfacings 4,204; traffic 163 (gis.tempe.gov often returns 403); summary 15.")
    if failed:
        print(f"Layers not downloaded: {failed}")
