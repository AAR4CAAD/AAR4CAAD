# DINOv2 measures — reproduction, distances to the corpora, adjusted directions (audit rev12)

Space: DINOv2 CLS, L2-normalised. g = centroid(AESTHETIC photos) − centroid(CONTROL photos); d = ‖g‖; u = g/d. For a cell: P = (e_A − e_C)·u; S = (e_A − e_C)·g = d·P; R = P/d = S/d². Intervals: bootstrap over the 48 prompts unless stated (conditional on the direction). The 'direction uncertainty' rows resample the photographs.

## Reproduction

| section | quantity | reported | recomputed | 95% CI | p | n | note |
|---|---|---|---|---|---|---|---|
| direction | gap between photograph centroids d | 0.235 | 0.235229 |  |  |  | frozen file: 0.235229; identical True; u·u_frozen = 1.000000000 |
| direction | gap under random relabelling (mean of null) | 0.138 | 0.138 |  | 0.0 |  | 2000 permutations of the 178 labels |
| direction | standardised distance d / pooled multivariate dispersion | 0.26 | 0.257 |  |  |  | pooled dispersion 0.9161 (root mean squared distance to the own centroid, averaged over the two sets); previous reply used 0.9131288332377052 with the same meaning → 0.258 |
| direction | AUC AESTHETIC vs CONTROL photographs (leave-one-out affinity) | 0.78 | 0.741 |  |  |  | AUC of the LOO relative affinity; the manuscript's 0.78 refers to the classifier of the historical report |
| direction | Spearman of the projection on the direction with the mean rating, 422 external photographs | 0.39 | 0.393 |  | 4.777269270235928e-17 | 422 |  |
| identities | S = d·P max abs error (192 cells) | 0 | 5.551115123125783e-17 |  |  |  | S = difference of relative affinities (e·g), P = projection on the unit direction; exact up to rounding |
| identities | R = P/d = S/d² max abs error | 0 | 6.661338147750939e-16 |  |  |  |  |
| identities | sign and rank invariance S vs P (Spearman) | 1 | 1.0 |  |  |  | conversion by a positive constant |
| 159 triplets | mean P (unit-direction projection) A−C | 0.0429 | 0.0429 | 0.0273 / 0.0602 | 0.0 | 159 | bootstrap over prompts (conditional on the frozen direction) |
| 159 triplets | mean P A−BASE | 0.0443 | 0.0443 | 0.0263 / 0.0632 | 0.0 | 159 | bootstrap over prompts (conditional on the frozen direction) |
| 159 triplets | mean P C−BASE | 0.0014 | 0.0014 | -0.0125 / 0.015 | 0.8432 | 159 | bootstrap over prompts (conditional on the frozen direction) |
| 159 triplets | transfer ratio R = mean P / d | 0.18 | 0.1823 | 0.1155 / 0.2558 | 0.0 |  | manuscript CI 12–25% |
| 159 triplets | share of triplets with P > 0 | 0.62 | 0.616 |  |  | 159 |  |
| 159 triplets | S: min / median / mean / max / SD | [-0.0289, 0.0053, 0.0101, 0.0995, 0.0212] | [-0.0289, 0.0053, 0.0101, 0.0995, 0.0212] |  |  |  | Fig. 1 of the manuscript labels −0.0289 / +0.0053 / +0.0995: these are S (affinity difference), while the text's +0.0429 is the mean of P |
| 159 triplets | P: min / median / mean / max / SD | [-0.1227, 0.0223, 0.0429, 0.4229, 0.09] | [-0.1227, 0.0223, 0.0429, 0.4229, 0.09] |  |  |  | Fig. 1 of the manuscript labels −0.0289 / +0.0053 / +0.0995: these are S (affinity difference), while the text's +0.0429 is the mean of P |
| 159 triplets | Fig. 1 cells (min, median, max of S) | A07/6127; ?; A08/7 | A07_6127; C14_25478; A08_7 |  |  |  | median cell = the 80th of 159 ordered values |
| 159 triplets | Spearman P vs human Δ rating A−C | 0.23 | 0.233 |  | 0.0032 | 159 |  |
| 159 triplets | Spearman P vs share of A choices | 0.04 | 0.037 |  | 0.648 | 159 |  |
| 192 cells | mean P A−C (original pair, all cells) | None | 0.0415 | 0.0279 / 0.0569 | 0.0 | 192 |  |
| 192 cells | mean P A−BASE (original pair, all cells) | None | 0.0416 | 0.0263 / 0.0591 | 0.0 | 192 |  |
| 192 cells | mean P C−BASE (original pair, all cells) | None | 0.0001 | -0.0124 / 0.0125 | 0.9812 | 192 |  |
| 192 cells | mean ‖Δ_A‖ / ‖Δ_C‖ (size of the shift from BASE), 159 / 192 | 0.678 / 0.699 (159); 0.701 / 0.719 (192) | 0.678 / 0.699 (159); 0.701 / 0.719 (192) |  |  |  |  |
| replication | mean P A−C, paired training seed 1254 | 0.0435 | 0.0435 | 0.0271 / 0.0607 | 0.0 | 192 |  |
| replication | AESTHETIC seed 1254: along u / along the shared direction | None | +0.0416 / see fig_embedding_shifts |  |  |  |  |
| replication | CONTROL seed 1254: along u / along the shared direction | None | -0.0019 / see fig_embedding_shifts |  |  |  |  |
| replication | mean P A−C, paired training seed 9865 | 0.0412 | 0.0412 | 0.0255 / 0.0579 | 0.0 | 192 |  |
| replication | AESTHETIC seed 9865: along u / along the shared direction | None | +0.0413 / see fig_embedding_shifts |  |  |  |  |
| replication | CONTROL seed 9865: along u / along the shared direction | None | +0.0001 / see fig_embedding_shifts |  |  |  |  |
| replication | mean P A−C, paired training seed 42160 | 0.0504 | 0.0504 | 0.0356 / 0.0684 | 0.0 | 192 |  |
| replication | AESTHETIC seed 42160: along u / along the shared direction | None | +0.0320 / see fig_embedding_shifts |  |  |  |  |
| replication | CONTROL seed 42160: along u / along the shared direction | None | -0.0185 / see fig_embedding_shifts |  |  |  |  |
| replication | AESTHETIC seed 1254: mean projection on u / on the shared orthogonal direction w | None | +0.0416 / +0.1118 |  |  |  | w = mean shift of the six adapters, orthogonalised to u (same construction as fig_embedding_shifts) |
| replication | AESTHETIC seed 9865: mean projection on u / on the shared orthogonal direction w | None | +0.0413 / +0.1040 |  |  |  | w = mean shift of the six adapters, orthogonalised to u (same construction as fig_embedding_shifts) |
| replication | AESTHETIC seed 42160: mean projection on u / on the shared orthogonal direction w | None | +0.0320 / +0.1182 |  |  |  | w = mean shift of the six adapters, orthogonalised to u (same construction as fig_embedding_shifts) |
| replication | CONTROL seed 1254: mean projection on u / on the shared orthogonal direction w | None | -0.0019 / +0.1202 |  |  |  | w = mean shift of the six adapters, orthogonalised to u (same construction as fig_embedding_shifts) |
| replication | CONTROL seed 9865: mean projection on u / on the shared orthogonal direction w | None | +0.0001 / +0.1229 |  |  |  | w = mean shift of the six adapters, orthogonalised to u (same construction as fig_embedding_shifts) |
| replication | CONTROL seed 42160: mean projection on u / on the shared orthogonal direction w | None | -0.0185 / +0.1048 |  |  |  | w = mean shift of the six adapters, orthogonalised to u (same construction as fig_embedding_shifts) |
| replication | determinism: mean distance between the two runs of seed 1254 (AESTHETIC) / between seeds 1254 and 9865 / between AESTHETIC and CONTROL at seed 1254 | 0.32 / 0.63 / 0.68 | 0.32 / 0.62 / 0.68 |  |  |  |  |
| direction uncertainty | d: 95% interval from resampling the 89+89 photographs | None | 0.2352 | 0.2326 / 0.3209 |  |  | the bootstrap d is biased upwards (noise adds length): shown as a scale of uncertainty, not as a corrected estimate |
| direction uncertainty | mean P (159) with the direction re-estimated on resampled photographs | None | 0.0429 | 0.0241 / 0.0482 |  |  | outputs fixed; only the direction varies |
| direction uncertainty | R with the direction re-estimated | None | 0.1823 | 0.0906 / 0.1801 |  |  |  |

**Which measure is in which figure/sentence.** Fig. 1 (min −0.0289, median +0.0053, max +0.0995) shows S; the text (+0.0429, 18%, Spearman +0.23, 62% positive) uses P and R. S and P differ by the constant d = 0.2352: identical signs, ranks and p-values. Fig. 3 plots P-type projections of cell means on u and on the shared orthogonal direction.

## Distances to the two photograph corpora (new, post-review)

Two metrics are reported and must not be confused: (i) distance between centroids (adapter mean image → photograph centroid); (ii) mean over images of the distance of each generated image to the photograph centroid. The *change* columns use (ii) per cell (adapter image minus the BASE image of the same cell), with prompt-bootstrap intervals.

| adapter | seed | target | centroid→centroid | mean image→centroid | mean image→photographs |
|---|---|---|---|---|---|
| BASE | 0 | AESTHETIC photographs | 0.3898 | 0.9283 | 1.2961 |
| BASE | 0 | CONTROL photographs | 0.3490 | 0.9134 | 1.2945 |
| AESTHETIC | 1254 | AESTHETIC photographs | 0.3374 | 0.9135 | 1.2850 |
| AESTHETIC | 1254 | CONTROL photographs | 0.3213 | 0.9097 | 1.2918 |
| AESTHETIC | 9865 | AESTHETIC photographs | 0.3504 | 0.9202 | 1.2900 |
| AESTHETIC | 9865 | CONTROL photographs | 0.3347 | 0.9164 | 1.2967 |
| AESTHETIC | 42160 | AESTHETIC photographs | 0.3406 | 0.9188 | 1.2890 |
| AESTHETIC | 42160 | CONTROL photographs | 0.3176 | 0.9124 | 1.2939 |
| CONTROL | 1254 | AESTHETIC photographs | 0.3544 | 0.9218 | 1.2914 |
| CONTROL | 1254 | CONTROL photographs | 0.3075 | 0.9063 | 1.2895 |
| CONTROL | 9865 | AESTHETIC photographs | 0.3428 | 0.9292 | 1.2969 |
| CONTROL | 9865 | CONTROL photographs | 0.2956 | 0.9146 | 1.2957 |
| CONTROL | 42160 | AESTHETIC photographs | 0.3934 | 0.9302 | 1.2974 |
| CONTROL | 42160 | CONTROL photographs | 0.3404 | 0.9108 | 1.2927 |

| adapter | seed | target | Δ mean image→centroid distance vs BASE | 95% CI | p |
|---|---|---|---|---|---|
| AESTHETIC | 1254 | AESTHETIC photographs | -0.0148 | -0.0205 / -0.0093 | 0.0000 |
| AESTHETIC | 1254 | CONTROL photographs | -0.0037 | -0.0084 / +0.0011 | 0.1280 |
| AESTHETIC | 1254 | own minus other corpus (approach difference) | -0.0111 | -0.0158 / -0.0070 | 0.0000 |
| AESTHETIC | 9865 | AESTHETIC photographs | -0.0081 | -0.0143 / -0.0017 | 0.0152 |
| AESTHETIC | 9865 | CONTROL photographs | +0.0031 | -0.0026 / +0.0087 | 0.2612 |
| AESTHETIC | 9865 | own minus other corpus (approach difference) | -0.0112 | -0.0161 / -0.0067 | 0.0000 |
| AESTHETIC | 42160 | AESTHETIC photographs | -0.0095 | -0.0155 / -0.0040 | 0.0000 |
| AESTHETIC | 42160 | CONTROL photographs | -0.0010 | -0.0063 / +0.0041 | 0.7180 |
| AESTHETIC | 42160 | own minus other corpus (approach difference) | -0.0085 | -0.0126 / -0.0048 | 0.0000 |
| CONTROL | 1254 | AESTHETIC photographs | -0.0065 | -0.0117 / -0.0016 | 0.0104 |
| CONTROL | 1254 | CONTROL photographs | -0.0071 | -0.0123 / -0.0021 | 0.0052 |
| CONTROL | 1254 | own minus other corpus (approach difference) | -0.0006 | -0.0033 / +0.0021 | 0.6744 |
| CONTROL | 9865 | AESTHETIC photographs | +0.0009 | -0.0043 / +0.0060 | 0.6992 |
| CONTROL | 9865 | CONTROL photographs | +0.0013 | -0.0032 / +0.0056 | 0.5884 |
| CONTROL | 9865 | own minus other corpus (approach difference) | +0.0004 | -0.0029 / +0.0036 | 0.8152 |
| CONTROL | 42160 | AESTHETIC photographs | +0.0019 | -0.0032 / +0.0071 | 0.4636 |
| CONTROL | 42160 | CONTROL photographs | -0.0025 | -0.0066 / +0.0015 | 0.2084 |
| CONTROL | 42160 | own minus other corpus (approach difference) | -0.0045 | -0.0081 / -0.0010 | 0.0140 |

Negative Δ = the adapter's images are closer to that corpus than BASE's. 'own minus other' < 0 means the adapter approaches its own corpus more than the other one.

Centroid-to-centroid metric (change vs BASE, prompt bootstrap, both centroids recomputed in each resample):

| adapter | seed | target | Δ centroid→centroid | 95% CI | p |
|---|---|---|---|---|---|
| AESTHETIC | 1254 | AESTHETIC photographs | -0.0525 | -0.0653 / -0.0344 | 0.0000 |
| AESTHETIC | 1254 | CONTROL photographs | -0.0277 | -0.0404 / -0.0099 | 0.0016 |
| AESTHETIC | 9865 | AESTHETIC photographs | -0.0395 | -0.0538 / -0.0209 | 0.0000 |
| AESTHETIC | 9865 | CONTROL photographs | -0.0143 | -0.0290 / +0.0043 | 0.1308 |
| AESTHETIC | 42160 | AESTHETIC photographs | -0.0493 | -0.0588 / -0.0338 | 0.0000 |
| AESTHETIC | 42160 | CONTROL photographs | -0.0314 | -0.0417 / -0.0146 | 0.0004 |
| CONTROL | 1254 | AESTHETIC photographs | -0.0354 | -0.0477 / -0.0193 | 0.0000 |
| CONTROL | 1254 | CONTROL photographs | -0.0415 | -0.0527 / -0.0259 | 0.0000 |
| CONTROL | 9865 | AESTHETIC photographs | -0.0470 | -0.0607 / -0.0260 | 0.0000 |
| CONTROL | 9865 | CONTROL photographs | -0.0534 | -0.0672 / -0.0320 | 0.0000 |
| CONTROL | 42160 | AESTHETIC photographs | +0.0035 | -0.0109 / +0.0189 | 0.6324 |
| CONTROL | 42160 | CONTROL photographs | -0.0086 | -0.0202 / +0.0050 | 0.2268 |

The two metrics answer different questions (mean position vs spread of individual images) and are reported separately.

## Direction adjusted for period and area (specification fixed before the run: `SPEC_direzione_aggiustata.json`)

The adjustment residualises the 600 photograph embeddings on recorded period (pre-1919 merged with 1919–1945) and recorded area (8 labels, kept as recorded) by per-dimension OLS; the adjusted direction is the A−C difference of the mean residuals. Outputs are not residualised (they have no period/area): the numbers are projections of the original outputs on an adjusted source direction.

| direction | d_adj | d_adj/d | cos with original | mean R² of the covariate model | A−C seed 1254 | seed 9865 | seed 42160 | pooled | R pooled | R, direction-bootstrap 95% | original pair 159: A−C | R |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| original (no adjustment) | 0.2352 | 1.000 | +1.000 | 0.000 | +0.0435 [+0.0271, +0.0609] | +0.0412 [+0.0252, +0.0577] | +0.0504 [+0.0356, +0.0669] | +0.0451 | 0.192 | 0.113 – 0.180 | +0.0429 [+0.0264, +0.0604] | 0.182 |
| adjusted for period | 0.2197 | 0.934 | +0.991 | 0.027 | +0.0437 [+0.0280, +0.0605] | +0.0373 [+0.0219, +0.0531] | +0.0480 [+0.0331, +0.0650] | +0.0430 | 0.196 | 0.108 – 0.179 | +0.0380 [+0.0229, +0.0548] | 0.173 |
| adjusted for area | 0.2231 | 0.948 | +0.990 | 0.042 | +0.0436 [+0.0281, +0.0609] | +0.0426 [+0.0272, +0.0587] | +0.0475 [+0.0334, +0.0640] | +0.0446 | 0.200 | 0.113 – 0.183 | +0.0450 [+0.0302, +0.0623] | 0.202 |
| adjusted for period and area (additive) | 0.2092 | 0.889 | +0.982 | 0.067 | +0.0437 [+0.0281, +0.0605] | +0.0380 [+0.0221, +0.0543] | +0.0454 [+0.0312, +0.0615] | +0.0423 | 0.202 | 0.110 – 0.187 | +0.0394 [+0.0248, +0.0558] | 0.188 |

A−BASE and C−BASE on the adjusted directions are in `dino_adjusted_direction.csv`.

Category counts (photographs): period × set

| period | AESTHETIC | CONTROL | other |
|---|---|---|---|
| 1919-1945 | 8 | 15 | 75 |
| 1946-1969 | 19 | 22 | 95 |
| 1970-1989 | 12 | 12 | 74 |
| 1990-2009 | 27 | 23 | 101 |
| 2010-today | 23 | 17 | 77 |

area × set

| area | AESTHETIC | CONTROL | other |
|---|---|---|---|
| Africa | 3 | 3 | 16 |
| Asia | 16 | 12 | 46 |
| Europe | 28 | 38 | 198 |
| Japan | 6 | 11 | 47 |
| Latin America | 12 | 8 | 48 |
| Middle East | 6 | 3 | 19 |
| North America | 14 | 10 | 34 |
| Oceania | 4 | 4 | 14 |

Limits: linear additive adjustment on two recorded variables only; small cells; the adjustment cannot turn the design into an experiment that isolates preference from composition.

