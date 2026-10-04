# Supplementary material — anonymous version for peer review

*From curated references to the generated image: transfer of human preferences in the fine-tuning of diffusion models
for architectural images* (pilot study)

Published at https://github.com/<redacted>/<redacted> (manuscript revision 16). Data, code, protocol and every result behind the manuscript, prepared for double-blind review. Nothing here identifies
the participants or the authors (see [ANONYMISATION.md](ANONYMISATION.md)).
[PAPER_MAP.md](PAPER_MAP.md) links every section, table, figure and number of the manuscript to the file that supports it.

## The study in six lines

1. **Phase 1.** 164 participants rated 600 Wikimedia Commons photographs of documented architecture on a 1–7 scale
   ("How aesthetically successful do you consider this architecture?"): 22,712 valid ratings.
2. **Two training sets of 89 photographs.** AESTHETIC: photographs selected by a preference rule (at least 10 ratings,
   mean at least 5, top 35%), defined after phase 1 and frozen before the datasets were built; not preregistered.
   CONTROL: 89 photographs not selected, drawn with a fixed seed so as to reproduce the stratum counts of AESTHETIC by
   building type × style where possible (20 photographs), by building type alone (41), and at random (28): there is no
   photograph-to-photograph pairing (`audit/outputs/report_control.md`). The treatment is
   *preference-guided*: the rule has no threshold on the dispersion of the ratings, so consensus is described, not manipulated.
3. **Two LoRA adapters** of Stable Diffusion XL, one per set, with the same settings; BASE is the unmodified model.
4. **Generation.** 48 prompts × 4 seeds × 3 conditions = 576 images; after a quality rule applied to whole triplets, 159
   of the 192 triplets (477 images) form the primary set.
5. **Phase 2.** 158 participants, blind to the condition: 9,413 valid ratings and 4,736 pairwise comparisons (4,010 decisive).
6. **Exploratory probes:** DINOv2 embeddings, 31 image-derived covariates (10 photographic measures, 21 CLIP zero-shot
   attributes), three vision-language models (VLM), and a post-hoc sensitivity with three paired training seeds.

The study concerns **images**: two-dimensional representations of architecture, not built form.

## Integrative materials not reported in full in the paper

Besides the data and code behind every number of the manuscript, the repository holds materials that the paper only summarises: the covariance decomposition of the 31 descriptor contrasts (`audit/outputs/report_descriptors.md`, `descriptors_profile.csv`), the lexical transition tables of the captions v1 → v2 (`audit/integrazione/caption_v1_v2_transizioni.csv`), the detailed per-photograph counts of phase 1 (`audit/inputs/integrazione_mirata/02_fase1_per_600_foto.csv`, `audit/integrazione/stabilita_inclusione_per_foto.csv`), the sensitivity analyses with their scripts (`audit/scripts/`, `analysis/*.py`: adjusted DINOv2 directions, crossed-effects and two-way bootstrap models, Davidson model, rater-resampling stability of the selection), the complete Table 3 (`audit/integrazione/tabella3_completa.csv`) and the figure of the two repertoires with photo credits (`analysis/figures/fig_repertoires*.{png,pdf,csv}`).

## Independent audit after the first review

The folder [`audit/`](audit/README.md) contains the independent re-analysis carried out after the first review: every number of the manuscript recomputed from the export (`audit/RIPRODUZIONE_PRECEDENTI.csv`), the exact re-execution of the CONTROL sampling, the chronology of all training runs, the decomposition of the descriptor covariances, the distances to the two corpora in both probe spaces, the direction adjusted for period and area, the crossed-effects and two-way bootstrap sensitivities of the human contrast, the caption audit, and the protocol of the controlled-caption experiment (not yet run). [`REVIEWER_GUIDE.md`](REVIEWER_GUIDE.md) maps each point of the review to the evidence. The audit's conclusions are in `audit/RISPOSTA_REVIEWER.md`; what remains open is in `audit/MATERIALI_O_DECISIONI_MANCANTI.md`.

## Where to look

| You want to check… | Go to |
|---|---|
| which file supports a statement of the manuscript | [`PAPER_MAP.md`](PAPER_MAP.md) |
| the evidence for each point of the review | [`REVIEWER_GUIDE.md`](REVIEWER_GUIDE.md), [`audit/`](audit/README.md) |
| what was planned, when, and what changed | [`protocol/`](protocol/README.md) |
| what is not preregistered and the other limits, stated by the authors | [`protocol/TRANSPARENCY_NOTES.md`](protocol/TRANSPARENCY_NOTES.md) |
| the human data | [`data/`](data/README.md) |
| the analyses, their code and how to re-run them | [`analysis/`](analysis/README.md) |
| how the adapters were trained and the images generated | [`training/`](training/README.md) |
| the images | `analysis/vlm/images/` (the 576 images as shown to participants), `analysis/replication/images/` |

Every report has a companion CSV with all its numbers. Result files are named after their analysis.

## Results reported in the manuscript (revision 16)

| Result | Value | Source in this repository |
|---|---|---|
| Phase 1: low individual agreement, precise aggregate | ICC(1) 0.138; ICC(k₀) 0.860 (one-way ANOVA on rater-centred scores, k₀ = 38.3); SE per AESTHETIC photograph 0.153–0.487 | `audit/integrazione/verifica_tabelle_locali.csv` |
| Stability of the selection under resampling of the 166 raters | 101.4 photographs selected on average (72–135); 79.4% of the 89 recovered; Jaccard 0.592; inclusion probability of the 89: 0.506–1.000 | `audit/integrazione/stabilita_bootstrap_riprodotta.csv` |
| CONTROL construction | stratum counts: 20 type+style, 41 type only, 28 random (seed 345145722); exact re-execution | `audit/outputs/report_control.md` |
| Source direction outside the LoRA sets | Spearman ρ 0.397 with the mean rating of the 422 external photographs | `audit/integrazione/verifica_tabelle_locali.csv` |
| **Transfer along the source direction** | P A−C +0.0429 [+0.0275; +0.0599] = 18.2% of d on 159 triplets; +0.0435 / +0.0412 / +0.0504 on 192 cells for the three paired seeds (R 19.2% on average) | `audit/outputs/dino_reproduction.csv`; `audit/integrazione/dino_aggiustamento_completo.csv` |
| After removing the period/area/type/style directions from photographs and outputs (G2) | P +0.0148 / +0.0089 / +0.0106 (CI > 0); R 11.4% of the residual separation (d_T 0.1005; 87 directions, 57.4% of photograph variance) | `audit/integrazione/dino_aggiustamento_completo.csv` |
| Approach to the own repertoire (DINOv2, original geometry) | ΔD −0.0148 / −0.0081 / −0.0095; own − other −0.0111 / −0.0112 / −0.0085 (CI < 0); after G2 the own − other contrast is no longer consistent across seeds | `audit/outputs/dino_distance_changes.csv`; `analysis/figures/fig_dino_distance_changes.png` |
| 31 descriptors | r(x, a−c) 0.707; 27/31 same sign; r(x,a) −0.006; r(x,c) −0.427; within type+style strata r 0.026 | `audit/outputs/descriptors_profile.csv`, `descriptors_by_stratum.csv` |
| Captions | 37/27 curves (20/14 strict), 17/27 concrete, 28/10 water; v1→v2 additions concentrated in AESTHETIC | `audit/outputs/report_captions.md`; `audit/integrazione/caption_v1_v2_transizioni.csv` |
| **Human contrast, ratings: AESTHETIC − CONTROL** | +0.104 [+0.029; +0.178] (t, n = 158); +0.101 [+0.016; +0.186] (crossed mixed model); +0.104 [−0.019; +0.237] (two-way bootstrap) | `audit/integrazione/tabella3_completa.csv` |
| BASE − CONTROL; AESTHETIC − BASE | +0.140 [+0.068; +0.212]; −0.036 [−0.108; +0.035] | idem |
| Pairwise choices | OR A:C 1.090 [0.985; 1.206] (BT), 1.089 (Davidson; two-way 0.909–1.306); B:C 1.133; A:B 0.962; binomial 677/1,320 = 51.3% (marginal) | idem |

**Note on the human estimates.** The manuscript reports participant-level estimates: for each participant the mean
difference AESTHETIC − CONTROL over the images rated, then a one-sample t test on the 158 differences; Bradley–Terry odds
ratios for the decisive pairwise choices. `analysis/paper_human_estimates.py` recomputes them from the export and
`human_report/report_paper_participant_level.md` lists them: they coincide with the values of the manuscript.
`human_report/report_human_votes.md` is a second analysis of the same data with mixed models: close, not identical
estimates (AESTHETIC − CONTROL +0.100, 95% CI +0.034 / +0.166), same reading. Both reports also contain quantities that
the manuscript does not use (equivalence intervals, Davidson model, sample-size projections).

## Analyses in this repository that go beyond the manuscript

These were run in the same project and are included for completeness, whatever their outcome.

| Analysis | Result | Source |
|---|---|---|
| The 31 descriptors against BASE: do the adapters move towards the profile of their training set? | no. AESTHETIC − BASE is unrelated to the training difference (r = −0.01), CONTROL − BASE goes against it (r = −0.43); the two adapters move from BASE in the same direction for 26 of 31 descriptors. The r = 0.71 of the manuscript is a difference between two nearly parallel shifts, not a move of AESTHETIC towards its own photographs | `analysis/figures/feature_base_analysis.md`, figures in `analysis/figures/` |
| Does the percentile of the preference rule matter? | no: the photographs are selected by the mean threshold alone; the selected set is identical for any percentile between 20% and 50%, hence for the preliminary 33% and the final 35% | `human_report/report_selection_rule.md` |
| Determinism control: the AESTHETIC adapter trained twice with identical settings | different weights and different images, no systematic shift along the direction (distance 0.32, against 0.63 when only the training seed changes and 0.68 when only the corpus changes) | `replication_report/report_replication_dino.md`, 5 |
| Corpus effect against training-seed effect along the direction | ratio 4.8 | `report_replication_dino.md`, 2 |
| Details of the VLM evaluation on the paired seeds (subset fixed in advance: 24 prompts × 2 seeds × 6 adapters; contrasts by seed and by model) | between-seed differences as large as the corpus contrasts | `vlm_report/report_replication_vlm.md` |
| Words that differ between the captions of the two sets | more `green`, `sky`, `river` in AESTHETIC; more "eye-level perspective" in CONTROL | `decomposition_report/report_captions.md` |
| Equivalence intervals, Davidson model with ties, mixed models, sample-size projections for the human data | see the reports | `human_report/` |

## Status of the analyses

The study is a **pilot**. The primary endpoint is the human contrast AESTHETIC − CONTROL between the two final adapters,
which were trained as two independent workflows with distinct seeds: it compares two workflows, not the pure effect of
the corpus at a fixed seed. No prospective power calculation was made; a minimum detectable effect is reported a
posteriori. Embedding, covariate and VLM analyses were designed after the human data collection and are exploratory.
The sensitivity with three training seeds applied to both corpora is post hoc; its protocol and criterion were written
before the additional trainings (plan, section 8). It concerns the representational transfer only: **no participant saw
the images of the additional adapters.**

## What is not in this repository

- The **600 photographs**: third-party works under their own licences. `data/export/image_metadata.csv` gives source
  URL, author and licence of each; their embeddings and covariates are included.
- The **platform** used to collect the data (a web application): only the script that ran training and generation is
  included (`training/`), with the exports it produced.
- The **original PNG files** of the generated images: the repository holds the display version shown to the participants
  (JPEG, same size 1216×832) and the 480-px thumbnails used for the embeddings.
- The **weights** of the adapters (their SHA-256 are in `data/export/generated_images.csv`).
- The **version-control history**: this anonymous copy starts from a single commit. The dated history of the protocol
  can be shown to the editors on request.

## Reuse

Material provided for peer review. A licence will be attached to the public release that accompanies the published paper.
