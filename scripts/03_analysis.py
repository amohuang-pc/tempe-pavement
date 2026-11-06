"""
03_analysis.py
Segment-level analysis of Tempe measure 1.22 (Pavement Quality Index).
Rebuilds the Oct 8 report's models from the 5,127 road segments instead of
grouped averages, and adds the pieces the report did not have: observed
treatment effects, planned-program coverage, equity by census tract, maps.

Run from the repo root after 01_download.py:

    python scripts/03_analysis.py

Inputs (data/raw, from 01_download.py; data/external, copied from the opioid repo):
  pqi_segments_current.geojson   current map layer, per_pqi_yr1 = City's current modelled PQI
  pqi_segment_detail.csv         inspection table: MEASURED_PQI on PQI_DATE, CURRENT_PQI, lanes
  planned_resurfacings.geojson   FY2025-2028 planned treatments by RM_NO
  pqi_citywide_summary.csv       official yearly citywide PQI
  census_tracts.geojson, tracts_income_2019_2023.geojson, tracts_poverty_2019_2023.geojson,
  character_areas.geojson, city_boundary.geojson

Outputs:
  data/processed/segments_enriched.geojson   one row per segment with everything joined
  data/processed/segments_enriched.csv       same without geometry
  outputs/analysis_tables.md                 every table below
  outputs/fig*.png                           figures
"""

import json
import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

RAW, EXT, PROC, OUT = Path("data/raw"), Path("data/external"), Path("data/processed"), Path("outputs")
PROC.mkdir(parents=True, exist_ok=True)
OUT.mkdir(exist_ok=True)

# Official condition bands from the City's own map renderer.
BANDS = [-1, 39.99, 59.99, 79.99, 100.01]
BAND_LABELS = ["Poor (0-39)", "Fair (40-59)", "Good (60-79)", "Excellent (80-100)"]
# One-hue ordinal ramp, darkest = Poor so the problem band carries the most ink.
BAND_COLORS = {"Poor (0-39)": "#0d366b", "Fair (40-59)": "#2a78d6",
               "Good (60-79)": "#6da7ec", "Excellent (80-100)": "#b7d3f6"}
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#898781", "#e1e0d9", "#fcfcfb"
plt.rcParams.update({"font.family": "sans-serif", "axes.edgecolor": "#c3c2b7",
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE})

lines = []


def say(text=""):
    print(text)
    lines.append(text)


def md(df, **kw):
    say(df.to_markdown(**kw))
    say()


def norm_id(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.lstrip("0")
    return s.replace("", "0")


def wavg(df, col, w):
    d = df.dropna(subset=[col, w])
    return float(np.average(d[col], weights=d[w])) if len(d) else np.nan


def band(x):
    return pd.cut(x, bins=BANDS, labels=BAND_LABELS)


# ====================================================================== load and join
seg = gpd.read_file(RAW / "pqi_segments_current.geojson").to_crs(4326)
det = pd.read_csv(RAW / "pqi_segment_detail.csv")
plan = gpd.read_file(RAW / "planned_resurfacings.geojson")
summary = pd.read_csv(RAW / "pqi_citywide_summary.csv")

seg["sid"] = norm_id(seg["section_number"])
det["sid"] = norm_id(det["SECTION_NUMBER"])
plan["sid"] = norm_id(plan["RM_NO"])

det["lanes"] = pd.to_numeric(det["COUNT_"], errors="coerce")
det["PQI_DATE"] = pd.to_datetime(det["PQI_DATE"], unit="ms", errors="coerce")
det["insp_year"] = det["YEAR"].astype("Int64")
det = det.drop_duplicates("sid")

seg = seg.merge(det[["sid", "lanes", "MEASURED_PQI", "CURRENT_PQI", "PQI_DATE", "insp_year", "CLASS"]],
                on="sid", how="left")
seg["pqi_now"] = pd.to_numeric(seg["per_pqi_yr1"], errors="coerce")
seg["miles"] = pd.to_numeric(seg["RM_MI"], errors="coerce")
seg["lane_mi"] = seg["miles"] * seg["lanes"]
seg["func"] = seg["rm_func"].fillna("Unknown")
seg["is_city"] = ~seg["func"].str.contains("private|alley", case=False)
seg["band_now"] = band(seg["pqi_now"])

# Planned treatment: one row per segment (keep the earliest fiscal year if several).
pl = (plan.sort_values("reh_iyear")
      .drop_duplicates("sid")[["sid", "reh_iyear", "sql_treatment_category", "reh_select_fdesc"]]
      .rename(columns={"reh_iyear": "plan_fy", "sql_treatment_category": "plan_cat",
                       "reh_select_fdesc": "plan_desc"}))
seg = seg.merge(pl, on="sid", how="left")
seg["plan_fy"] = seg["plan_fy"].astype("Int64")

# Treatment families: group the 13 descriptions into 3 families used in costing.
FAMILY = {"MILL_OL": "Mill and overlay", "MILL_MICRO": "Mill and overlay", "RECONSTRUCTION": "Reconstruction",
          "SEAL_COAT": "Surface seal", "SLURRY": "Surface seal", "CAPE": "Surface seal", "REJV_FOG": "Surface seal"}
seg["plan_family"] = seg["plan_cat"].map(FAMILY)

# Census tracts and ACS (spatial join on segment midpoint, so each segment lands in one tract).
tracts = gpd.read_file(EXT / "census_tracts.geojson").to_crs(4326)[["GEOID", "NAME", "geometry"]]
inc = gpd.read_file(EXT / "tracts_income_2019_2023.geojson")
inc = inc[["GEOID", "Households_Median_income__dolla", "Households_Total"]].rename(
    columns={"Households_Median_income__dolla": "median_hh_income", "Households_Total": "households"})
inc["GEOID"] = inc["GEOID"].astype(str)
# ACS exports income as text ("250,000+", "-"); keep the numeric part.
inc["median_hh_income"] = pd.to_numeric(inc["median_hh_income"].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
inc["households"] = pd.to_numeric(inc["households"], errors="coerce")
pov = gpd.read_file(EXT / "tracts_poverty_2019_2023.geojson")
pov = pov[["NAME", "B17020_calc_pctPovE"]].rename(columns={"B17020_calc_pctPovE": "pct_poverty"})
pov["pct_poverty"] = pd.to_numeric(pov["pct_poverty"], errors="coerce")
tracts["GEOID"] = tracts["GEOID"].astype(str)
tracts = tracts.merge(inc, on="GEOID", how="left").merge(pov, on="NAME", how="left")

mid = seg.copy()
mid["geometry"] = mid.geometry.interpolate(0.5, normalized=True)
mid = gpd.sjoin(mid[["sid", "geometry"]], tracts, how="left", predicate="within").drop(columns="index_right")
mid = mid.drop_duplicates("sid")
seg = seg.merge(mid[["sid", "GEOID", "NAME", "median_hh_income", "households", "pct_poverty"]], on="sid", how="left")

# Character areas (the City's eight planning areas).
areas = gpd.read_file(EXT / "character_areas.geojson").to_crs(4326)[["area_name", "geometry"]]
mid2 = seg.copy()
mid2["geometry"] = mid2.geometry.interpolate(0.5, normalized=True)
mid2 = gpd.sjoin(mid2[["sid", "geometry"]], areas, how="left", predicate="within").drop_duplicates("sid")
seg = seg.merge(mid2[["sid", "area_name"]], on="sid", how="left")

city = seg[seg["is_city"]].copy()
say("# 1.22 PQI segment-level analysis\n")
say(f"Segments: {len(seg):,} total, {len(city):,} city-maintained ({city['miles'].sum():.1f} centerline miles, "
    f"{city['lane_mi'].sum():.0f} lane-miles). Segments matched to a tract: {seg['GEOID'].notna().mean():.1%}; "
    f"to a character area: {seg['area_name'].notna().mean():.1%}.\n")

# ====================================================================== A. network state
say("## A. Network state (June 2026 snapshot, City's current modelled PQI)\n")
say("Citywide averages under each weighting (city-maintained segments):")
say(f"- simple mean per segment: {city['pqi_now'].mean():.1f}")
say(f"- centerline-mile weighted: {wavg(city, 'pqi_now', 'miles'):.1f}")
say(f"- lane-mile weighted: {wavg(city, 'pqi_now', 'lane_mi'):.1f}")
say(f"- official 1.22 value for 2025: {summary.loc[summary['Type'] == 'PQI', 'metricValue'].iloc[-1]}")
# Which weighting reproduces the official 65 from the July 2025 extract?
say("\nSame three weightings on the July 2025 detail extract (CURRENT_PQI), which is the dataset the measure page publishes:")
c25 = city.dropna(subset=["CURRENT_PQI"])
say(f"- simple mean: {c25['CURRENT_PQI'].mean():.1f}; centerline-weighted: {wavg(c25, 'CURRENT_PQI', 'miles'):.1f}; "
    f"lane-mile weighted: {wavg(c25, 'CURRENT_PQI', 'lane_mi'):.1f}")
say("Reading: the lane-mile weighted mean of the published 2025 table rounds to the official 65; the other two do not. "
    "Working hypothesis (to confirm with the City): measure 1.22 is a lane-mile weighted average.\n")

tab = (city.groupby("func")
       .agg(segments=("sid", "size"), centerline_mi=("miles", "sum"), lane_mi=("lane_mi", "sum"),
            pqi_lane_weighted=("pqi_now", lambda s: wavg(city.loc[s.index], "pqi_now", "lane_mi")),
            share_poor_lane_mi=("pqi_now", lambda s: city.loc[s.index].loc[s < 40, "lane_mi"].sum() / city.loc[s.index, "lane_mi"].sum()))
       .sort_values("lane_mi", ascending=False).round(2))
say("By functional class:")
md(tab)

bt = city.groupby("band_now", observed=False).agg(segments=("sid", "size"), centerline_mi=("miles", "sum"), lane_mi=("lane_mi", "sum"))
bt["share_centerline"] = bt["centerline_mi"] / bt["centerline_mi"].sum()
bt["share_lane_mi"] = bt["lane_mi"] / bt["lane_mi"].sum()
say("By official condition band:")
md(bt.round(3))

# Figure 1: miles by band and class (stacked horizontal bars)
fig, ax = plt.subplots(figsize=(8, 3.6))
piv = city.pivot_table(index="func", columns="band_now", values="lane_mi", aggfunc="sum", observed=False).fillna(0)
piv = piv.loc[piv.sum(axis=1).sort_values().index]
left = np.zeros(len(piv))
for b in BAND_LABELS:
    ax.barh(piv.index, piv[b], left=left, color=BAND_COLORS[b], label=b, height=0.55, edgecolor=SURFACE, linewidth=2)
    left += piv[b].values
ax.set_xlabel("Lane-miles")
ax.set_title("Tempe pavement condition by class, June 2026 (official PQI bands)", loc="left", fontsize=11, color=INK, pad=22)
ax.legend(frameon=False, fontsize=8, ncol=4, loc="lower left", bbox_to_anchor=(0, 1.0))
ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
fig.text(0.01, -0.02, "Source: Pavement Quality Index Segments (data.tempe.gov, snapshot 2026-06-03); lanes from 1.22 PQI Road Segment (detail).",
         fontsize=7, color=MUTED)
fig.tight_layout(); fig.savefig(OUT / "fig1_condition_by_class.png", dpi=180, bbox_inches="tight"); plt.close(fig)

# ====================================================================== B. deterioration
say("## B. Deterioration implied by the City's own model\n")
say("For each segment the detail table carries the inspection reading (MEASURED_PQI on PQI_DATE) and the "
    "modelled value as of the July 2025 extract (CURRENT_PQI). The difference per year is the City's deterioration "
    "assumption for that segment. It is a model, not an observation, because only one inspection cycle is published.\n")
d = city.dropna(subset=["MEASURED_PQI", "CURRENT_PQI", "insp_year"]).copy()
d["years"] = 2025 - d["insp_year"].astype(int)
d = d[d["years"] > 0]
d["loss_per_year"] = (d["MEASURED_PQI"] - d["CURRENT_PQI"]) / d["years"]
d["band_measured"] = band(d["MEASURED_PQI"])
say(f"Segments with at least one modelled year: {len(d):,}. Inspection years in the table: "
    f"{det['insp_year'].value_counts().sort_index().to_dict()} (a rolling survey, roughly a third of the network per year).\n")
say("Loss per year by class (lane-mile weighted mean, with spread):")
md(d.groupby("func").apply(lambda g: pd.Series({
    "segments": len(g), "mean": wavg(g, "loss_per_year", "lane_mi"),
    "p10": g["loss_per_year"].quantile(0.1), "median": g["loss_per_year"].median(),
    "p90": g["loss_per_year"].quantile(0.9)})).round(2))
say("Loss per year by the segment's measured condition band:")
md(d.groupby("band_measured", observed=False).apply(lambda g: pd.Series({
    "segments": len(g), "mean": wavg(g, "loss_per_year", "lane_mi"), "median": g["loss_per_year"].median(),
    "p90": g["loss_per_year"].quantile(0.9)})).round(2))
say("Reading: the Oct 8 report's flat 3 points per year is close to the network mean, but the City's curve is steeper "
    "for segments already in Fair or Poor and flatter for Excellent segments. A projection that uses one rate for "
    "all segments will understate how fast the bad roads get worse and overstate how fast good roads decline.\n")
LOSS_BY_BAND = d.groupby("band_measured", observed=False)["loss_per_year"].median().to_dict()

# ====================================================================== C. treatment effect
say("## C. Treatment effect observed on FY2025 work\n")
say("Segments planned for FY2025 (July 2024 to June 2025) show a different value on the June 2026 map than in the "
    "July 2025 table, and no other segments do. So the map was updated after the FY2025 work was accepted. "
    "Comparing the pre-work inspection reading with the post-work map value gives the City's own post-treatment score.\n")
f25 = city[city["plan_fy"] == 2025].copy()
f25["changed"] = (f25["pqi_now"] - f25["CURRENT_PQI"]).abs() > 0.05
f25["gain_vs_measured"] = f25["pqi_now"] - f25["MEASURED_PQI"]
tc = f25.groupby("plan_cat").apply(lambda g: pd.Series({
    "segments": len(g), "lane_mi": g["lane_mi"].sum(), "share_updated": g["changed"].mean(),
    "pre_measured_median": g["MEASURED_PQI"].median(), "post_map_median": g["pqi_now"].median(),
    "gain_median_updated_only": g.loc[g["changed"], "gain_vs_measured"].median(),
    "post_map_median_updated_only": g.loc[g["changed"], "pqi_now"].median()})).round(1)
md(tc)
ov_post = tc.loc["MILL_OL", "post_map_median_updated_only"] if "MILL_OL" in tc.index else np.nan
sc_gain = tc.loc["SEAL_COAT", "gain_median_updated_only"] if "SEAL_COAT" in tc.index else np.nan
sc_upd = tc.loc["SEAL_COAT", "share_updated"] if "SEAL_COAT" in tc.index else np.nan
say(f"Reading: mill and overlay resets a segment to about {ov_post:.0f} (the Oct 8 report assumed 95: confirmed). "
    f"Seal coats on updated segments gain a median {sc_gain:.0f} points (the report assumed 10), but only {sc_upd:.0%} of "
    f"FY2025 seal-coat segments were updated at all; the rest may be unrecorded or RoadMatrix may treat a seal as a "
    f"life extension rather than a score jump. Micro-mill segments were already in the mid-90s at inspection, so their "
    f"effect cannot be read here. Confirm both points with the City (interview question 2).\n")
TREAT_POST = {"Mill and overlay": float(tc.loc[tc.index.isin(["MILL_OL", "MILL_MICRO"]), "post_map_median_updated_only"].mean()),
              "Reconstruction": 98.0}
SEAL_GAIN = float(tc.loc[tc.index.isin(["SEAL_COAT", "SLURRY"]), "gain_median_updated_only"].mean())

# ====================================================================== D. planned program
say("## D. Planned program FY2026 to FY2028 against today's condition\n")
fut = city[city["plan_fy"] >= 2026]
say(f"Planned segments FY2026-2028: {len(fut):,} ({fut['miles'].sum():.1f} centerline miles, {fut['lane_mi'].sum():.0f} lane-miles), "
    f"{fut['lane_mi'].sum() / city['lane_mi'].sum():.0%} of city lane-miles. The City calls this a tentative schedule that "
    f"depends on a funding plan not yet approved.\n")
md(fut.groupby(["plan_fy", "plan_family"]).agg(segments=("sid", "size"), centerline_mi=("miles", "sum"),
                                                lane_mi=("lane_mi", "sum"), pqi_now_median=("pqi_now", "median")).round(1))
say("Does the plan reach the roads that need it? Current band of city lane-miles by plan status:")
pf = city["plan_fy"].astype(float).fillna(0).to_numpy()
city["plan_status"] = np.where(pf == 2025, "Done FY2025", np.where(pf >= 2026, "Planned FY2026-28", "No plan"))
cov = city.pivot_table(index="band_now", columns="plan_status", values="lane_mi", aggfunc="sum", observed=False).fillna(0)
cov["total"] = cov.sum(axis=1)
cov["share_unplanned"] = cov["No plan"] / cov["total"]
md(cov.round(1))
gap = city[(city["plan_status"] == "No plan") & (city["pqi_now"] < 60)]
say(f"Gap list: {len(gap):,} segments, {gap['miles'].sum():.1f} centerline miles, {gap['lane_mi'].sum():.0f} lane-miles are "
    f"Poor or Fair today with no planned treatment through FY2028. By class:")
md(gap.groupby("func").agg(segments=("sid", "size"), lane_mi=("lane_mi", "sum"), pqi_median=("pqi_now", "median")).round(1))
gap.sort_values("pqi_now")[["RM_STREET", "RM_FROM", "RM_TO", "func", "pqi_now", "miles", "lanes", "lane_mi", "area_name", "NAME"]] \
   .to_csv(PROC / "gap_segments_no_plan_below60.csv", index=False)
say(f"Full gap list written to data/processed/gap_segments_no_plan_below60.csv.\n")

# ====================================================================== E. equity
say("## E. Equity: condition by census tract income (the measure's own clause)\n")
say("The target reads 'a citywide average of 70 across all demographic categories'. Tract median household income "
    "(ACS 2019-2023) is used as the available proxy; race and ethnicity tables can be added with the same join.\n")
e = city.dropna(subset=["median_hh_income", "lane_mi", "pqi_now"]).copy()
e["income_q"] = pd.qcut(e["median_hh_income"], 4, labels=["Q1 lowest income", "Q2", "Q3", "Q4 highest income"])
eq = e.groupby("income_q", observed=False).apply(lambda g: pd.Series({
    "tracts": g["GEOID"].nunique(), "lane_mi": g["lane_mi"].sum(),
    "income_range": f"${g['median_hh_income'].min():,.0f} to ${g['median_hh_income'].max():,.0f}",
    "pqi_lane_weighted": wavg(g, "pqi_now", "lane_mi"),
    "share_poor": g.loc[g["pqi_now"] < 40, "lane_mi"].sum() / g["lane_mi"].sum(),
    "share_poor_or_fair": g.loc[g["pqi_now"] < 60, "lane_mi"].sum() / g["lane_mi"].sum(),
    "share_planned_fy26_28": g.loc[g["plan_fy"] >= 2026, "lane_mi"].sum() / g["lane_mi"].sum(),
    "share_poor_fair_unplanned": g.loc[(g["pqi_now"] < 60) & (g["plan_status"] == "No plan"), "lane_mi"].sum()
                                  / max(g.loc[g["pqi_now"] < 60, "lane_mi"].sum(), 1e-9)}))
md(eq.round(3))
# per-tract table
tr = e.groupby(["GEOID", "NAME"]).apply(lambda g: pd.Series({
    "median_hh_income": g["median_hh_income"].iloc[0], "pct_poverty": g["pct_poverty"].iloc[0],
    "lane_mi": g["lane_mi"].sum(), "pqi_lane_weighted": wavg(g, "pqi_now", "lane_mi"),
    "share_poor_or_fair": g.loc[g["pqi_now"] < 60, "lane_mi"].sum() / g["lane_mi"].sum(),
    "share_planned_fy26_28": g.loc[g["plan_fy"] >= 2026, "lane_mi"].sum() / g["lane_mi"].sum()})).reset_index()
tr.to_csv(PROC / "tract_pqi_equity.csv", index=False)
say(f"Tracts below the 70 target today (lane-mile weighted): {(tr['pqi_lane_weighted'] < 70).sum()} of {len(tr)}. "
    f"Lowest five:")
md(tr.sort_values("pqi_lane_weighted").head(5)[["NAME", "median_hh_income", "lane_mi", "pqi_lane_weighted", "share_poor_or_fair", "share_planned_fy26_28"]].round(2), index=False)
corr = tr[["median_hh_income", "pqi_lane_weighted"]].corr().iloc[0, 1]
say(f"Correlation between tract income and tract PQI across {len(tr)} tracts: {corr:.2f}.\n")
say("Character areas (the City's eight planning areas):")
md(city.dropna(subset=["area_name"]).groupby("area_name").apply(lambda g: pd.Series({
    "lane_mi": g["lane_mi"].sum(), "pqi_lane_weighted": wavg(g, "pqi_now", "lane_mi"),
    "share_poor_or_fair": g.loc[g["pqi_now"] < 60, "lane_mi"].sum() / g["lane_mi"].sum(),
    "share_planned_fy26_28": g.loc[g["plan_fy"] >= 2026, "lane_mi"].sum() / g["lane_mi"].sum()})).round(2).sort_values("pqi_lane_weighted"))

# Figure 2: equity bars
fig, ax = plt.subplots(figsize=(7, 3.2))
x = np.arange(len(eq))
ax.bar(x, eq["pqi_lane_weighted"], color="#2a78d6", width=0.55)
ax.axhline(70, color="#d03b3b", linewidth=1.2, linestyle="--")
ax.text(len(eq) - 0.5, 70.6, "target 70", color="#d03b3b", fontsize=8, ha="right")
for i, v in enumerate(eq["pqi_lane_weighted"]):
    ax.text(i, v + 0.8, f"{v:.1f}", ha="center", fontsize=9, color=INK)
ax.set_xticks(x); ax.set_xticklabels(eq.index, fontsize=9)
ax.set_ylim(0, 100); ax.set_ylabel("Lane-mile weighted PQI")
ax.set_title("Pavement condition by tract income quartile, June 2026", loc="left", fontsize=11, color=INK)
ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
fig.text(0.01, -0.03, "Source: PQI Segments joined to ACS 2019-2023 tract median household income at segment midpoints.", fontsize=7, color=MUTED)
fig.tight_layout(); fig.savefig(OUT / "fig2_equity_income_quartile.png", dpi=180, bbox_inches="tight"); plt.close(fig)

# ====================================================================== F. projection (Model C at segment level)
say("## F. Projection to FY2036 at segment level\n")
say("Rules: each segment loses the City's median rate for its current band each year (section B). Segments planned for "
    "FY2026-2028 are treated in their planned year: mill and overlay or reconstruction resets to the observed post-work "
    "score (section C); a surface seal adds the observed seal gain and holds the segment at its current score for the "
    "seal's life (3 years, assumption). After FY2028 three scenarios: no further work; a preservation-only program that "
    "seals every segment that drops into Fair; and a continued program that also overlays every segment that drops into Poor.\n")

LOSS = {b: max(LOSS_BY_BAND.get(b, 3.0), 0.5) for b in BAND_LABELS}
SEAL_LIFE = 3
OVERLAY_POST = TREAT_POST["Mill and overlay"]


def project(df, scenario, horizon=2036, loss_rule="city_bands", last_plan_year=2028):
    """last_plan_year: planned work after this fiscal year is assumed not funded (sensitivity)."""
    """loss_rule: 'city_bands' uses the median loss per official band from section B;
    'report_two_tier' uses the Oct 8 report's rule (1 point/yr at 85 and above, 3 below)."""
    pqi = df["pqi_now"].to_numpy(dtype=float).copy()
    w = df["lane_mi"].fillna(0).to_numpy()
    plan_fy = df["plan_fy"].astype(float).to_numpy()
    plan_fy = np.where(plan_fy > last_plan_year, np.nan, plan_fy)
    fam = df["plan_family"].to_numpy()
    seal_hold = np.zeros(len(df))
    rows = [{"year": 2026, "avg": np.average(pqi, weights=w),
             "share_poor": w[pqi < 40].sum() / w.sum(), "overlay_lane_mi": 0.0, "seal_lane_mi": 0.0,
             "note": "June 2026 snapshot, FY2026 work not yet recorded"}]
    # FY2026 (July 2025 to June 2026) work is finished but not yet in the June 2026 map
    # (section C shows only FY2025 segments were updated), so apply it first.
    m_ov = (plan_fy == 2026) & np.isin(fam, ["Mill and overlay", "Reconstruction"])
    m_se = (plan_fy == 2026) & (fam == "Surface seal")
    pqi[m_ov] = OVERLAY_POST
    pqi[m_se] = np.minimum(pqi[m_se] + SEAL_GAIN, 100); seal_hold[m_se] = SEAL_LIFE
    rows.append({"year": 2026.5, "avg": np.average(pqi, weights=w), "share_poor": w[pqi < 40].sum() / w.sum(),
                 "overlay_lane_mi": w[m_ov].sum(), "seal_lane_mi": w[m_se].sum(), "note": "after FY2026 work"})
    for yr in range(2027, horizon + 1):
        # deterioration
        if loss_rule == "report_two_tier":
            loss = np.where(pqi >= 85, 1.0, 3.0)
        else:
            b = pd.cut(pqi, bins=BANDS, labels=BAND_LABELS).astype(str)
            loss = np.array([LOSS.get(x, 3.0) for x in b])
        loss[seal_hold > 0] = 0
        pqi = np.clip(pqi - loss, 0, 100)
        seal_hold = np.maximum(seal_hold - 1, 0)
        ov = se = 0.0
        # planned work (fiscal year labelled by ending year; FY2027 work shows in the 2027 snapshot)
        m_ov = (plan_fy == yr) & np.isin(fam, ["Mill and overlay", "Reconstruction"])
        m_se = (plan_fy == yr) & (fam == "Surface seal")
        pqi[m_ov] = OVERLAY_POST; ov += w[m_ov].sum()
        pqi[m_se] = np.minimum(pqi[m_se] + SEAL_GAIN, 100); seal_hold[m_se] = SEAL_LIFE; se += w[m_se].sum()
        if yr > 2028 and scenario in ("preserve", "continue"):
            m = (pqi >= 40) & (pqi < 60) & (seal_hold == 0)
            pqi[m] = np.minimum(pqi[m] + SEAL_GAIN, 100); seal_hold[m] = SEAL_LIFE; se += w[m].sum()
        if yr > 2028 and scenario == "continue":
            m = pqi < 40
            pqi[m] = OVERLAY_POST; ov += w[m].sum()
        rows.append({"year": yr, "avg": np.average(pqi, weights=w), "share_poor": w[pqi < 40].sum() / w.sum(),
                     "overlay_lane_mi": ov, "seal_lane_mi": se, "note": ""})
    return pd.DataFrame(rows)


scen = {s: project(city, s) for s in ("stop", "preserve", "continue")}
# Sensitivity: the Oct 8 report's two-tier rule (1 point/yr at 85+, 3 below).
flat_stop = project(city, "stop", loss_rule="report_two_tier")
flat_pres = project(city, "preserve", loss_rule="report_two_tier")
# Sensitivity: the FY2028 tranche of the tentative plan is never funded.
cut_stop = project(city, "stop", last_plan_year=2027)
tabF = pd.DataFrame({"year": scen["stop"]["year"],
                     "stop after FY2028": scen["stop"]["avg"],
                     "preserve (seal Fair)": scen["preserve"]["avg"],
                     "continue (seal Fair + overlay Poor)": scen["continue"]["avg"],
                     "share Poor, stop": scen["stop"]["share_poor"],
                     "share Poor, continue": scen["continue"]["share_poor"]}).round(3)
tabF["stop, two-tier 1/3 pts (Oct 8 rule)"] = flat_stop["avg"].round(3)
tabF["preserve, two-tier 1/3 pts"] = flat_pres["avg"].round(3)
tabF["stop, FY2028 tranche unfunded"] = cut_stop["avg"].round(3)
md(tabF, index=False)
yr_below = tabF.loc[(tabF["year"] > 2028) & (tabF["stop after FY2028"] < 70), "year"]
yr_below_flat = tabF.loc[(tabF["year"] > 2028) & (tabF["stop, two-tier 1/3 pts (Oct 8 rule)"] < 70), "year"]
yr_below_cut = tabF.loc[(tabF["year"] > 2028) & (tabF["stop, FY2028 tranche unfunded"] < 70), "year"]
say(f"If the FY2028 tranche of the plan is never funded and nothing follows: 2036 value "
    f"{tabF['stop, FY2028 tranche unfunded'].iloc[-1]:.1f}, below 70 from "
    f"{'not before 2036' if yr_below_cut.empty else int(yr_below_cut.iloc[0])}.")
say(f"Year the citywide average falls below 70 with no work after FY2028: "
    f"{'not before 2036' if yr_below.empty else int(yr_below.iloc[0])} under the City's band-specific curve; "
    f"{'not before 2036' if yr_below_flat.empty else int(yr_below_flat.iloc[0])} under the Oct 8 report's two-tier rule (1 point a year at 85 and above, 3 below). "
    f"The conclusion about post-bond funding depends on which deterioration curve is right, so this is the first "
    f"thing to confirm with the City.\n")
# Cost of the continue scenario at Tempe's own unit prices (per lane-mile, 2022 RoadMatrix curve)
UNIT = {"seal": 20_000, "overlay": 50_000}
c = scen["continue"]; p = scen["preserve"]
post = c[c["year"] > 2028]
say(f"Post-FY2028 work in the 'continue' scenario, FY2029-2036: {post['overlay_lane_mi'].sum():.0f} lane-miles overlay and "
    f"{post['seal_lane_mi'].sum():.0f} lane-miles seal, about ${(post['overlay_lane_mi'].sum() * UNIT['overlay'] + post['seal_lane_mi'].sum() * UNIT['seal']) / 1e6:.0f}M "
    f"over eight years at Tempe's 2022 unit costs ($50k overlay, $20k maintenance per lane-mile), roughly "
    f"${(post['overlay_lane_mi'].sum() * UNIT['overlay'] + post['seal_lane_mi'].sum() * UNIT['seal']) / 8e6:.0f}M a year. "
    f"'Preserve' alone: {p[p['year'] > 2028]['seal_lane_mi'].sum():.0f} lane-miles seal, about ${p[p['year'] > 2028]['seal_lane_mi'].sum() * UNIT['seal'] / 8e6:.1f}M a year.\n")
say("Reading: the bond program lifts the network above 70 by FY2028 in every scenario; what happens after decides "
    "whether 70 holds to FY2036. Unit costs are from a 2022 vendor publication quoting the City's own curve and must be "
    "confirmed; the seal gain is the small observed value, so the 'preserve' line is conservative.\n")

# Figure 3: projection lines
fig, ax = plt.subplots(figsize=(7.5, 3.6))
cols = {"stop after FY2028": "#e34948", "preserve (seal Fair)": "#eda100", "continue (seal Fair + overlay Poor)": "#2a78d6"}
for k, col in cols.items():
    ax.plot(tabF["year"], tabF[k], color=col, linewidth=2, label=k)
    ax.text(tabF["year"].iloc[-1] + 0.15, tabF[k].iloc[-1], f"{tabF[k].iloc[-1]:.0f}", color=INK, fontsize=9, va="center")
ax.plot(tabF["year"], tabF["stop, two-tier 1/3 pts (Oct 8 rule)"], color=MUTED, linewidth=1.5, linestyle=":",
        label="stop, Oct 8 report wear rule (1/yr at 85+, 3 below)")
ax.text(tabF["year"].iloc[-1] + 0.15, tabF["stop, two-tier 1/3 pts (Oct 8 rule)"].iloc[-1],
        f"{tabF['stop, two-tier 1/3 pts (Oct 8 rule)'].iloc[-1]:.0f}", color=MUTED, fontsize=9, va="center")
ax.axhline(70, color=MUTED, linewidth=1, linestyle="--"); ax.text(2029.6, 70.8, "target 70", color=MUTED, fontsize=8)
ax.axvspan(2026, 2028.5, color=GRID, alpha=0.5, lw=0); ax.text(2026.1, 88.3, "bond program FY2026-28", fontsize=8, color=MUTED)
ax.set_xticks(range(2026, 2037)); ax.set_xticklabels([str(y) for y in range(2026, 2037)], fontsize=8)
ax.set_ylim(40, 90); ax.set_xlim(2026, 2037); ax.set_ylabel("Lane-mile weighted PQI")
ax.set_title("Citywide PQI to FY2036 under three post-bond scenarios", loc="left", fontsize=11, color=INK)
ax.legend(frameon=False, fontsize=8, loc="lower right"); ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
fig.text(0.01, -0.03, "Segment-level simulation; deterioration and treatment effects from the City's own data (sections B, C). Illustrative.", fontsize=7, color=MUTED)
fig.tight_layout(); fig.savefig(OUT / "fig3_projection_scenarios.png", dpi=180, bbox_inches="tight"); plt.close(fig)

# ====================================================================== G. maps
boundary = gpd.read_file(EXT / "city_boundary.geojson").to_crs(4326)
fig, ax = plt.subplots(figsize=(7, 8))
boundary.boundary.plot(ax=ax, color=MUTED, linewidth=0.8)
for b in BAND_LABELS[::-1]:
    city[city["band_now"] == b].plot(ax=ax, color=BAND_COLORS[b], linewidth=1.1 if b.startswith("Poor") else 0.7, label=b)
ax.set_axis_off(); ax.set_title("Pavement condition by segment, June 2026 (official PQI bands)", loc="left", fontsize=11, color=INK)
ax.legend(frameon=False, fontsize=8, loc="upper left")
fig.text(0.01, 0.01, "Source: Pavement Quality Index Segments, data.tempe.gov (2026-06-03). City boundary from data.tempe.gov.", fontsize=7, color=MUTED)
fig.tight_layout(); fig.savefig(OUT / "fig4_map_condition.png", dpi=180, bbox_inches="tight"); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 8))
tr_geo = tracts.merge(tr[["GEOID", "pqi_lane_weighted"]], on="GEOID", how="inner")
tr_geo.plot(ax=ax, column="pqi_lane_weighted", cmap="Blues_r", vmin=50, vmax=85, edgecolor=SURFACE, linewidth=0.6,
            legend=True, legend_kwds={"shrink": 0.5, "label": "Lane-mile weighted PQI"})
gap.plot(ax=ax, color="#d03b3b", linewidth=1.0, label="Poor/Fair, no plan through FY2028")
boundary.boundary.plot(ax=ax, color=MUTED, linewidth=0.8)
ax.set_axis_off(); ax.set_title("Tract PQI (darker = worse) and unplanned Poor/Fair segments", loc="left", fontsize=11, color=INK)
ax.legend(frameon=False, fontsize=8, loc="upper left")
fig.text(0.01, 0.01, "Sources: PQI Segments; Planned Road Resurfacings; Census tracts (data.tempe.gov).", fontsize=7, color=MUTED)
fig.tight_layout(); fig.savefig(OUT / "fig5_map_tract_gap.png", dpi=180, bbox_inches="tight"); plt.close(fig)

# ====================================================================== write
keep = ["sid", "RM_NO", "RM_STREET", "RM_FROM", "RM_TO", "func", "is_city", "miles", "lanes", "lane_mi", "pqi_now", "band_now",
        "MEASURED_PQI", "CURRENT_PQI", "PQI_DATE", "insp_year", "plan_fy", "plan_cat", "plan_desc", "plan_family",
        "usr_CIP_Number", "GEOID", "NAME", "median_hh_income", "pct_poverty", "area_name", "geometry"]
seg_out = seg[keep].copy()
seg_out["band_now"] = seg_out["band_now"].astype(str)
seg_out["PQI_DATE"] = seg_out["PQI_DATE"].dt.strftime("%Y-%m-%d")
seg_out.to_file(PROC / "segments_enriched.geojson", driver="GeoJSON")
seg_out.drop(columns="geometry").to_csv(PROC / "segments_enriched.csv", index=False)
(OUT / "analysis_tables.md").write_text("\n".join(lines), encoding="utf-8")
print(f"\nWrote outputs/analysis_tables.md and five figures; data/processed/segments_enriched.*")
