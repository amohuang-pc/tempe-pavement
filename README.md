# tempe-pavement

Data-side support for Simon's analysis of Tempe performance measure 1.22, Pavement Quality Index (Data4Good 2026, team Select * from ListChampion). The team's competition case is 1.31 Ending Opioid Overdoses (repo tempe-opioid); this repo validates and extends the 1.22 report at segment level.

## Layout
- data/raw        downloaded as-is from data.tempe.gov ArcGIS REST (01_download.py); not committed
- data/external   census tracts, ACS income and poverty, character areas, city boundary (copied from tempe-opioid)
- data/processed  segments_enriched.* (one row per segment, everything joined), gap list, tract table
- scripts         01_download.py, 02_definitions_check.py, 03_analysis.py (run in order from the repo root)
- outputs         definitions_check.md, analysis_tables.md, fig1 to fig5
- docs            data_inventory.md, definitions.md, findings_round1.md, review_memo_for_simon.md

## Reproduce
    pip install -r requirements.txt
    python scripts/01_download.py
    python scripts/02_definitions_check.py
    python scripts/03_analysis.py

## Sources
Pavement Quality Index Segments, 1.22 PQI Road Segment (detail), 1.22 PQI Average Citywide (summary), Planned Road Resurfacings: https://data.tempe.gov. Target wording: Tempe City Council Strategic Priorities and Performance Measures Index, Nov 2025. Unit costs: Crafco case study on Tempe (2022), to be confirmed with the City.
