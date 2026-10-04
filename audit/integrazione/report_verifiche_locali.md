# Verification of the author's local tables (AAR_integrazione_mirata) and out-of-training check

| section | quantity | package | recomputed | agree | note |
|---|---|---|---|---|---|
| fase1 | duplicate participant-photo pairs | 0 | 0 | True |  |
| fase1 | per-photo n_giudizi: max abs difference over 600 | 0 | 0.0 | True |  |
| fase1 | per-photo n_valutatori_distinti: max abs difference over 600 | 0 | 0.0 | True |  |
| fase1 | per-photo media: max abs difference over 600 | 0 | 0.0 | True |  |
| fase1 | per-photo sd_campionaria: max abs difference over 600 | 0 | 0.0 | True |  |
| fase1 | per-photo errore_standard_media: max abs difference over 600 | 0 | 0.0 | True |  |
| fase1 | 89 AESTHETIC: n range | 14-64 | 14-64 | True |  |
| fase1 | 89 AESTHETIC: SE range | 0.1533-0.4871 | 0.1533-0.4871 | True |  |
| regola | historical rule on the complete sample reproduces the 89 AESTHETIC (eligible-population percentile) | True | True | True | cutoff P65 = 4.562 (platform recorded 4.563) |
| regola | author's convention (percentile over all active images) gives the same 89 | True | True | True | cutoff 4.562; both non-binding because < 5 |
| stabilita | historical convention (eligible): mean cardinality | 100.939 | 101.375 | False | different seed and convention: compare distributions, not digits |
| stabilita | historical convention (eligible): cardinality quantiles 2.5/50/97.5 | [71.0, 100.0, 134.0] | [72.0, 101.0, 135.0] | False |  |
| stabilita | historical convention (eligible): mean recovery of the 89 | 0.788 | 0.7939 | False |  |
| stabilita | historical convention (eligible): mean Jaccard | 0.5877 | 0.5924 | False |  |
| stabilita | author's convention (all active): mean cardinality | 100.939 | 101.578 | False | different seed and convention: compare distributions, not digits |
| stabilita | author's convention (all active): cardinality quantiles 2.5/50/97.5 | [71.0, 100.0, 134.0] | [73.0, 101.0, 136.0] | False |  |
| stabilita | author's convention (all active): mean recovery of the 89 | 0.788 | 0.7921 | False |  |
| stabilita | author's convention (all active): mean Jaccard | 0.5877 | 0.5895 | False |  |
| stabilita | inclusion probability of the 89: min / median / max (historical convention) | [0.507, 0.795, 1.0] | [0.506, 0.801, 1.0] | False |  |
| stabilita | correlation of per-image inclusion probabilities with the package's (600 images) | 1 | 0.9998 | False |  |
| icc | complete: ICC1 | 0.138184 | 0.138184 | True | one-way ANOVA on rater-centred scores, df_within reduced by (raters − 1); NOT a crossed model |
| icc | complete: ICCk | 0.860065 | 0.860065 | True |  |
| icc | complete: k0 | 38.331948 | 38.331948 | True |  |
| icc | complete: MS_between | 12.802915 | 12.802915 | True |  |
| icc | complete: MS_within | 1.791578 | 1.791578 | True |  |
| icc | complete: df_within | 22247.0 | 22247.0 | True |  |
| icc | filtered: ICC1 | 0.138146 | 0.138146 | True | one-way ANOVA on rater-centred scores, df_within reduced by (raters − 1); NOT a crossed model |
| icc | filtered: ICCk | 0.858439 | 0.858439 | True |  |
| icc | filtered: k0 | 37.83199 | 37.83199 | True |  |
| icc | filtered: MS_between | 12.693051 | 12.693051 | True |  |
| icc | filtered: MS_within | 1.796844 | 1.796844 | True |  |
| icc | filtered: df_within | 21949.0 | 21949.0 | True |  |
| lotti | batch 1: photographs / ratings / raters | 300/18143/166 | 300/18143/166 | True | import dates from source_images.imported_at |
| lotti | batch 2: photographs / ratings / raters | 300/4869/54 | 300/4869/54 | True | import dates from source_images.imported_at |
| lotti | batch 1 AESTHETIC: photographs | 43 | 43 | True |  |
| lotti | batch 2 AESTHETIC: photographs | 46 | 46 | True |  |
| lotti | batch 1 CONTROL: photographs | 46 | 46 | True |  |
| lotti | batch 2 CONTROL: photographs | 43 | 43 | True |  |
| binomiale | wins / n | 677/1320 | 677/1320 | True |  |
| binomiale | two-sided exact p | 0.3637276593 | 0.3637276593 | True |  |
| binomiale | Clopper–Pearson 95% low / high | 0.485533/0.540167 | 0.485533/0.540167 | True | marginal summary assuming independent comparisons; does not replace the clustered inference |
| fuori_training | n external photographs | 422 | 422 | True |  |
| fuori_training | Spearman projection-on-u vs mean rating, complete sample | 0.396569 | 0.396569 | True | projection on u from the matrices (affinity = d·projection: same ranks) |
| fuori_training | Spearman, filtered sample | 0.393121 | 0.393121 | True |  |
| fuori_training | Spearman(saved affinity, projection on u) over the 422 | 1 | 1.0 | True | the saved affinity is a positive affine transform of the projection for non-members |
| dispersione | AESTHETIC: RMS distance to own centroid |  | 0.9095 |  | bootstrap of photographs 95% 0.8857–0.9202 (biased downward by resampling duplicates) |
| dispersione | CONTROL: RMS distance to own centroid |  | 0.9225 |  | 95% 0.9039–0.9287 |
| dispersione | A − C: RMS distance to own centroid |  | -0.013 |  | difference bootstrap 95% -0.0352/+0.0076 |
| dispersione | AESTHETIC: mean distance to own centroid |  | 0.9055 |  | bootstrap of photographs 95% 0.8803–0.9175 (biased downward by resampling duplicates) |
| dispersione | CONTROL: mean distance to own centroid |  | 0.9207 |  | 95% 0.9013–0.9274 |
| dispersione | A − C: mean distance to own centroid |  | -0.0151 |  | difference bootstrap 95% -0.0389/+0.0071 |
| dispersione | AESTHETIC: mean pairwise distance |  | 1.2874 |  | bootstrap of photographs 95% 1.2450–1.2968 (biased downward by resampling duplicates) |
| dispersione | CONTROL: mean pairwise distance |  | 1.3085 |  | 95% 1.2737–1.3105 |
| dispersione | A − C: mean pairwise distance |  | -0.0211 |  | difference bootstrap 95% -0.0541/+0.0094 |
| dispersione | pooled RMS dispersion used for the standardised distance 0.26 |  | 0.9161 |  | d / pooled RMS = 0.257 |

Notes. (1) The historical rule (`SelectionService.Evaluate`) computes the percentile cutoff on the ELIGIBLE images (active, n ≥ 10) with linear interpolation; the package's specification uses all active images. On the original data both give the 89 AESTHETIC because the cutoff is below 5 in both cases; in the rater bootstrap the two conventions are reported separately. (2) Bootstrap distributions are compared, not digits: different seed. (3) Inclusion frequencies measure internal stability of the selection under resampling of the raters, not generalisation. (4) The out-of-training correlation verifies that the photograph direction is associated with the ratings outside the LoRA sets; it says nothing about memorisation of training examples in the outputs, and 'held out' refers to the LoRA, not to the SDXL pretraining.
