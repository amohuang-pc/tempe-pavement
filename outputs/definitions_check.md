# Definitions check (run on the raw downloads)

Rows: segments 5,127; detail 5,312; planned 4,204; summary 15

## 1. Functional classes in the current layer

| rm_func            |   segments |   centerline_mi |   lane_mi |   mean_pqi_simple |
|:-------------------|-----------:|----------------:|----------:|------------------:|
| Local              |       3907 |           323.1 |     646.5 |              64.1 |
| Arterial           |        561 |            87   |     414.2 |              74.2 |
| Collector          |        456 |            42.1 |      97.1 |              71.1 |
| Local - Industrial |        193 |            31.8 |      68.2 |              67.8 |
| Private            |          9 |             1.8 |       3.7 |              50.6 |
| Alley              |          1 |             0   |       0   |              21.1 |

Total centerline miles: 485.7; total lane-miles: 1229.7 (City quoted 532 centerline / 1,241 lane-miles in 2022).
SegmentLength vs RM_MI x 5280: median abs difference 7.1 ft, 9.0% of segments differ by more than 50 ft.

Excluded as non-city (private/alley): 10 segments, 1.8 miles. Remaining: 5,117 segments, 483.9 miles.

## 2. Citywide average under three weightings

- simple mean per segment (all classes): 65.96
- simple mean per segment (city classes): 66.00
- centerline-mile weighted (city classes): 67.05
- lane-mile weighted (city classes): 68.58

Official summary table (last 5 rows):
|   ObjectId | Type   | status    |   metricValue | asOfDate            |   comment |
|-----------:|:-------|:----------|--------------:|:--------------------|----------:|
|         11 | PQI    | Off Track |            60 | 2022-12-31 00:00:00 |       nan |
|         12 | PQI    | Off Track |            60 | 2023-12-31 00:00:00 |       nan |
|         13 | PQI    | Off Track |            60 | 2024-12-31 00:00:00 |       nan |
|         14 | PQI    | Off Track |            65 | 2025-12-31 00:00:00 |       nan |
|         15 | Target | nan       |            70 | 2029-12-31 00:00:00 |       nan |

Latest official citywide value: 65.0 (the Oct 8 report cites 65 for end 2025 and the City expected 64 for June 2026).
Reading: the weighting whose result is closest to the official value is the one to use. If none is within about 1 point, the City may include or exclude classes differently; ask the City (definitions.md question 7).

## 3. Share of centerline miles by the City's official bands (city classes)

| per_pqi_yr1        |   miles |   share |
|:-------------------|--------:|--------:|
| Poor (0-39)        |  92.458 |   0.191 |
| Fair (40-59)       |  77.675 |   0.161 |
| Good (60-79)       | 137.05  |   0.283 |
| Excellent (80-100) | 176.727 |   0.365 |

For comparison with the Oct 8 report's custom bands:
- share of miles below 40: 19.1%
- share of miles below 55: 30.8%
- share of miles below 70: 48.0%
- share of miles below 85: 70.6%

## 4. Does per_pqi_yr1 (map) equal CURRENT_PQI (detail)?

Duplicate ids: detail 0, map layer 4.
Map segments matched to a detail row: 5,122 of 5,127 (99.9%).
per_pqi_yr1 vs CURRENT_PQI: exact (<0.05) for 87.0% of matched rows; median abs difference 0.00; 90th percentile 13.30.
per_pqi_yr1 vs MEASURED_PQI: exact for 21.2%; median abs difference 3.70.
Reading: if per_pqi_yr1 matches CURRENT_PQI and not MEASURED_PQI, the map shows the modelled current-year score, not the inspection reading. If it matches neither, the map layer was re-modelled after the detail extract (map 2026-06, detail 2025-07).

## 5. Is YEAR the inspection year?

YEAR equals year(PQI_DATE) in 99.6% of rows.
Rows by YEAR:
YEAR
2014.0       5
2018.0       2
2019.0       6
2020.0       3
2021.0      25
2023.0    1971
2024.0    2339
2025.0     939

PQI_DATE range: 2014-01-22 to 2025-07-09

## 6. Is (MEASURED_PQI - CURRENT_PQI) / years a fixed formula?

|                                |    n |   mean |    std |   min |   max |
|:-------------------------------|-----:|-------:|-------:|------:|------:|
| ('Arterial', 2020.0)           |    2 |   3.18 |   1.33 |  2.24 |  4.12 |
| ('Arterial', 2023.0)           |    2 |   3    |   1.77 |  1.75 |  4.25 |
| ('Collector', 2018.0)          |    1 |   3.97 | nan    |  3.97 |  3.97 |
| ('Collector', 2020.0)          |    1 |   1    | nan    |  1    |  1    |
| ('Collector', 2021.0)          |   12 |   3.47 |   0.43 |  2.92 |  4.25 |
| ('Collector', 2023.0)          |  274 |   3.42 |   1.56 |  0.25 |  9.55 |
| ('Collector', 2024.0)          |  231 |   2.15 |   1.75 |  0    |  6.8  |
| ('Local', 2014.0)              |    5 |   3.44 |   0.05 |  3.36 |  3.49 |
| ('Local', 2018.0)              |    1 |   3.71 | nan    |  3.71 |  3.71 |
| ('Local', 2019.0)              |    6 |   2.12 |   0.45 |  1.5  |  2.68 |
| ('Local', 2021.0)              |    8 |   3.36 |   0.36 |  2.78 |  4    |
| ('Local', 2023.0)              | 1590 |   3.25 |   0.93 |  0.15 |  8.95 |
| ('Local', 2024.0)              | 2058 |   2.49 |   1.37 |  0    |  4.4  |
| ('Local - Industrial', 2021.0) |    5 |   2.25 |   1.4  |  1.32 |  4.7  |
| ('Local - Industrial', 2023.0) |  105 |   3.01 |   0.98 |  0.9  |  5.5  |
| ('Local - Industrial', 2024.0) |   50 |   1.91 |   1.36 |  0    |  4.7  |

Reading: if std is near zero within a CLASS x YEAR group, the City's system applies one deterioration rate per group (a formula). If std is large, the system models each segment differently (for example by MEASURED_PQI level), and a per-segment curve can be fitted.
Correlation between MEASURED_PQI and annual_loss across all rows: -0.69 (a strong value means the curve depends on the starting score).

## 7. Planned Road Resurfacings: double counting and join rate

Planned rows: 4,204; distinct RM_NO: 4,200 (rows per id above 1 means a segment appears in more than one year or treatment).
Rows per RM_NO:
count
1    4198
2       1
4       1

Planned RM_NO found in the current layer: 100.0%.

Planned work by fiscal year and treatment category (distinct segments, miles from the current layer, so no double counting of divided roads):
|                          |   segments |   centerline_mi |   lane_mi |   mean_pqi_now |
|:-------------------------|-----------:|----------------:|----------:|---------------:|
| (2025, 'MILL_MICRO')     |         39 |             7   |      14.8 |           94   |
| (2025, 'MILL_OL')        |        746 |            61.6 |     157.6 |           92.5 |
| (2025, 'SEAL_COAT')      |        296 |            25.9 |      79.8 |           79.2 |
| (2025, 'SLURRY')         |         12 |             1.3 |       7.6 |           90.5 |
| (2026, 'MILL_MICRO')     |         13 |             1.6 |       4.9 |           59.5 |
| (2026, 'MILL_OL')        |        782 |            72.6 |     160.8 |           34.9 |
| (2026, 'RECONSTRUCTION') |          2 |             0.8 |       1.6 |           41   |
| (2026, 'SEAL_COAT')      |        542 |            55.4 |     130.3 |           69.4 |
| (2027, 'CAPE')           |         73 |             6.8 |      13.7 |           59.2 |
| (2027, 'MILL_OL')        |        718 |            65.2 |     165.9 |           45   |
| (2027, 'SEAL_COAT')      |        193 |            20   |      66.9 |           72.2 |
| (2027, 'SLURRY')         |         80 |             9.4 |      38.7 |           74   |
| (2028, 'MILL_MICRO')     |          8 |             1   |       2.1 |           59.3 |
| (2028, 'MILL_OL')        |        468 |            45.5 |      98.1 |           50.3 |
| (2028, 'REJV_FOG')       |        112 |            11.1 |      23.5 |           81.7 |
| (2028, 'SEAL_COAT')      |         96 |            14.1 |      40   |           80.6 |
| (2028, 'SLURRY')         |         20 |             2.5 |      13   |           74   |

Treatment descriptions present (reh_select_fdesc):
reh_select_fdesc
Full Width Mill & Conventional Overlay          2527
Seal Coat - PMM                                  400
Seal Coat - TRMSS HF                             289
Seal Coat - LiquidRoad                           210
Full Width Mill & Rubber Overlay                 191
Seal Coat - TRMSS                                147
Rejuvenator Agent                                112
Microsurfacing                                    86
Seal Coat - HDMB                                  81
Cape Seal                                         73
Micromill & Microsurfacing                        60
Slurry Seal                                       26
Reconstruction - Collector/Industrial Street       2