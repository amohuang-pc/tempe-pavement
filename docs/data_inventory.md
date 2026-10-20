# Tempe 1.22 Pavement Quality Index: Data Inventory (C2 check)

Draft v0.1, 2026-10-19, Amos. Purpose: verify what row-level data exists behind Simon's Oct 8 PQI report, and list what is still missing. Numbers in brackets [S1] point to the Sources list at the end.

## 1. Official metric definition (verified 2026-10-19)

| Item | Finding | Source |
|---|---|---|
| Measure | 1.22 Pavement Quality Index, Council priority 1 Safe and Secure Communities | [S1] |
| Target wording | "Achieve adopted standards for Pavement Quality Index greater than or equal to a citywide average of 70 across all demographic categories" | [S1], [S2] |
| Target date | FY 2035/36 (the open-data summary table lists 2030; the Nov 2025 Council index is the authoritative document, so use FY 2035/36 and note the conflict) | [S1] |
| Baseline | 59 (FY 2015/16) | [S1] |
| Inspection cycle | Every 3 years, survey vehicle with imaging and sensors; scores stored in Stantec RoadMatrix | [S2], [S6] |
| Publish frequency | Citywide average: annual. Segment PQI: quarterly. Publish method: manual | [S4] |
| Data contacts | Author: Isaac Chavira (isaac_chavira@tempe.gov). Maintainer: Sue Taaffe (sue_taaffe@tempe.gov). Pavement management supervisor quoted in trade press: Ed Bond, Senior Civil Engineer | [S4], [S6] |
| City values (7) | People, Integrity, Respect, Openness, Creativity, Quality, Diversity | [S7] |

Implication for the report: the equity clause ("across all demographic categories") is part of the official target, so an equity breakdown is required, not optional. The values that map most directly are Quality (service levels), Diversity/Respect (equity across neighborhoods) and Openness (open data).

## 2. Datasets found (row-level access confirmed through the ArcGIS REST API)

All layers sit on the Tempe ArcGIS Online org `services.arcgis.com/lQySeXwbBg53XWDi` unless noted. Every layer pages at 2,000 records, so downloads must loop with `resultOffset`.

| # | Dataset | REST endpoint | Rows (2026-10-19) | Geometry | Last edit | Key fields | Use |
|---|---|---|---|---|---|---|---|
| D1 | Pavement Quality Index Segments (current snapshot) | `.../Pavement_Quality_Index_Segment/FeatureServer/7` (layer name PresentStatusPQI) | 5,127 | Polyline | 2026-06-03 | RM_NO (segment id), RM_STREET/FROM/TO, RM_MI (miles), RM_NUM (lane count), rm_func (class), per_pqi_yr1 (PQI), usr_CIP_Number, section_number | Current condition map, miles by class and score band, lane-mile check (RM_NUM) |
| D2 | 1.22 PQI Road Segment (detail) | `.../1_22_PQI_Road_Segment_(detail)/FeatureServer/0` (a table, no geometry) | 5,312 | None | 2025-07-23 | SECTION_NUMBER, ON/FROM/TO_STREET, LENGTH, CURRENT_PQI, MEASURED_PQI, PQI_DATE, YEAR, CLASS | Wear rate per segment (Model B); joins to D1 on section_number = SECTION_NUMBER |
| D3 | 1.22 PQI Average Citywide (summary) | item 9048488c2150415b8c9d1ebf1861ebf9 (CSV download endpoint rate-limited today; pull via REST or portal) | about 14 yearly rows 2010 to 2026 | None | 2025-10 | year, PQI, target | Trend baseline (Model A) |
| D4 | Planned Road Resurfacings | `.../Planned_Road_Resurfacings/FeatureServer/0` | 4,204 | Polyline | 2025-03-14 | RM_NO, reh_iyear (FY 2025 to 2028), reh_select_fdesc (treatment), sql_treatment_category, alt_code | Bond-period volume (Model C); joins to D1 on RM_NO |
| D5 | Traffic Count Segments | `gis.tempe.gov/arcgis/rest/services/Open_Data/TrafficCountSegment/FeatureServer/0` | 163 | Polyline | described as last checked 2016 | StreetOn/From/To, CountFirst, CountSecond, TotalVolume, CaptureDate, StreetClassification | Traffic weighting, but thin: 163 segments vs 5,127 road segments, and dated |

Notes:
- D1 and D4 share RM_NO (RoadMatrix id), so the planned treatments can be joined to each current segment directly. D2 shares section_number. This is better than the grouped approach in the Oct 8 report, which never joined the layers.
- D1 carries RM_NUM = lane count. Summing RM_MI x RM_NUM gives lane-miles from the City's own data, replacing the estimated 2.47 lane factor.
- D1 row count moved from 5,136 (earlier harvest) to 5,127, and the detail table has 5,312 rows, so segment ids changed between the 2025 detail extract and the 2026 snapshot. Expect some unmatched rows on the join; report the match rate.
- D5 is the weak spot. For traffic weighting use MAG (Maricopa Association of Governments) or ADOT AADT counts instead; both cover Tempe arterials with recent years. To be sourced in round 2.

## 3. External sources found

| # | Source | What it gives | Status |
|---|---|---|---|
| E1 | Crafco case study on Tempe crack sealing (vendor publication, 2022) [S6] | Tempe's own cost per lane-mile from its RoadMatrix deterioration curve: maintenance $20,000, overlay $50,000, rehabilitation $160,000, reconstruction $330,000. Network 1,241 lane-miles = 532 centerline miles (lane factor 2.33). Staff goal quoted as PQI 70 by 2028 | Replaces the Littleton 2016 prices in the report. Vendor source, so confirm with the City, but it is Tempe-specific and far better than Colorado |
| E2 | Tempe Strategic Priorities and Performance Measures Index, Nov 2025 [S1] | Authoritative target wording and date | Done |
| E3 | Census ACS 5-year, tract level (median household income, race/ethnicity, poverty) | Equity breakdown required by the target wording | Same pull as the opioid repo; reuse scripts |
| E4 | Census TIGER tract boundaries | Spatial join of D1 segments to tracts | Reuse from opioid repo |
| E5 | MAG or ADOT traffic counts | Recent AADT on arterials and collectors | To find in round 2 |
| E6 | Tempe FY2026/27 CIP and budget documents | Post-bond street maintenance budget line, actual bond road share | To find in round 2; the report says no post-2028 upkeep budget is public |
| E7 | Tempe 311 service requests | Not found as an open dataset; only 311 performance summaries (2.03, 2.17) exist | Likely needs a records request or interview |

## 4. Gaps against the Oct 8 report

| Gap in the report | Can open data close it? | How |
|---|---|---|
| Grouped data only (Model C assumes even spread within score bands) | Yes | Rebuild Model C from D1 segments (5,127 rows) |
| Wear rate is a system projection, not measured | Partly | D2 has MEASURED_PQI, CURRENT_PQI, PQI_DATE per segment. If (MEASURED minus CURRENT) / years is identical across segments, that proves it is a formula. True measured change needs two inspection cycles, which the open data does not publish (only the latest). Ask the City for the prior-cycle table |
| Unit prices from Littleton 2016 | Yes, mostly | Use E1 Tempe figures per lane-mile; confirm with City |
| Lane factor 2.47 estimated | Yes | Sum RM_MI x RM_NUM in D1; cross-check against 1,241 lane-miles in E1 |
| Seal adds 10 points (assumed) | No | Needs before/after inspections of sealed segments; ask the City, or cite RoadMatrix treatment-effect defaults if the City will share them |
| Planned lengths may double count divided roads | Yes | D4 joined to D1 on RM_NO; count distinct RM_NO rather than summing shape length |
| Traffic not joined | Partly | D5 is too thin; use E5 |
| Equity not addressed at all | Yes | D1 x E3/E4: PQI distribution by tract income and race/ethnicity |
| No map | Yes | D1 has geometry |
| 2030 vs 2036 target conflict | Yes | Resolved: FY 2035/36 per [S1] |

## 5. Interview decision

An interview or email request to the pavement management team is worth doing, because three things cannot come from open data: the prior inspection cycle (true wear rate), the post-bond maintenance budget, and treatment-effect assumptions in RoadMatrix. Suggested contact order: Isaac Chavira (dataset author) or Sue Taaffe (maintainer) at data@tempe.gov, then Ed Bond (pavement management). Draft questions:

1. Is a prior-cycle inspection table (the 2020 to 2022 survey) available alongside the current one, so we can measure actual deterioration?
2. What PQI gain and service-life extension does RoadMatrix assume for each treatment type (crack seal, slurry/micro seal, mill and overlay, reconstruction)?
3. What are current Tempe unit costs per lane-mile for each treatment (the 2022 figures were $20k / $50k / $160k / $330k)?
4. Of the 2024 bond, what dollar amount is allocated to streets, and is there a planned annual pavement preservation budget after FY2028?
5. Does the City track PQI by neighborhood or demographic group for the "across all demographic categories" clause, and if so how?
6. How many lane-miles were re-inspected in 2026, and when will those scores be published?

## Sources

- [S1] Tempe City Council, Strategic Priorities and Performance Measures Index, November 2025. https://www.tempe.gov/home/showpublisheddocument/115566/638991440904370000 (1.22: target "greater than or equal to a citywide average of 70 across all demographic categories", 70 by FY 2035/36, baseline 59 in FY 2015/16)
- [S2] 1.22 Pavement Quality Index dashboard page. https://safe-and-secure-communities-tempegov.hub.arcgis.com/pages/pavement-quality-index (3-year inspection cycle, segment-level PQI map)
- [S3] Pavement Quality Index Segments, REST layer 7. https://services.arcgis.com/lQySeXwbBg53XWDi/arcgis/rest/services/Pavement_Quality_Index_Segment/FeatureServer/7 (5,127 features, last edit 2026-06-03)
- [S4] 1.22 PQI Road Segment (detail). https://data.tempe.gov/datasets/tempegov::1-22-pqi-road-segment-detail and REST https://services.arcgis.com/lQySeXwbBg53XWDi/arcgis/rest/services/1_22_PQI_Road_Segment_(detail)/FeatureServer/0 (5,312 rows, last edit 2025-07-23; contacts and publish frequency from the item description)
- [S5] Planned Road Resurfacings. https://services.arcgis.com/lQySeXwbBg53XWDi/arcgis/rest/services/Planned_Road_Resurfacings/FeatureServer/0 (4,204 features, FY 2025 to 2028, last edit 2025-03-14)
- [S6] Crafco, Case Study: Crack Sealing, Tempe AZ DOT, 2022. https://crafco.com/wp-content/uploads/2023/05/Crafco-Case-Study-Crack-Sealing-Tempe-AZ-DOT-2022.pdf (1,241 lane-miles / 532 centerline miles; cost per lane-mile $20,000 maintenance, $50,000 overlay, $160,000 rehabilitation, $330,000 reconstruction; 4 to 10 times claim; Ed Bond)
- [S7] City of Tempe, Mission and Values. https://www.tempe.gov/government/city-manager-s-office/mission-and-values (seven values)
- [S8] Traffic Count Segments. https://gis.tempe.gov/arcgis/rest/services/Open_Data/TrafficCountSegment/FeatureServer/0 (163 segments, last checked 2016)
- [S9] 1.22 PQI Average Citywide (summary), item 9048488c2150415b8c9d1ebf1861ebf9. https://data.tempe.gov/datasets/tempegov::1-22-pqi-average-citywide-summary
