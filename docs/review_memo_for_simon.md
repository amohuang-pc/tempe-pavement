# Review memo: 1.22 PQI report (Oct 8) and the data-side rebuild

From Amos, 2026-10-20. Repo: github.com/amohuang-pc/tempe-pavement (scripts 01 to 03 reproduce every number here). Full tables: outputs/analysis_tables.md. Narrative: docs/findings_round1.md.

## Short version

The report's structure is solid and I kept it. I pulled all four City layers row by row (5,127 segments) and joined them on the RoadMatrix id, which the grouped pull could not do. Three things change, three things get added, and one thing you flagged turned out fine.

**Changes**

1. Condition bands. The City's own map uses Poor 0-39, Fair 40-59, Good 60-79, Excellent 80-100. The report's 40/55/70/85 cuts and the "below 55" KPI are not official. Suggest switching every share to the official bands and making the second KPI "share of lane-miles in Poor" (16% today) or "Poor or Fair" (31%).
2. Insight 1 ("keeping it is hard"). At segment level, running the City's actual FY2026-28 list on the real segments, the network peaks near 87 in 2028 and is still 73 to 75 in 2036 with zero spending after the bond, under both your wear rule and the City's curve. The report's 69.3 came from (a) assuming half of FY2026 was already in the June snapshot (it is not: only FY2025 segments were updated on the map), (b) even spread within bands, and (c) centerline weighting. The one case that misses 70 is the FY2028 tranche never being funded (68.7 in 2036). So the message becomes: passing is certain, holding 70 is likely, but the plan is tentative and the Poor share climbs from 2% to 9% without a maintenance budget. Recommendation 1 survives; the deadline-miss framing does not.
3. Costs. Tempe's own cost curve was quoted in a 2022 vendor case study: $20k maintenance, $50k overlay, $160k rehab, $330k reconstruction per lane-mile. Use these instead of Littleton 2016 (seal $35k, overlay $320k), and note the ratio is very different: overlay is 2.5x maintenance in Tempe's curve, 9x in Littleton's, which changes Model D's answer. Lane-miles are now computed from the data (1,226), so the 2.47 factor is not needed.

**Additions**

4. Equity, which the target wording requires ("across all demographic categories"). By tract income there is no gradient (lowest-income quartile 70.6, highest 69.5, correlation -0.03). By geography there is a large one: Alameda 58.6 with 48% of lane-miles Poor or Fair; Kiwanis/The Lakes 82.8 with 5%. Twenty of forty tracts are below 70. This section also gives us the values alignment the report is missing (Diversity, Respect, Quality, Openness).
5. Treatment effects from Tempe data. FY2025 segments show the before and after: mill and overlay goes to 96 (your 95 is confirmed); seal coat moves 8 points on the 60% of segments that were updated and nothing on the rest. So seal +10 is slightly high and needs the City's answer.
6. Two maps (condition by segment; tract PQI with the 25 unplanned Poor/Fair segments).

**Confirmed**

7. The 2030 vs 2036 question: the Council's Nov 2025 index says FY 2035/36; the summary table's "2029-12-31" target row is stale. Your call to follow the Council document was right.
8. Lane factor: 1,200 miles in the bond coverage is lane-miles; the data gives 1,226, so your 2.47 was close.

## Definition notes worth putting in the report

- The map's score (`per_pqi_yr1`) is the City's modelled current-year value, updated when work is accepted; the only measured field is `MEASURED_PQI` in the detail table. Model B therefore recovers the City's wear curve, which you already said in the limitations; it should also be in the main text.
- The City's curve is not flat: median loss per year is 3.4 Poor, 3.8 Fair, 2.95 Good, 0.9 Excellent.
- The official average is most likely lane-mile weighted: the July 2025 detail table gives 64.7 that way (official 65) and 62.6 by centerline miles.
- Planned Road Resurfacings is described by the City as tentative and dependent on an unapproved funding schedule. Quote it as a plan.

## What I need from you

- Whether you want the report edited in place or a v2 with these sections, and who writes which part.
- A yes to sending the City six questions (docs/data_inventory.md section 5; isaac_chavira@tempe.gov is the dataset author, Ed Bond runs pavement management). The prior inspection cycle and the seal-coat effect are the two answers that would change the model most.
