# Verification and sensitivity analyses (basis of manuscript revision 16)

This folder contains the independent re-analysis of the study and the sensitivity analyses whose results are reported in the manuscript (revision 16, 4 October 2026): every number of the paper was recomputed from the export and from the stored matrices, and the new analyses requested during review were run here. Nothing historical (data, frozen datasets, training runs, earlier reports in `../analysis/`) was modified. All new analyses are post-review and exploratory; their specifications were written before computing the results (`outputs/SPEC_direzione_aggiustata.json`, `integrazione/SPEC_dino_aggiustamento_completo.json`).

How it was produced: a first verification pass on an earlier manuscript version (revision 12), an external check of that pass with two corrections (bootstrap multiplicity, variance-component labels), and a targeted integration (adjustment for building type and style, complete Table 3, captions v1→v2, hardware). The process documents of those passes — written for the authors, with the wording of the earlier revisions — are kept unchanged in `history/`; the current results are in `outputs/` and `integrazione/`.

## What is where

| folder / file | content |
|---|---|
| `outputs/` | reproduction of the manuscript's numbers and first-pass sensitivities: human statistics (`report_human.md`, `human_reproduction.csv`, `human_sensitivities.csv`), CONTROL re-execution (`report_control.md`, `control_construction.csv`), DINOv2 (`report_dino.md`, `dino_*.csv`), descriptors (`report_descriptors.md`, `descriptors_*.csv`), captions (`report_captions.md`, `caption_*.csv`), training runs and chronology (`report_runs_timeline.md`, `runs_all.csv`, `timeline_full.csv`), documentation items (`report_documentation.md`), inventory of inputs with hashes (`INVENTARIO_INPUT.csv`), blind material for a second screening (`second_screening/`, key withheld) |
| `integrazione/` | targeted integration: DINOv2 direction adjusted for period + area + type + style in two geometries (`dino_aggiustamento_completo.csv`, `report_dino_aggiustamento_completo.md`), reproduction of the authors' local tables and rater-resampling stability of the selection (`verifica_tabelle_locali.csv`, `stabilita_*.csv`), captions v1→v2 transitions (`caption_v1_v2_*.csv`, `report_caption_v1_v2.md`), complete Table 3 (`tabella3_completa.csv`, `report_tabella3.md`), hardware / LoRA inference scale / chronology (`report_hardware_calendario.md`), input hashes (`HASH_INPUT.txt`) |
| `PROTOCOLLO_CAPTION_CONTROLLATE.md`, `config_caption_controllate.json`, `scripts/a10_caption_control_analysis.py` | protocol of the controlled-caption experiment (identical neutral caption for both corpora); prepared and dry-run tested, **not executed** |
| `scripts/` | all code (`a0*` first pass, `b0*` integration, `common.py`); `logs/` run logs; `env/` Python 3.14.3 and package versions |
| `inputs/previous_reply/` | attachments of an earlier technical reply (derived data: lexicon, control strata, prompts, timeline) used for comparison |
| `inputs/integrazione_mirata/` | the authors' local verification package (per-photograph statistics, rater bootstrap, ICC, batches, binomial, out-of-training check) reproduced in `integrazione/` |
| `history/` | process documents of the verification passes (point-by-point replies, closure table, value-by-value reproduction table, proposed wording), referring to earlier manuscript revisions; superseded by revision 16 |

In the `reported` columns of `outputs/*reproduction.csv` and in the `report_*.md` files, the reference values are those of the manuscript version under verification (revision 12); revision 16 adopted the recomputed values, so they coincide with the final paper unless the report says otherwise. `PAPER_MAP.md` at the root maps every statement of revision 16 to its file.

## Re-running in this repository

The scripts read `../data/export/` by default (anonymised export: random participant identifiers, relative timestamps, rare roles aggregated), `../analysis/metrics/*.npz|csv`, `../analysis/baseline/direction_dinov2.npz` and `../analysis/vlm/images/`. Re-run on 4 October 2026 in this layout: `a00`–`a05`, `a09`, `b01`–`b05`, `a10 --dry-run` reproduce the same estimates as the run on the complete export; bootstrap limits differ by Monte Carlo error only (the random participant identifiers change the resampling order; e.g. two-way bootstrap of the rating contrast −0.024/+0.235 vs −0.025/+0.233). `a06_runs_timeline.py` and `a07_documentation.py` need the complete platform audit log, which contains participant-level events and is not redistributed: their outputs, produced on the complete export, are in `outputs/`.

```
# Python 3.14.3; packages in env/requirements_frozen.txt; set ARCH300_EXPORT=<zip> to use a complete export
set PYTHONIOENCODING=utf-8
cd audit/scripts
python a00_inventory.py && python a01_human.py && python a02_control_matching.py && python a03_dino.py && python a04_descriptors.py && python a05_captions.py && python b01_dino_adjust_full.py && python b02_verifiche_locali.py && python b03_caption_v1_v2.py && python b05_tabella3.py && python a09_deliverables.py
```

Bootstrap seeds: 20261003 (`common.SEED`, first pass and Table 3) and 20261004 (`b01`, `b02`). `a09_deliverables.py` rebuilds the value-by-value reproduction table and the closure table into the audit root; the versions kept for reference are in `history/`.

## Distribution

The key of the blind second-screening material is withheld until the screening is complete. Hashes of every file of the repository: `../SHA256SUMS.txt`. No credentials, no personal data beyond the anonymised export.
