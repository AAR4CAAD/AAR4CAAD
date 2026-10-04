# CONTROL: how it was built, re-executed from the platform algorithm (verification run, October 2026)

> Reference values in the *reported* columns are those of the manuscript version under verification (revision 12, 3 October 2026); the final manuscript (revision 16) adopted the recomputed values and wording. See `../README.md`.

Stored parameters (control_dataset.csv): method `MatchedControl`, matching variables `BuildingType,Style`, seed `345145722`, reference `AESTHETIC-v1`, reference images excluded from the pool `True`. Pool = active photographs not in AESTHETIC-v1 (511), ordered by image_asset_id, shuffled once with xoshiro256**(SplitMix64(345145722)).

## Re-execution

- Same 89 photographs: **True**; same order (sort_order 0–88): **True**; same recorded reasons: **True**.
- v1 and v2 datasets have identical membership and order (v2 only re-snapshots the captions): True.
- The export carries the current BuildingType/Style; the audit log has no metadata-edit event for photographs after import, so the strata used here are those of 2026-09-27 13:39 UTC.

## What the algorithm does — and does not do

`SampleControl(MatchedControl)` matches **stratum counts**, not photographs: for every stratum `BuildingType | Style` of the 89 AESTHETIC photographs (ordered by key) it takes the same number of pool photographs from that stratum (in shuffled order); strata with a deficit are refilled by `BuildingType` alone; the remainder is random. **No photograph-to-photograph pairing is created or stored**: the '1:1 matching' of the manuscript and the '61 pairs' of the previous reply do not correspond to any recorded object. The recoverable unit is the stratum. Row order (`sort_order`) is the order of the strata by key, not a pairing.

| CONTROL subgroup | n | AESTHETIC photographs sharing the stratum | post-1990 | Europe | industrial |
|---|---|---|---|---|---|
| type_and_style | 20 | same type and style | 10 | 7 | 1 |
| type_only | 41 | same building type | 20 | 16 | 6 |
| random_fill | 28 | none (random) | 10 | 15 | 8 |

AESTHETIC has 85 distinct type+style strata; 19 could be matched completely in the pool; the deficit of 69 photographs was refilled by type (41) and at random (28). AESTHETIC photographs with at least one CONTROL in their exact stratum: 20 of 89; with at least one CONTROL of the same type (relaxed strata): 63.

## Composition (whole sets)

- Period, post-1990: AESTHETIC 50 vs CONTROL 40 (of 89 each). Europe: 28 vs 38. Industrial: 10 vs 15.
- Tab. 1 recomputed: {"AESTHETIC": {"periods": [8, 19, 12, 27, 23], "countries": 37, "europe": 28, "types": 49, "industrial": 10, "licences": 9, "ccbysa4": 41}, "CONTROL": {"periods": [15, 22, 12, 23, 17], "countries": 33, "europe": 38, "types": 47, "industrial": 15, "licences": 11, "ccbysa4": 40}}.
- Period and area are NOT matching variables; type and style are matched only for the stratum-count subgroups. The review's observation that 'exact 1:1 matching would give identical type distributions' is correct; the recorded procedure never promised that.

## Consequence for the manuscript

Replace 'abbinate 1:1 per tipologia e stile' with: 'controllo di pari numerosità (89) estratto dalle fotografie non selezionate, con riproduzione dei conteggi per strato tipologia×stile dove possibile (20 fotografie), rilassato alla sola tipologia (41) e completato a caso (28); seed 345145722'. Period and geography were not controlled (sensitivity in `report_direction_adjusted.md`).

