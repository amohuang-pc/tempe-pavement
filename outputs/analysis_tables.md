# 1.22 PQI segment-level analysis

Segments: 5,127 total, 5,117 city-maintained (483.9 centerline miles, 1226 lane-miles). Segments matched to a tract: 99.5%; to a character area: 99.7%.

## A. Network state (June 2026 snapshot, City's current modelled PQI)

Citywide averages under each weighting (city-maintained segments):
- simple mean per segment: 66.0
- centerline-mile weighted: 67.0
- lane-mile weighted: 68.6
- official 1.22 value for 2025: 65.0

Same three weightings on the July 2025 detail extract (CURRENT_PQI), which is the dataset the measure page publishes:
- simple mean: 60.4; centerline-weighted: 62.6; lane-mile weighted: 64.7
Reading: the lane-mile weighted mean of the published 2025 table rounds to the official 65; the other two do not. Working hypothesis (to confirm with the City): measure 1.22 is a lane-mile weighted average.

By functional class:
| func               |   segments |   centerline_mi |   lane_mi |   pqi_lane_weighted |   share_poor_lane_mi |
|:-------------------|-----------:|----------------:|----------:|--------------------:|---------------------:|
| Local              |       3907 |          323.07 |    646.51 |               64.49 |                 0.23 |
| Arterial           |        561 |           86.96 |    414.17 |               74.88 |                 0.04 |
| Collector          |        456 |           42.06 |     97.06 |               68.76 |                 0.17 |
| Local - Industrial |        193 |           31.82 |     68.23 |               68.85 |                 0.2  |

By official condition band:
| band_now           |   segments |   centerline_mi |   lane_mi |   share_centerline |   share_lane_mi |
|:-------------------|-----------:|----------------:|----------:|-------------------:|----------------:|
| Poor (0-39)        |       1117 |          92.458 |   197.573 |              0.191 |           0.161 |
| Fair (40-59)       |        794 |          77.675 |   185.43  |              0.161 |           0.151 |
| Good (60-79)       |       1379 |         137.05  |   372.728 |              0.283 |           0.304 |
| Excellent (80-100) |       1827 |         176.727 |   470.24  |              0.365 |           0.384 |

## B. Deterioration implied by the City's own model

For each segment the detail table carries the inspection reading (MEASURED_PQI on PQI_DATE) and the modelled value as of the July 2025 extract (CURRENT_PQI). The difference per year is the City's deterioration assumption for that segment. It is a model, not an observation, because only one inspection cycle is published.

Segments with at least one modelled year: 4,272. Inspection years in the table: {np.int64(2014): 5, np.int64(2018): 2, np.int64(2019): 6, np.int64(2020): 3, np.int64(2021): 25, np.int64(2023): 1971, np.int64(2024): 2339, np.int64(2025): 939} (a rolling survey, roughly a third of the network per year).

Loss per year by class (lane-mile weighted mean, with spread):
| func               |   segments |   mean |   p10 |   median |   p90 |
|:-------------------|-----------:|-------:|------:|---------:|------:|
| Arterial           |          7 |   2.72 |   0   |      2.9 |  3.04 |
| Collector          |        434 |   2.86 |   0   |      3.4 |  4.73 |
| Local              |       3672 |   2.79 |   0.9 |      3.3 |  3.8  |
| Local - Industrial |        159 |   2.56 |   0.9 |      3.1 |  3.8  |

Loss per year by the segment's measured condition band:
| band_measured      |   segments |   mean |   median |   p90 |
|:-------------------|-----------:|-------:|---------:|------:|
| Poor (0-39)        |       1064 |   3.41 |     3.4  |  3.6  |
| Fair (40-59)       |        970 |   3.89 |     3.8  |  4.1  |
| Good (60-79)       |       1321 |   2.87 |     2.95 |  3.65 |
| Excellent (80-100) |        917 |   0.98 |     0.9  |  2.05 |

Reading: the Oct 8 report's flat 3 points per year is close to the network mean, but the City's curve is steeper for segments already in Fair or Poor and flatter for Excellent segments. A projection that uses one rate for all segments will understate how fast the bad roads get worse and overstate how fast good roads decline.

## C. Treatment effect observed on FY2025 work

Segments planned for FY2025 (July 2024 to June 2025) show a different value on the June 2026 map than in the July 2025 table, and no other segments do. So the map was updated after the FY2025 work was accepted. Comparing the pre-work inspection reading with the post-work map value gives the City's own post-treatment score.

| plan_cat   |   segments |   lane_mi |   share_updated |   pre_measured_median |   post_map_median |   gain_median_updated_only |   post_map_median_updated_only |
|:-----------|-----------:|----------:|----------------:|----------------------:|------------------:|---------------------------:|-------------------------------:|
| MILL_MICRO |         39 |      14.8 |             0   |                  95.9 |              95.9 |                      nan   |                          nan   |
| MILL_OL    |        746 |     157.6 |             0.6 |                  49.6 |              96.1 |                       57.7 |                           96.1 |
| SEAL_COAT  |        296 |      79.8 |             0.6 |                  77   |              81.4 |                        8   |                           80.2 |
| SLURRY     |         12 |       7.6 |             1   |                  76.2 |              92.4 |                       16.6 |                           92.4 |

Reading: mill and overlay resets a segment to about 96 (the Oct 8 report assumed 95: confirmed). Seal coats on updated segments gain a median 8 points (the report assumed 10), but only 60% of FY2025 seal-coat segments were updated at all; the rest may be unrecorded or RoadMatrix may treat a seal as a life extension rather than a score jump. Micro-mill segments were already in the mid-90s at inspection, so their effect cannot be read here. Confirm both points with the City (interview question 2).

## D. Planned program FY2026 to FY2028 against today's condition

Planned segments FY2026-2028: 3,110 (306.6 centerline miles, 762 lane-miles), 62% of city lane-miles. The City calls this a tentative schedule that depends on a funding plan not yet approved.

|                            |   segments |   centerline_mi |   lane_mi |   pqi_now_median |
|:---------------------------|-----------:|----------------:|----------:|-----------------:|
| (2026, 'Mill and overlay') |        795 |            74.3 |     165.7 |             30.5 |
| (2026, 'Reconstruction')   |          2 |             0.8 |       1.6 |             41   |
| (2026, 'Surface seal')     |        542 |            55.4 |     130.3 |             70.2 |
| (2027, 'Mill and overlay') |        722 |            65.9 |     168.3 |             42.6 |
| (2027, 'Surface seal')     |        346 |            36.3 |     119.3 |             69.8 |
| (2028, 'Mill and overlay') |        475 |            46.5 |     100.2 |             48.3 |
| (2028, 'Surface seal')     |        228 |            27.6 |      76.6 |             81.2 |

Does the plan reach the roads that need it? Current band of city lane-miles by plan status:
| band_now           |   Done FY2025 |   No plan |   Planned FY2026-28 |   total |   share_unplanned |
|:-------------------|--------------:|----------:|--------------------:|--------:|------------------:|
| Poor (0-39)        |           9.5 |       1.5 |               186.6 |   197.6 |               0   |
| Fair (40-59)       |          18   |       4.1 |               163.3 |   185.4 |               0   |
| Good (60-79)       |          43.3 |      76.5 |               252.9 |   372.7 |               0.2 |
| Excellent (80-100) |         189   |     122.3 |               159   |   470.2 |               0.3 |

Gap list: 25 segments, 2.4 centerline miles, 6 lane-miles are Poor or Fair today with no planned treatment through FY2028. By class:
| func               |   segments |   lane_mi |   pqi_median |
|:-------------------|-----------:|----------:|-------------:|
| Arterial           |          3 |       1   |         56.4 |
| Collector          |          2 |       0.9 |         37.2 |
| Local              |         18 |       2.9 |         52.2 |
| Local - Industrial |          2 |       0.8 |         52.6 |

Full gap list written to data/processed/gap_segments_no_plan_below60.csv.

## E. Equity: condition by census tract income (the measure's own clause)

The target reads 'a citywide average of 70 across all demographic categories'. Tract median household income (ACS 2019-2023) is used as the available proxy; race and ethnicity tables can be added with the same join.

| income_q          |   tracts |   lane_mi | income_range         |   pqi_lane_weighted |   share_poor |   share_poor_or_fair |   share_planned_fy26_28 |   share_poor_fair_unplanned |
|:------------------|---------:|----------:|:---------------------|--------------------:|-------------:|---------------------:|------------------------:|----------------------------:|
| Q1 lowest income  |       18 |   387.888 | $26,995 to $72,282   |              70.619 |        0.126 |                0.276 |                   0.63  |                       0.031 |
| Q2                |        8 |   255.624 | $74,380 to $93,333   |              64.71  |        0.216 |                0.353 |                   0.733 |                       0.006 |
| Q3                |        8 |   279.505 | $93,825 to $124,048  |              68.221 |        0.142 |                0.332 |                   0.569 |                       0     |
| Q4 highest income |        6 |   260.57  | $126,310 to $177,750 |              69.497 |        0.205 |                0.329 |                   0.556 |                       0.011 |

Tracts below the 70 target today (lane-mile weighted): 20 of 40. Lowest five:
|    NAME |   median_hh_income |   lane_mi |   pqi_lane_weighted |   share_poor_or_fair |   share_planned_fy26_28 |
|--------:|-------------------:|----------:|--------------------:|---------------------:|------------------------:|
| 3194.03 |              93825 |     34.32 |               46.53 |                 0.75 |                    0.95 |
| 3192.01 |              51977 |     14.79 |               51.32 |                 0.67 |                    0.93 |
| 3199.09 |             147537 |     23.18 |               51.35 |                 0.7  |                    1    |
| 3191.01 |              26995 |      4.8  |               52.73 |                 0.56 |                    0.56 |
| 3194.04 |             100129 |     20.69 |               52.87 |                 0.63 |                    1    |

Correlation between tract income and tract PQI across 40 tracts: -0.03.

Character areas (the City's eight planning areas):
| area_name                                          |   lane_mi |   pqi_lane_weighted |   share_poor_or_fair |   share_planned_fy26_28 |
|:---------------------------------------------------|----------:|--------------------:|---------------------:|------------------------:|
| Alameda                                            |    240.41 |               58.61 |                 0.48 |                    0.68 |
| Downtown Tempe / Rio Salado /ASU/ NW Neighborhoods |    148.27 |               63.89 |                 0.37 |                    0.8  |
| Corona/South Tempe                                 |    209.76 |               65.81 |                 0.41 |                    0.7  |
| Apache                                             |     70.23 |               67.17 |                 0.37 |                    0.66 |
| Southwest Tempe                                    |    148.13 |               69.35 |                 0.28 |                    0.64 |
| Diablo/Double Butte                                |    107.24 |               71.46 |                 0.23 |                    0.7  |
| Papago/North Tempe                                 |     76.06 |               72.69 |                 0.29 |                    0.44 |
| Kiwanis/The Lakes                                  |    210.65 |               82.79 |                 0.05 |                    0.32 |

## F. Projection to FY2036 at segment level

Rules: each segment loses the City's median rate for its current band each year (section B). Segments planned for FY2026-2028 are treated in their planned year: mill and overlay or reconstruction resets to the observed post-work score (section C); a surface seal adds the observed seal gain and holds the segment at its current score for the seal's life (3 years, assumption). After FY2028 three scenarios: no further work; a preservation-only program that seals every segment that drops into Fair; and a continued program that also overlays every segment that drops into Poor.

|   year |   stop after FY2028 |   preserve (seal Fair) |   continue (seal Fair + overlay Poor) |   share Poor, stop |   share Poor, continue |   stop, two-tier 1/3 pts (Oct 8 rule) |   preserve, two-tier 1/3 pts |   stop, FY2028 tranche unfunded |
|-------:|--------------------:|-----------------------:|--------------------------------------:|-------------------:|-----------------------:|--------------------------------------:|-----------------------------:|--------------------------------:|
| 2026   |              68.579 |                 68.579 |                                68.579 |              0.161 |                  0.161 |                                68.579 |                       68.579 |                          68.579 |
| 2026.5 |              77.512 |                 77.512 |                                77.512 |              0.071 |                  0.071 |                                77.512 |                       77.512 |                          77.512 |
| 2027   |              83.654 |                 83.654 |                                83.654 |              0.04  |                  0.04  |                                83.489 |                       83.489 |                          83.654 |
| 2028   |              86.726 |                 86.726 |                                86.726 |              0.022 |                  0.022 |                                86.39  |                       86.39  |                          82.42  |
| 2029   |              85.748 |                 86.114 |                                87.669 |              0.023 |                  0     |                                85.276 |                       85.663 |                          81.156 |
| 2030   |              84.572 |                 85.339 |                                86.951 |              0.025 |                  0     |                                83.909 |                       84.671 |                          79.684 |
| 2031   |              83.195 |                 84.454 |                                86.125 |              0.028 |                  0     |                                82.332 |                       83.552 |                          77.995 |
| 2032   |              81.682 |                 83.62  |                                85.349 |              0.034 |                  0     |                                80.621 |                       82.459 |                          76.241 |
| 2033   |              80.122 |                 82.785 |                                84.572 |              0.041 |                  0     |                                78.876 |                       81.477 |                          74.435 |
| 2034   |              78.508 |                 81.79  |                                83.634 |              0.052 |                  0     |                                77.109 |                       80.532 |                          72.564 |
| 2035   |              76.855 |                 80.838 |                                82.734 |              0.071 |                  0     |                                75.31  |                       79.374 |                          70.659 |
| 2036   |              75.162 |                 79.94  |                                81.885 |              0.093 |                  0     |                                73.497 |                       78.402 |                          68.724 |

If the FY2028 tranche of the plan is never funded and nothing follows: 2036 value 68.7, below 70 from 2036.
Year the citywide average falls below 70 with no work after FY2028: not before 2036 under the City's band-specific curve; not before 2036 under the Oct 8 report's two-tier rule (1 point a year at 85 and above, 3 below). The conclusion about post-bond funding depends on which deterioration curve is right, so this is the first thing to confirm with the City.

Post-FY2028 work in the 'continue' scenario, FY2029-2036: 29 lane-miles overlay and 275 lane-miles seal, about $7M over eight years at Tempe's 2022 unit costs ($50k overlay, $20k maintenance per lane-mile), roughly $1M a year. 'Preserve' alone: 275 lane-miles seal, about $0.7M a year.

Reading: the bond program lifts the network above 70 by FY2028 in every scenario; what happens after decides whether 70 holds to FY2036. Unit costs are from a 2022 vendor publication quoting the City's own curve and must be confirmed; the seal gain is the small observed value, so the 'preserve' line is conservative.
