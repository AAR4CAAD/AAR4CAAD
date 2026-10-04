# From the manuscript to the files (manuscript revision 16, 4 October 2026)

Paths are relative to the root of the repository. "Export" is `data/export/` (anonymised copy). Audit outputs are in `audit/outputs/`, the post-audit integration in `audit/integrazione/`. Every value below was recomputed from the export and the matrices by the scripts named in the last column.

## Abstract and Section 3 — Corpus and method

| Manuscript | Statement | File |
|---|---|---|
| Abstract, 3.1 | 600 photographs, 166 participants, 23,012 ratings; 89 AESTHETIC; 89 CONTROL "per strati progressivamente rilassati" | export `pretraining_ratings.csv`, `aesthetic_dataset.csv`, `control_dataset.csv`; `audit/outputs/report_control.md` |
| 3.1 | two batches of 300 imported 25 and 26 Sep 2026; 18,143 ratings from 166 and 4,869 from 54; 43/46 and 46/43 AESTHETIC/CONTROL per batch | export `source_images.csv` (`corpus_batch`, `imported_at`); `audit/inputs/integrazione_mirata/04_conteggi_per_lotto.csv`; `audit/integrazione/verifica_tabelle_locali.csv` (section `lotti`) |
| 3.1 | 76 countries, 264 European, 78 industrial, no author more than 7 times | export `image_metadata.csv` |
| 3.1 | roles 63/58/8/8/29; rule ≥10 ratings, mean ≥5, top 35% of eligible; percentile non-binding for 30–40% | export `participants.csv`, `selection_rules.json`; `audit/outputs/human_reproduction.csv` (section `selection`); `analysis/human_report/report_selection_rule.md` |
| 3.1 | rater bootstrap "senza imporre 89 selezionati" | `audit/integrazione/stabilita_bootstrap_riprodotta.csv`, `stabilita_inclusione_per_foto.csv`; `audit/inputs/integrazione_mirata/01_stabilita_bootstrap.csv` (authors' run); script `audit/scripts/b02_verifiche_locali.py` |
| 3.2, Tab. 1 | CONTROL: 511-photograph pool, xoshiro256** seed 345145722, 20 type+style / 41 type / 28 random; periods 8/19/12/27/23 vs 15/22/12/23/17; 37/28 vs 33/38 countries/European; 49/10 vs 47/15 types/industrial | `audit/outputs/report_control.md`, `control_construction.csv`, `control_composition.csv`; algorithm `training/platform/TrainingDatasetService.cs`, `DeterministicRandom.cs`; port `audit/scripts/a02_control_matching.py` |
| 3.2, Tab. 1 | captions present/modified v1→v2: 89/89 and 89/62; 27 unchanged keep the v1 review timestamp; two accounts; tool not recorded | `audit/integrazione/report_caption_v1_v2.md`, `caption_v1_v2_copertura.csv`; export `aesthetic_dataset.csv` / `control_dataset.csv` (`caption_snapshot`), `captions.csv` |
| 3.3 | SDXL base 1.0 revision; LoRA on to_q/k/v/out.0, frozen text encoders; rank=alpha=16, lr 1e-4, batch 1, 1,500 steps, 1024 px, fp16, noise offset 0.0357, timestep min 250; LoRA weight 1.0; NVIDIA L4, Python 3.10.12, torch 2.4.1+cu121, diffusers 0.30.3, peft 0.12.0 | `training/aar_worker.py`, `training/README.md`; export `training_runs.csv`, `generated_images.csv` (`generation_parameters_json`); `audit/integrazione/report_hardware_calendario.md`; `audit/outputs/runs_all.csv`, `cloud_jobs.csv` |
| 3.3, Fig. 1 | twelve references (six per repertoire), selection rule, credits and licences | `analysis/figures/fig_repertoires.png`, `fig_repertoires_credits.csv`; script `analysis/figures_repertoires.py` |
| 3.3 | four successive configurations; seeds 1254/9865 constant; RUN-4 before phase 2; prompts frozen after 292 trial images; timeline | `audit/outputs/report_runs_timeline.md`, `runs_all.csv`, `timeline_full.csv`; `protocol/timeline_from_audit_log.csv` |
| 3.3 | 48 prompts × 4 seeds (25478, 85, 6127, 7); 1216×832, DPM++ 2M Karras, guidance 5, 40 steps; prompt A04 | `protocol/generation_prompts.csv`; export `generation_plan.csv`, `prompt_sets.csv` |
| 3.3 | phase 1 ends 27 Sep 13:35 UTC; first phase-2 rating 28 Sep 15:33; last rating 1 Oct 11:55:54; closure 12:52:27 | `audit/outputs/timeline_full.csv`; `audit/integrazione/report_hardware_calendario.md` |
| 3.3 | paired seeds 1254, 9865, 42160; six adapters, 192 cells each, same BASE | `analysis/replication/design.json`; export `training_runs.csv` (REP-*) |
| 3.4 | screening: 48 images (21/14/13), 159 triplets, 477 images; defect categories | export `generated_images.csv` (`review_defects`, `excluded_by_review_rule`); `audit/outputs/report_runs_timeline.md` §3 |
| 3.4 | phase 2: 158 participants, 9,413 ratings (15–22 per image), 4,736 comparisons, 726 ties, 4,010 decisive; 32 linked, 16/99/11 | export `posttraining_ratings.csv`, `pairwise_trials.csv`, `participants.csv`; `audit/outputs/human_reproduction.csv` (section `perimeters`) |
| 3.4 | global filter: 18 excluded (12 incompleteness, 3 automatic speed rule, 3 other); 164/22,712 vs 166/23,012; subsets 161 and 159 | `audit/integrazione/report_tabella3.md` (definitions); `audit/outputs/human_sensitivities.csv` |
| 3.5, eq. 1–3 | g, d, u; P, R; S = d·P; ΔD definition; centroid distance | `analysis/baseline/direction_dinov2.npz`, `analysis/baseline/freeze.py`; `audit/outputs/dino_reproduction.csv` (identities); `audit/scripts/a03_dino.py` |
| 3.6 | the 31 descriptors (names, blocks, CLIP prompts), standardisation on the 600 photographs | `analysis/image_scripts/covariates.py`; `analysis/metrics/covariates_images.csv` |
| 3.6 | adjustment: additive regressions on period, area, type (35 + rare), style (41 + rare); G2 projector; G1 alternative | `audit/integrazione/SPEC_dino_aggiustamento_completo.json`, `dino_aggiustamento_completo.csv`, `report_dino_aggiustamento_completo.md`; script `audit/scripts/b01_dino_adjust_full.py` |
| 3.6 | caption lexicon (28 descriptors, negations, strict vs extended curves, 13 informative variables) | `audit/inputs/previous_reply/caption_lexicon_v1.json`; `audit/outputs/report_captions.md`, `caption_lexical_vs_visual.csv`, `caption_definition_variants.csv` |
| 3.7 | ICC estimator (one-way ANOVA on rater-centred scores, k₀ = 38.332), rater bootstrap, mixed model, Davidson, two-way bootstrap, prompt bootstrap, binomial | `audit/outputs/report_human.md` (Definitions); `audit/integrazione/verifica_tabelle_locali.csv` (section `icc`); scripts `audit/scripts/a01_human.py`, `b05_tabella3.py` |

## Section 4 — Results

| Manuscript | Statement | File |
|---|---|---|
| 4.1 | means 5.295 / 4.211; within-image SD 1.444 / 1.556; 14–64 ratings, SE 0.153–0.487 per AESTHETIC photograph | `audit/outputs/human_reproduction.csv` (`phase1`); `audit/inputs/integrazione_mirata/03_fase1_per_89_aesthetic.csv`, `02_fase1_per_600_foto.csv` |
| 4.1 | ICC(1) = 0.138, ICC(k₀) = 0.860; ρ = 0.425 (599), 0.496 (600) | `audit/integrazione/verifica_tabelle_locali.csv`; `audit/outputs/human_reproduction.csv` |
| 4.1 | bootstrap: 101.4 selected (72–135), 79.4% recovered, Jaccard 0.592, inclusion 0.506–1.000 (median 0.801) | `audit/integrazione/stabilita_bootstrap_riprodotta.csv`, `stabilita_inclusione_per_foto.csv` |
| 4.1 | ρ = 0.397 on the 422 photographs outside the LoRA sets | `audit/integrazione/verifica_tabelle_locali.csv` (`fuori_training`) |
| 4.1, Fig. 2 | three cells at min / median / max of P (A07/6127, C14/25478, A08/7) | `analysis/embedding_report/triplet_transfer_dino.csv`; `audit/outputs/dino_reproduction.csv`; images `analysis/vlm/images/<opaque_id>.jpg` via export `generated_images.csv` |
| 4.2 | d = 0.23523; P A−C = +0.0429 [+0.0275; +0.0599], 18.2% [11.7–25.5%]; A−BASE +0.0443; C−BASE +0.0014; 98/159 positive; 192 cells +0.0415 | `audit/outputs/dino_reproduction.csv`; `analysis/embedding_report/report_dino.md` |
| 4.2, Tab. 2 | per seed +0.0435/+0.0412/+0.0504 (R 0.185/0.175/0.214); G2 complete +0.0148/+0.0089/+0.0106 (R 0.147/0.088/0.106); mean R 19.2% → 11.4%; d_T = 0.1005; 87 directions, 57.4% variance | `audit/integrazione/dino_aggiustamento_completo.csv` (geometry G2, direction iii) |
| 4.2, Fig. 3 | ΔD original geometry: −0.0148/−0.0081/−0.0095; own−other −0.0111/−0.0112/−0.0085 | `audit/outputs/dino_distance_changes.csv`, `dino_centroid_distance_changes.csv`; figure `analysis/figures/fig_dino_distance_changes.png` (`analysis/figures_distances.py`) |
| 4.2 | ΔD after G2: −0.0119 / +0.0000 / −0.0049; own−other −0.00140 / −0.00048 / −0.00090; CONTROL −0.00111/−0.00103/−0.00093 | `audit/integrazione/dino_aggiustamento_completo.csv` (quantities "ΔD …", direction iii) |
| 4.2 | dispersion 0.906 vs 0.921 (−0.015; −0.039/+0.007); pooled RMS 0.916; d/dispersion 0.257; 0.047 | `audit/integrazione/verifica_tabelle_locali.csv` (`dispersione`) |
| 4.3, Fig. 4 | r(x, a−c) = 0.707 (0.537–0.790), 27/31 same sign; r(x,a) = −0.006; r(x,c) = −0.427; 26 shared signs, 0.82; covariance decomposition | `audit/outputs/descriptors_reproduction.csv`, `descriptors_profile.csv`, `report_descriptors.md`; figure `analysis/figures/fig_source_contrasts_three_panels.png` (`analysis/figures_transfer.py`) |
| 4.3 | descriptor-space distances: AESTHETIC per-image CI include zero, CONTROL reduces in three seeds; centroid CI negative in one seed | `audit/outputs/descriptors_distance_changes.csv`, `descriptors_centroid_distance_changes.csv` |
| 4.3 | strata: r = 0.026 (20 type+style, 19 strata), 0.632 (41 type, 25 strata), 0.434 (61), 0.709 (28 random vs all AESTHETIC) | `audit/outputs/descriptors_by_stratum.csv` |
| 4.4 | curves 37/27 (20/14 strict), concrete 17/27, water 28/10, greenery 55/55; lexical vs photographic 0.57 (−0.01/+0.90), vs outputs 0.32 (−0.11/+0.70) | `audit/outputs/report_captions.md`, `caption_lexical_vs_visual.csv`, `caption_definition_variants.csv`; transitions `audit/integrazione/caption_v1_v2_transizioni.csv` |
| 4.5, Tab. 3 | all human contrasts by method; 677/1,320 (51.29%; 48.55–54.02%; p 0.3637); without global filter +0.130 (n 167); < 1 s removed +0.120 | `audit/integrazione/tabella3_completa.csv`, `report_tabella3.md`; `audit/outputs/human_sensitivities.csv` |
| 4.5 | ρ(P, Δ rating) = 0.233 (0.089/0.378); ρ(P, pairs) = 0.037; linked/unlinked −0.116 (−0.289/+0.056) | `audit/outputs/dino_reproduction.csv`, `human_reproduction.csv` |

## Declarations and historical analyses

| Manuscript | File |
|---|---|
| participation and ethics; consent text | `protocol/consent_text.md`; `protocol/TRANSPARENCY_NOTES.md`, section 6 |
| data availability | this repository; `ANONYMISATION.md` |
| VLM evaluation (not in the body of revision 16; audit material) | `analysis/vlm_report/`, `analysis/vlm/` |
| exploratory analyses of the earlier revisions (decomposition of the source direction, residual direction, VLM) | `analysis/decomposition_report/`, `analysis/embedding_report/`, `analysis/replication_report/` |
| independent audit of revision 12 and its second pass | `audit/RISPOSTA_REVIEWER.md`, `audit/CORREZIONI_SECONDO_PASSAGGIO.md`, `audit/RIPRODUZIONE_PRECEDENTI.csv`, `audit/TABELLA_CHIUSURA.csv` |
| integration after the audit (basis of revision 16) | `audit/integrazione/RISCONTRO_INTEGRAZIONE.md` |

## Notes

- **Roles in the anonymised export.** Professional roles declared by fewer than ten participants overall are merged into `Other` in `participants.csv` (see `ANONYMISATION.md`); the manuscript reports 29 participants "in altre categorie".
- `audit/PATCH_MANOSCRITTO.md` and `audit/integrazione/SOSTITUZIONI_MIRATE.md` are the wording proposals that preceded revision 16; they are kept as history and are superseded by the manuscript.
- Intervals in the manuscript come from bootstrap draws; a re-run on the anonymised export (random participant identifiers) reproduces every estimate and shifts bootstrap limits by Monte Carlo error only (`audit/README.md`).
