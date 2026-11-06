# 1.22 Pavement Quality Index: Definitions Register

Draft v0.1, 2026-10-19, Amos. Every number that appears in a team document must be traceable to one of the definitions below. Where the Oct 8 report used a different definition, the difference is flagged so it can be corrected before anything is presented. Sources in brackets [S1] are listed at the end.

## A. The measure itself

| Term | Official definition (wording as published) | Source | What the Oct 8 report used | Action |
|---|---|---|---|---|
| Performance measure 1.22 | "Achieve adopted standards for Pavement Quality Index greater than or equal to a citywide average of 70 across all demographic categories." Target: 70 by FY 2035/36. Baseline: 59 (FY 2015/16). | [S1] | Same target and date. Equity clause not addressed. | Keep. Add an equity section. |
| PQI | "Measurement of the smoothness of the roadway and any distresses in the pavement surface", scored 0 (worst) to 100 (best). Collected about every 3 years by a survey vehicle; stored in Stantec RoadMatrix. | [S2], [S3] | Same. | Keep. |
| Condition bands (official) | Poor 0 to 39.99; Fair 40 to 59.99; Good 60 to 79.99; Excellent 80 to 100. These are the class breaks on the City's own PQI map layer. | [S4] | Custom bands: below 40, 40 to 55, 55 to 70, 70 to 85, 85+. KPI "share of miles below 55". | **Change.** Report shares by the official four bands. Replace "below 55" with "Poor + Fair (below 60)" or "Poor (below 40)". The bond goal "every street above 82" sits inside the official Excellent band (80+), so state it as "Excellent". |
| Citywide average | Not documented anywhere public: the data dictionary says only "Average Pavement Quality Index score for city streets" and that `asOfDate` is the last day of the reporting period (sample 12/31/2010, so calendar-year end). Weighting (per segment, per centerline mile, or per lane-mile) and included road classes are not stated. | [S5] | Length-weighted (centerline miles) over 485.7 miles, excluding 1.8 miles of private roads and alleys; model start 66.2 vs official 65. | **Verify.** `02_definitions_check.py` computes the average three ways from the June 2026 snapshot and compares each to the official 65 (end 2025) and the City's expected 64 (June 2026). Use whichever reproduces the official figure; if none does, ask the City (interview question 7). |
| Reporting period | Summary records are stamped at calendar year end (`asOfDate` 12/31). The target is stated in fiscal-year terms (FY 2035/36 ends June 30, 2036). | [S1], [S5] | "June 2036 deadline". | Keep, but say "FY 2035/36 (ends June 30, 2036)". |
| Status categories | Achieved: met or exceeded target. Off Track: at least 75% of target but not met. At Risk: below 75% of target. Not Started: baseline only. | [S5] | "Yellow (Concerned)". | Use the dictionary's wording. 65 / 70 = 93%, so the current status under the dictionary rule is Off Track. Confirm the dashboard label before quoting a color. |
| Target-year conflict | Open-data summary table lists a target of 70 by 2030; the Nov 2025 Council index says FY 2035/36. | [S1], [S5] | Noted; followed the Council document. | Keep. The 2030 figure is probably an older target that was not updated in the table. |

## B. Dataset fields (what each column means)

### B1. Pavement Quality Index Segments (current map layer, 5,127 features, snapshot 2026-06-03) [S4]

| Field | Alias | Meaning | Caution |
|---|---|---|---|
| RM_NO | SegmentNumber | RoadMatrix segment id. Join key to Planned Road Resurfacings (RM_NO). | |
| section_number | Section Number | Join key to the 1.22 detail table (SECTION_NUMBER). | Detail table has 5,312 rows vs 5,127 here; expect unmatched rows. |
| RM_STREET / RM_FROM / RM_TO | SegmentOn / From / To | Street and cross streets. | |
| RM_MI | SegmentMileage | Centerline miles of the segment. | |
| SegmentLength | SegmentLength | Length in feet (integer). | Check RM_MI x 5280 = SegmentLength. |
| RM_NUM | LaneCount | Number of lanes. | Lane-miles = RM_MI x RM_NUM. The City's own figure is 1,241 lane-miles on 532 centerline miles [S6]; compare. |
| rm_func | SegmentFunction | Functional class (Arterial, Collector, Local, Local-industrial, plus private/alley values). | Confirm the exact value list from the data. |
| per_pqi_yr1 | SegmentQuality | The PQI value the City maps as the segment's current score. | **Definition risk.** The field name reads like a RoadMatrix "performance, year 1" value, i.e. a modelled current-year score, not the raw inspection reading. The detail table's CURRENT_PQI is described the same way ("as of current year"). Treat per_pqi_yr1 as "City's current modelled PQI", never as "measured". The check script tests whether per_pqi_yr1 equals CURRENT_PQI on matched sections. |
| usr_CIP_Number | CIP Number | Capital project number if the segment is in a funded project. | Useful flag for "already scheduled". |

### B2. 1.22 PQI Road Segment (detail) (5,312 rows, table without geometry, last edit 2025-07-23) [S7]

| Field | Official description | Caution |
|---|---|---|
| SECTION_NUMBER | Unique identifier for each street segment | Join key to section_number above. |
| ON_STREET / FROM_STREET / TO_STREET | Street and cross streets | |
| LENGTH | Length of the segment, in feet (stored as text) | Convert to numeric; divide by 5280 for miles. |
| COUNT | Number of lanes in the segment | |
| CLASS | Functional classification | |
| MEASURED_PQI | PQI measured for the segment on the PQI Date | This is the only field described as a measurement. |
| PQI_DATE | Date the PQI was measured | Stored as text with "0:00"; parse as date. |
| CURRENT_PQI | Current PQI of the segment "as of current year" | Not described as measured. Given the 3-year survey cycle, this must be modelled (RoadMatrix deterioration curve). |
| YEAR | Year the data was recorded | The dictionary does not say whether this is the measurement year or the extract year. The Oct 8 report assumed measurement year; the check script compares YEAR to the year of PQI_DATE. |

The Oct 8 report's Model B divides (MEASURED_PQI minus CURRENT_PQI) by (2025 minus YEAR) and calls it a wear rate. Under the definitions above this is the City's modelled deterioration, not an observed one. The report says so in its limitations; the main text should say so too.

### B3. Planned Road Resurfacings (4,204 features, FY 2025 to 2028, last edit 2025-03-14) [S8]

| Field | Alias | Meaning | Caution |
|---|---|---|---|
| RM_NO | RoadMatrixId | Join key to the segments layer. | |
| reh_iyear | Fiscal Year | Fiscal year of the planned work, labelled by its ending year (FY runs July 1 to June 30). | "2026" means July 2025 to June 2026. |
| reh_select_fdesc | (treatment description) | Treatment name (13 distinct values per the Oct 8 report). | Map each to an official treatment family before summing miles. |
| sql_treatment_category | (treatment category) | Grouped treatment category. | Use this for the overlay vs seal split rather than hand-grouping. |
| alt_code | reh_code | Treatment code. | |
| Shape__Length | | Geometry length in the layer's units. | Do not sum this for miles; use RM_MI from the joined segments layer, and count distinct RM_NO to avoid double counting divided roads. |

The City describes this layer as a tentative five-year paving schedule that depends on a funding schedule "not yet approved" and can change with each annual budget [S2]. Quote it as a plan, not as committed work.

### B4. 1.22 PQI Average Citywide (summary) [S5]

Fields: Type (text, e.g. "PQI"), status, metricValue (PQI score), asOfDate (last day of the reporting period), comment. About 14 yearly rows, 2010 to 2026.

## C. Network size: three different numbers that are not interchangeable

| Figure | Meaning | Source |
|---|---|---|
| 485.7 centerline miles | Sum of RM_MI in the June 2026 segments layer (excluding 1.8 miles of private and alley segments per the Oct 8 report) | [S4] via Oct 8 report |
| 532 centerline miles / 1,241 lane-miles | City network size quoted by the pavement management supervisor in 2022 | [S6] |
| "nearly 1,200 miles" | Figure used in 2024 to 2025 bond communications; most likely lane-miles | Oct 8 report citing Arizona PBS |

The Oct 8 report derived a lane factor of 2.47 from 1,200 / 485.7. The City's own ratio is 1,241 / 532 = 2.33. Neither is needed once RM_NUM (lane count) is summed from the data. Always label a mileage figure as centerline or lane-miles.

## D. Costs

| Figure | Meaning | Source |
|---|---|---|
| Maintenance $20,000; Overlay $50,000; Rehabilitation $160,000; Reconstruction $330,000 per lane-mile | Tempe's own cost assumptions from its RoadMatrix deterioration curve, as quoted in 2022 | [S6] (vendor case study; confirm with the City) |
| Surface seal $35,000; Mill and overlay $320,000; Reconstruction $1.3M per lane-mile | City of Littleton, Colorado, 2016 bid prices | Oct 8 report |

Use the Tempe figures. Keep the Littleton figures only as a sensitivity case. Note the ratio differs a lot: overlay is 2.5x maintenance in Tempe's curve but 9x in Littleton's, which will change the Model D result.

## E. Open definition questions (for the City or the organizers)

7. How is the citywide average PQI in measure 1.22 calculated: per segment, per centerline mile, or per lane-mile, and which functional classes are included?
8. Is `per_pqi_yr1` (map layer) the same value as `CURRENT_PQI` (detail table), and is it a modelled current-year value from RoadMatrix or the latest measured value?
9. In the detail table, does YEAR mean the inspection year or the extract year?
10. How is "across all demographic categories" measured for 1.22: by census tract, by neighborhood association, or another geography?

(Questions 1 to 6 are in data_inventory.md section 5.)

## Sources

- [S1] Tempe City Council, Strategic Priorities and Performance Measures Index, November 2025. https://www.tempe.gov/home/showpublisheddocument/115566/638991440904370000 (1.22 wording, 70 by FY 2035/36, baseline 59)
- [S2] City of Tempe, Pavement Management Program page. https://www.tempe.gov/government/public-works/engineering/pavement-management-program (PQI description, 3-year cycle, treatment types, "not yet approved" funding schedule)
- [S3] 1.22 Pavement Quality Index dashboard page. https://safe-and-secure-communities-tempegov.hub.arcgis.com/pages/pavement-quality-index
- [S4] Pavement Quality Index Segments, REST layer 7 (PresentStatusPQI). https://services.arcgis.com/lQySeXwbBg53XWDi/arcgis/rest/services/Pavement_Quality_Index_Segment/FeatureServer/7 (fields; renderer class breaks Poor 0 to 39.99, Fair 40 to 59.99, Good 60 to 79.99, Excellent 80 to 100; 5,127 features; last edit 2026-06-03)
- [S5] Tempe data dictionary, 1.22 PQI Average Citywide. https://tempe.gitbook.io/data-dictionary/1.22-pqi-average-citywide (fields, asOfDate definition, status categories)
- [S6] Crafco, Case Study: Crack Sealing, Tempe AZ DOT, 2022. https://crafco.com/wp-content/uploads/2023/05/Crafco-Case-Study-Crack-Sealing-Tempe-AZ-DOT-2022.pdf (1,241 lane-miles / 532 centerline miles; cost per lane-mile $20,000 / $50,000 / $160,000 / $330,000)
- [S7] Tempe data dictionary, 1.22 PQI Road Segment. https://tempe.gitbook.io/data-dictionary/1.22-pqi-road-segment.md (field definitions, LENGTH in feet, COUNT = lanes, CURRENT_PQI "as of current year", MEASURED_PQI measured on PQI Date)
- [S8] Planned Road Resurfacings, REST layer 0. https://services.arcgis.com/lQySeXwbBg53XWDi/arcgis/rest/services/Planned_Road_Resurfacings/FeatureServer/0 (fields; fiscal year labelled by ending year, July 1 to June 30)
