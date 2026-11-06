"""
02_definitions_check.py
Before any modelling, confirm what the data actually measures. This script
reads the raw downloads and answers the definition questions listed in
docs/definitions.md, then writes a report to outputs/definitions_check.md.

Run from the repo root after 01_download.py:

    python scripts/02_definitions_check.py

Questions answered:
  1. Which functional classes exist, and how many centerline miles and lane-miles each has.
  2. Which weighting of the segment PQI reproduces the official citywide average
     (simple mean per segment, centerline-mile weighted, or lane-mile weighted).
  3. Share of miles in the City's official bands (Poor <40, Fair 40-59, Good 60-79, Excellent 80+).
  4. Whether per_pqi_yr1 (map layer) equals CURRENT_PQI (detail table) on matched sections.
  5. Whether YEAR in the detail table is the inspection year (compare to PQI_DATE).
  6. Whether (MEASURED_PQI - CURRENT_PQI) / years is a fixed formula or varies by segment.
  7. Whether the planned-resurfacing layer double counts segments, and how many planned
     segments join to the current layer.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw")
OUT = Path("outputs")
OUT.mkdir(exist_ok=True)

lines = []          # report lines, written at the end


def say(text=""):
    print(text)
    lines.append(text)


def load_geojson_props(path: Path) -> pd.DataFrame:
    """Read only the attribute table of a GeoJSON file (no geometry needed here)."""
    data = json.loads(path.read_text())
    return pd.DataFrame([f["properties"] for f in data["features"]])


def norm_id(series: pd.Series) -> pd.Series:
    """Normalise section ids so '0000000060', '60', 60.0 all become '60'."""
    s = series.astype(str).str.strip()
    s = s.str.replace(r"\.0$", "", regex=True)
    s = s.str.lstrip("0")
    return s.replace("", "0")


# ---------------------------------------------------------------- 1. load
seg = load_geojson_props(RAW / "pqi_segments_current.geojson")
det = pd.read_csv(RAW / "pqi_segment_detail.csv")
plan = load_geojson_props(RAW / "planned_resurfacings.geojson")

summary_path = RAW / "pqi_citywide_summary.csv"      # written by 01_download.py
summary = pd.read_csv(summary_path) if summary_path.exists() else None

say("# Definitions check (run on the raw downloads)\n")
say(f"Rows: segments {len(seg):,}; detail {len(det):,}; planned {len(plan):,}; "
    f"summary {'n/a' if summary is None else len(summary)}\n")

# ---------------------------------------------------------------- 2. classes and mileage
seg["RM_MI"] = pd.to_numeric(seg["RM_MI"], errors="coerce")
seg["per_pqi_yr1"] = pd.to_numeric(seg["per_pqi_yr1"], errors="coerce")
# NOTE: the service aliases RM_NUM as "LaneCount", but its values (60 to 57,550)
# are the numeric form of RM_NO, the segment id. Lane counts come from the
# detail table's COUNT_ field instead (joined below on the section id).
seg["sid"] = norm_id(seg["section_number"])
det["sid"] = norm_id(det["SECTION_NUMBER"])
det["lanes"] = pd.to_numeric(det["COUNT_"] if "COUNT_" in det.columns else det["COUNT"], errors="coerce")
seg = seg.merge(det.drop_duplicates("sid")[["sid", "lanes"]], on="sid", how="left")
seg["lane_mi"] = seg["RM_MI"] * seg["lanes"]

say("## 1. Functional classes in the current layer\n")
by_class = (seg.groupby("rm_func", dropna=False)
            .agg(segments=("RM_MI", "size"),
                 centerline_mi=("RM_MI", "sum"),
                 lane_mi=("lane_mi", "sum"),
                 mean_pqi_simple=("per_pqi_yr1", "mean"))
            .sort_values("centerline_mi", ascending=False))
say(by_class.round(1).to_markdown())
say(f"\nTotal centerline miles: {seg['RM_MI'].sum():.1f}; "
    f"total lane-miles: {seg['lane_mi'].sum():.1f} "
    f"(City quoted 532 centerline / 1,241 lane-miles in 2022).")

# Does SegmentLength (feet) agree with RM_MI (miles)?
if "SegmentLength" in seg.columns:
    ft = pd.to_numeric(seg["SegmentLength"], errors="coerce")
    diff = (ft - seg["RM_MI"] * 5280).abs()
    say(f"SegmentLength vs RM_MI x 5280: median abs difference {diff.median():.1f} ft, "
        f"{(diff > 50).mean():.1%} of segments differ by more than 50 ft.\n")

# City-managed classes: drop anything that looks private or an alley.
mask_city = ~seg["rm_func"].fillna("").str.contains("private|alley", case=False)
city = seg[mask_city].copy()
say(f"Excluded as non-city (private/alley): {(~mask_city).sum()} segments, "
    f"{seg.loc[~mask_city, 'RM_MI'].sum():.1f} miles. "
    f"Remaining: {len(city):,} segments, {city['RM_MI'].sum():.1f} miles.\n")

# ---------------------------------------------------------------- 3. which average is official
say("## 2. Citywide average under three weightings\n")


def wavg(df, w):
    d = df.dropna(subset=["per_pqi_yr1", w])
    return np.average(d["per_pqi_yr1"], weights=d[w])


results = {
    "simple mean per segment (all classes)": seg["per_pqi_yr1"].mean(),
    "simple mean per segment (city classes)": city["per_pqi_yr1"].mean(),
    "centerline-mile weighted (city classes)": wavg(city, "RM_MI"),
    "lane-mile weighted (city classes)": wavg(city, "lane_mi"),
}
for k, v in results.items():
    say(f"- {k}: {v:.2f}")

official = None
if summary is not None:
    val_col = next((c for c in summary.columns if c.lower() == "metricvalue"), None)
    date_col = next((c for c in summary.columns if c.lower() == "asofdate"), None)
    if val_col:
        s = summary.copy()
        if date_col:
            s[date_col] = pd.to_datetime(s[date_col], errors="coerce")
            s = s.sort_values(date_col)
        say("\nOfficial summary table (last 5 rows):")
        say(s.tail(5).to_markdown(index=False))
        type_col = next((c for c in s.columns if c.lower() == "type"), None)
        if type_col:
            s = s[s[type_col].astype(str).str.upper() == "PQI"]      # drop the Target row
        official = pd.to_numeric(s[val_col], errors="coerce").dropna().iloc[-1]
say(f"\nLatest official citywide value: {official if official is not None else 'not downloaded'} "
    f"(the Oct 8 report cites 65 for end 2025 and the City expected 64 for June 2026).")
say("Reading: the weighting whose result is closest to the official value is the one to use. "
    "If none is within about 1 point, the City may include or exclude classes differently; "
    "ask the City (definitions.md question 7).\n")

# ---------------------------------------------------------------- 4. official bands
say("## 3. Share of centerline miles by the City's official bands (city classes)\n")
bands = pd.cut(city["per_pqi_yr1"], bins=[-1, 39.99, 59.99, 79.99, 100.01],
               labels=["Poor (0-39)", "Fair (40-59)", "Good (60-79)", "Excellent (80-100)"])
band_tab = city.groupby(bands, observed=False)["RM_MI"].sum()
band_tab = pd.DataFrame({"miles": band_tab, "share": band_tab / band_tab.sum()})
say(band_tab.round(3).to_markdown())
say("\nFor comparison with the Oct 8 report's custom bands:")
for cut in (40, 55, 70, 85):
    say(f"- share of miles below {cut}: {city.loc[city['per_pqi_yr1'] < cut, 'RM_MI'].sum() / city['RM_MI'].sum():.1%}")

# ---------------------------------------------------------------- 5. map layer vs detail table
say("\n## 4. Does per_pqi_yr1 (map) equal CURRENT_PQI (detail)?\n")
seg["sid"] = norm_id(seg["section_number"])
det["sid"] = norm_id(det["SECTION_NUMBER"])
for c in ("CURRENT_PQI", "MEASURED_PQI", "YEAR", "COUNT_", "COUNT", "LENGTH"):
    if c in det.columns:
        det[c] = pd.to_numeric(det[c], errors="coerce")
det["PQI_DATE"] = pd.to_datetime(det["PQI_DATE"], unit="ms", errors="coerce")   # ArcGIS dates are epoch ms

dup_det = det["sid"].duplicated().sum()
dup_seg = seg["sid"].duplicated().sum()
say(f"Duplicate ids: detail {dup_det}, map layer {dup_seg}.")
m = seg.merge(det.drop_duplicates("sid").drop(columns=["lanes"]), on="sid", how="left", suffixes=("", "_det"))
matched = m["CURRENT_PQI"].notna()
say(f"Map segments matched to a detail row: {matched.sum():,} of {len(seg):,} ({matched.mean():.1%}).")
if matched.any():
    d = (m.loc[matched, "per_pqi_yr1"] - m.loc[matched, "CURRENT_PQI"]).abs()
    say(f"per_pqi_yr1 vs CURRENT_PQI: exact (<0.05) for {(d < 0.05).mean():.1%} of matched rows; "
        f"median abs difference {d.median():.2f}; 90th percentile {d.quantile(0.9):.2f}.")
    d2 = (m.loc[matched, "per_pqi_yr1"] - m.loc[matched, "MEASURED_PQI"]).abs()
    say(f"per_pqi_yr1 vs MEASURED_PQI: exact for {(d2 < 0.05).mean():.1%}; median abs difference {d2.median():.2f}.")
    say("Reading: if per_pqi_yr1 matches CURRENT_PQI and not MEASURED_PQI, the map shows the "
        "modelled current-year score, not the inspection reading. If it matches neither, the map "
        "layer was re-modelled after the detail extract (map 2026-06, detail 2025-07).\n")

# ---------------------------------------------------------------- 6. YEAR vs PQI_DATE
say("## 5. Is YEAR the inspection year?\n")
yr_from_date = det["PQI_DATE"].dt.year
agree = (yr_from_date == det["YEAR"]).mean()
say(f"YEAR equals year(PQI_DATE) in {agree:.1%} of rows.")
say("Rows by YEAR:")
say(det["YEAR"].value_counts().sort_index().to_string())
say("\nPQI_DATE range: "
    f"{det['PQI_DATE'].min().date() if det['PQI_DATE'].notna().any() else 'n/a'} to "
    f"{det['PQI_DATE'].max().date() if det['PQI_DATE'].notna().any() else 'n/a'}\n")

# ---------------------------------------------------------------- 7. is the wear rate a formula
say("## 6. Is (MEASURED_PQI - CURRENT_PQI) / years a fixed formula?\n")
ref_year = 2025      # the detail extract date (2025-07-23) implies current = 2025
det["years_elapsed"] = ref_year - det["YEAR"]
ok = det["years_elapsed"] > 0
det.loc[ok, "annual_loss"] = (det.loc[ok, "MEASURED_PQI"] - det.loc[ok, "CURRENT_PQI"]) / det.loc[ok, "years_elapsed"]
g = (det[ok].groupby(["CLASS", "YEAR"])["annual_loss"]
     .agg(n="size", mean="mean", std="std", min="min", max="max")
     .round(2))
say(g.to_markdown())
say("\nReading: if std is near zero within a CLASS x YEAR group, the City's system applies one "
    "deterioration rate per group (a formula). If std is large, the system models each segment "
    "differently (for example by MEASURED_PQI level), and a per-segment curve can be fitted.")
# Is the loss a function of the starting score? Correlate within the largest group.
if ok.any():
    corr = det.loc[ok, ["MEASURED_PQI", "annual_loss"]].corr().iloc[0, 1]
    say(f"Correlation between MEASURED_PQI and annual_loss across all rows: {corr:.2f} "
        "(a strong value means the curve depends on the starting score).\n")

# ---------------------------------------------------------------- 8. planned layer
say("## 7. Planned Road Resurfacings: double counting and join rate\n")
plan["RM_NO"] = plan["RM_NO"].astype(str).str.strip()
seg["RM_NO"] = seg["RM_NO"].astype(str).str.strip()
say(f"Planned rows: {len(plan):,}; distinct RM_NO: {plan['RM_NO'].nunique():,} "
    f"(rows per id above 1 means a segment appears in more than one year or treatment).")
say("Rows per RM_NO:")
say(plan["RM_NO"].value_counts().value_counts().sort_index().to_string())
in_seg = plan["RM_NO"].isin(seg["RM_NO"])
say(f"\nPlanned RM_NO found in the current layer: {in_seg.mean():.1%}.")
pj = plan.merge(seg[["RM_NO", "RM_MI", "lane_mi", "rm_func", "per_pqi_yr1"]], on="RM_NO", how="left")
cat_col = "sql_treatment_category" if "sql_treatment_category" in pj.columns else "reh_select_fdesc"
tab = (pj.drop_duplicates(["RM_NO", "reh_iyear", cat_col])
       .groupby(["reh_iyear", cat_col])
       .agg(segments=("RM_NO", "nunique"), centerline_mi=("RM_MI", "sum"),
            lane_mi=("lane_mi", "sum"), mean_pqi_now=("per_pqi_yr1", "mean"))
       .round(1))
say("\nPlanned work by fiscal year and treatment category (distinct segments, miles from the "
    "current layer, so no double counting of divided roads):")
say(tab.to_markdown())
say("\nTreatment descriptions present (reh_select_fdesc):")
say(plan["reh_select_fdesc"].value_counts().to_string())

# ---------------------------------------------------------------- write
(OUT / "definitions_check.md").write_text("\n".join(lines), encoding="utf-8")
print(f"\nReport written to {OUT / 'definitions_check.md'}")
