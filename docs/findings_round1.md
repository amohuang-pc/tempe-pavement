# 1.22 Pavement Quality Index: Round 1 Findings (segment level)

2026-10-20, Amos. Reproducible from `scripts/01_download.py`, `02_definitions_check.py`, `03_analysis.py`; tables in `outputs/analysis_tables.md`, figures in `outputs/fig1` to `fig5`. Numbers marked [A] come from those scripts; [S1] etc. point to the Sources list at the end. This round rebuilds the Oct 8 report's models from the 5,127 road segments and adds what the report did not have: observed treatment effects, planned-program coverage, equity, maps.

## 1. Definitions settled before modelling (see docs/definitions.md)

- Target: "citywide average of 70 across all demographic categories", 70 by FY 2035/36, baseline 59 (FY 2015/16) [S1]. The open-data summary table carries an older target row of 70 by 2029-12-31 [S9]; the Council document governs.
- Official condition bands, from the City's own map layer: Poor 0 to 39, Fair 40 to 59, Good 60 to 79, Excellent 80 to 100 [S4]. All shares below use these bands.
- `per_pqi_yr1` on the map equals `CURRENT_PQI` in the detail table for 87% of segments; the 13% that differ are exactly the segments resurfaced in FY2025. So the map carries the City's modelled current-year score, updated for completed work, not the raw inspection reading. The only measured field is `MEASURED_PQI` [A].
- `YEAR` in the detail table is the inspection year (matches `PQI_DATE` in 99.6% of rows). Inspections roll through the network: 1,971 segments in 2023, 2,339 in 2024, 939 in 2025 [A].
- The map layer's `RM_NUM` field is aliased "LaneCount" but holds the segment id. Lane counts come from the detail table's `COUNT` field. Summing miles times lanes gives 1,226 lane-miles on 483.9 city centerline miles (factor 2.53) [A], which matches the 1,241 lane-miles the City quoted in 2022 [S6] and the "nearly 1,200 miles" in bond coverage. The Oct 8 report's 2.47 estimate was close; the data now replaces it.
- Which average is the official one: the lane-mile weighted mean of the July 2025 detail table is 64.7, which rounds to the official 65 for 2025; the centerline-weighted (62.6) and simple (60.4) means do not [A]. Working hypothesis: measure 1.22 is lane-mile weighted. To confirm with the City.

## 2. Network state, June 2026 [A]

| | Lane-miles | Share |
|---|---|---|
| Poor (0-39) | 198 | 16.1% |
| Fair (40-59) | 185 | 15.1% |
| Good (60-79) | 373 | 30.4% |
| Excellent (80-100) | 470 | 38.4% |

Lane-mile weighted average 68.6 (centerline 67.0, simple 66.0). Local streets hold 646 of the 1,226 lane-miles and 23% of their lane-miles are Poor; arterials are 4% Poor. Figure 1 and the map in Figure 4.

## 3. Deterioration: the City's curve is not flat [A]

Loss per year implied by MEASURED_PQI minus CURRENT_PQI over the years since inspection, by the segment's measured band (median): Poor 3.4, Fair 3.8, Good 2.95, Excellent 0.9. Within each class and year the spread is wide (standard deviation 0.9 to 1.7), so the City's system does not apply one rate per group; it applies a curve that depends on the segment's score. This is still the City's model, not an observation; a second inspection cycle is needed for that (interview question 1).

## 4. Treatment effects observed on FY2025 work [A]

The FY2025 segments (746 mill-and-overlay, 296 seal-coat, 12 slurry, 39 micro-mill) are the only ones whose map value changed after the July 2025 extract. Pre-work inspection reading vs post-work map value, medians:

| Treatment | Segments updated | Pre | Post | Gain |
|---|---|---|---|---|
| Mill and overlay | 60% | 49.6 | 96.1 | +58 |
| Seal coat | 60% | 77.0 | 80.2 | +8 |
| Slurry seal | 100% (12) | 76.2 | 92.4 | +17 |

Mill and overlay resets to about 96, which confirms the Oct 8 report's 95. The seal-coat gain of 8 on updated segments is below the report's assumed 10, and 40% of seal segments show no change at all. Whether that means unrecorded work or a life-extension (no score jump) treatment in RoadMatrix is interview question 2.

## 5. The planned program covers almost every Poor and Fair road [A]

FY2026 to FY2028 planned work: 3,110 segments, 306.6 centerline miles, 762 lane-miles, 62% of the city's lane-miles (434 lane-miles mill and overlay, 326 seal). Joined to today's condition, only 25 segments (6 lane-miles) are Poor or Fair with no treatment planned through FY2028 (list in `data/processed/gap_segments_no_plan_below60.csv`). The planned overlays start from a median PQI of 30 to 48, so the plan is worst-first in practice, as the City says. The City calls the schedule tentative and dependent on a funding plan not yet approved [S2].

## 6. Equity: income shows no gradient; geography does [A]

By census tract median household income (ACS 2019-2023), lane-mile weighted PQI is 70.6 in the lowest-income quartile, 64.7, 68.2 and 69.5 in the others; correlation between tract income and tract PQI across 40 tracts is -0.03. The lowest-income tracts are not worse off, and their roads are the most heavily covered by the plan (63% of lane-miles). This is a negative finding and should be reported as one.

The disparity is spatial. By the City's eight character areas: Alameda 58.6 (48% of lane-miles Poor or Fair), Downtown/ASU 63.9, Corona/South Tempe 65.8, Apache 67.2, Southwest 69.4, Diablo/Double Butte 71.5, Papago/North Tempe 72.7, Kiwanis/The Lakes 82.8 (5%). Twenty of forty tracts sit below 70 today. Figure 5. Race and ethnicity tables (ACS B03002) can be joined the same way and should be, since the target wording says "demographic".

## 7. Projection to FY2036 at segment level [A]

Each segment loses the City's median rate for its band each year; planned work is applied in its fiscal year with the observed effects above (FY2026 work is applied immediately, because the June 2026 map does not yet record it); a seal holds a segment for three years (assumption). Lane-mile weighted citywide PQI:

| | 2028 peak | 2036 | Below 70 by |
|---|---|---|---|
| Stop all work after FY2028 | 86.7 | 75.2 | not before 2036 |
| Same, with the Oct 8 report's wear rule (1 at 85+, 3 below) | 86.4 | 73.5 | not before 2036 |
| Stop, and the FY2028 tranche is never funded | 83.7 | 68.7 | 2036 |
| Preserve only: seal every segment that drops into Fair | 86.7 | 79.9 | never |
| Continue: seal Fair and overlay Poor | 86.7 | 81.9 | never |

Share of lane-miles in Poor with no work after FY2028: 2% in 2028, 9% in 2036. Post-FY2028 cost of the preserve-only program: about 275 lane-miles of seal over eight years, about $0.7M a year at the City's 2022 unit cost of $20,000 per lane-mile for maintenance [S6]; the continue program about $1M a year ($50,000 per lane-mile overlay).

What changed against the Oct 8 report. The report's base case fell to 69.3 in 2036 with no post-bond spending. At segment level the same rule gives 73.5, because (a) the full FY2026 tranche is applied rather than half (the map proves it is not yet recorded), (b) the planned segments are the actual worst ones, not an even spread within bands, and (c) the measure is weighted by lane-miles, which favours the arterials. The direction of the report's main recommendation holds: without a post-bond budget the average drifts down about 1.4 points a year and the Poor share quadruples. What does not hold is the certainty of missing 70 by 2036; the base case now clears it by 3 to 5 points, and the one scenario that misses is the plan itself not being fully funded.

## 8. What to say to Simon (summary)

1. Keep the problem statement and the four-model structure. Change the bands to the official four and the KPI from "below 55" to "Poor (below 40)" or "Poor or Fair (below 60)".
2. Replace Littleton prices with Tempe's own ($20k / $50k / $160k / $330k per lane-mile, 2022, vendor-quoted) and the 2.47 factor with the computed 1,226 lane-miles.
3. Re-state Insight 1: passing is not in doubt and holding 70 is likely even with no spending; the risks are the unfunded FY2028 tranche and the return of Poor roads, not the citywide average.
4. Add the equity section: no income gradient, large area gradient (Alameda vs Kiwanis), 20 of 40 tracts below 70. This answers the target's own wording and the Diversity and Respect values.
5. Add the maps.
6. Treatment effects now come from Tempe data: overlay to 96 confirmed; seal gain 8, not 10, with a question mark.

## Open questions for the City

See docs/data_inventory.md section 5 (questions 1 to 6) and docs/definitions.md section E (7 to 10). Highest value: the prior inspection cycle, the seal-coat effect in RoadMatrix, and the post-FY2028 budget.

## Sources

- [S1] Tempe City Council, Strategic Priorities and Performance Measures Index, Nov 2025. https://www.tempe.gov/home/showpublisheddocument/115566/638991440904370000 (1.22 wording; 70 by FY 2035/36; baseline 59)
- [S2] City of Tempe, Pavement Management Program. https://www.tempe.gov/government/public-works/engineering/pavement-management-program (3-year inspections; five-year schedule "not yet approved")
- [S4] Pavement Quality Index Segments, REST layer 7. https://services.arcgis.com/lQySeXwbBg53XWDi/arcgis/rest/services/Pavement_Quality_Index_Segment/FeatureServer/7 (5,127 features, 2026-06-03; renderer bands)
- [S6] Crafco, Case Study: Crack Sealing, Tempe AZ DOT, 2022. https://crafco.com/wp-content/uploads/2023/05/Crafco-Case-Study-Crack-Sealing-Tempe-AZ-DOT-2022.pdf (1,241 lane-miles; $20k / $50k / $160k / $330k per lane-mile)
- [S7] Tempe data dictionary, 1.22 PQI Road Segment. https://tempe.gitbook.io/data-dictionary/1.22-pqi-road-segment.md (COUNT = lanes; LENGTH in feet; CURRENT_PQI "as of current year"; MEASURED_PQI on PQI Date)
- [S8] Planned Road Resurfacings, REST layer 0. https://services.arcgis.com/lQySeXwbBg53XWDi/arcgis/rest/services/Planned_Road_Resurfacings/FeatureServer/0 (4,204 features, FY2025-2028)
- [S9] 1.22 PQI Average Citywide (summary), REST. https://services.arcgis.com/lQySeXwbBg53XWDi/arcgis/rest/services/1.22_PQI_Average_Citywide_(summary)_-_OD/FeatureServer/0 (59, 60, 56.5, 56.2, 59 x4, 60 x5, 65 for 2010-2025; Target 70 dated 2029-12-31)
- Census tracts and ACS 2019-2023 income and poverty: data.tempe.gov tract layers, copied from the tempe-opioid repository (data/external).
