# The 31 descriptors — reproduction, covariance decomposition, strata, distances (audit rev12)

Standardisation: every descriptor (CLIP attributes as logits) centred and scaled on the 600 photographs. x = mean(A photos) − mean(C photos); a, c = per-cell differences of the generated images from BASE (same prompt and seed), mean of the three paired training seeds, mean over the 192 cells.

## Reproduction and definitions

| section | quantity | reported | recomputed | 95% CI | note |
|---|---|---|---|---|---|
| profile | r(x, a−c) | 0.71 | 0.707 | 0.567 / 0.827 | bootstrap over the 31 descriptors (as in the historical figure) |
| profile | r(x, a) | -0.01 | -0.006 | -0.3 / 0.29 |  |
| profile | r(x, c) | -0.43 | -0.427 | -0.68 / -0.123 |  |
| profile | same sign as x: a−c / a / c | 27 / 14 / 13 | 27 / 14 / 13 |  |  |
| profile | a and c same sign / r(a,c) | 26 / +0.82 | 26 / +0.82 |  |  |
| profile | 'shared component' 0.21 SD: definition = mean |(a+c)/2|; 'specific' 0.07 = mean |(a−c)/2| | 0.21 / 0.07 | 0.206 / 0.069 |  | mean absolute value over the 31 descriptors of the signed cell-mean differences; r(x,m) and r(x,h) below |
| profile | r(x, (a+c)/2) / r(x, (a−c)/2) | -0.23 / +0.71 | -0.228 / +0.707 |  | r(x,(a−c)/2) = r(x,a−c) EXACTLY: a positive constant does not change a correlation. It is an identity, not independent evidence |
| profile | mean |x| / |a−c| / |a| / |c| | 0.22 / 0.14 / 0.21 / 0.21 | 0.22 / 0.14 / 0.21 / 0.21 |  |  |
| profile | r(x,a−c): prompt-bootstrap 95% |  | 0.707 | 0.537 / 0.79 | uncertainty from the prompts, descriptors fixed |
| profile | r(x,a): prompt-bootstrap 95% |  | -0.006 | -0.14 / 0.125 |  |
| profile | r(x,c): prompt-bootstrap 95% |  | -0.427 | -0.51 / -0.32 |  |
| covariance | Cov(x,a−c) = Cov(x,a) − Cov(x,c) | 0.03198 | -0.00047 − (-0.03244) = 0.03198 |  | identity error 6.9e-18 |
| covariance | share of Cov(x,a−c) carried by −Cov(x,c) (the CONTROL term) |  | 1.015 | 0.734 / 1.387 | prompt bootstrap; descriptor bootstrap 0.31–1.74. Shares are ratios of covariances with uncertain denominators: read as 'most of the covariance comes from CONTROL moving against x', not as an exact percentage |
| covariance | share carried by Cov(x,a) (the AESTHETIC term) |  | -0.015 |  | = 1 − the previous row; point estimate near zero or slightly negative because r(x,a) ≈ −0.01 |
| covariance | slopes of a−c, a, c on x (SD per SD) |  | +0.382 / -0.006 / -0.387 |  |  |
| descriptor signs | curved_organic: x (photos) / a−c / a / c |  | +0.61 / +0.10 / +0.22 / +0.12 |  | same direction photos→outputs |
| descriptor signs | concrete: x (photos) / a−c / a / c |  | -0.58 / -0.10 / -0.16 / -0.06 |  | same direction photos→outputs |
| descriptor signs | low_angle: x (photos) / a−c / a / c |  | +0.41 / +0.20 / -0.16 / -0.36 |  | same direction photos→outputs |
| descriptor signs | cars: x (photos) / a−c / a / c |  | -0.41 / -0.22 / +0.17 / +0.40 |  | same direction photos→outputs |
| descriptor signs | glass: x (photos) / a−c / a / c |  | +0.37 / +0.09 / -0.32 / -0.41 |  | same direction photos→outputs |
| descriptor signs | iconic_design: x (photos) / a−c / a / c |  | +0.58 / +0.19 / -0.11 / -0.30 |  | same direction photos→outputs |
| descriptor signs | contemporary: x (photos) / a−c / a / c |  | +0.43 / +0.29 / -0.04 / -0.33 |  | same direction photos→outputs |
| descriptor signs | monumental: x (photos) / a−c / a / c |  | +0.42 / +0.11 / +0.08 / -0.03 |  | same direction photos→outputs |
| descriptor signs | interior: x (photos) / a−c / a / c |  | +0.45 / +0.09 / -0.35 / -0.44 |  | same direction photos→outputs |
| redundancy | descriptor correlations on the 600 photographs: mean |r| / max |r| / effective number of descriptors |  | 0.14 / 0.88 / 14.4 |  | effective number = (Σλ)²/Σλ²; the 31 descriptors are not independent, the profile r treats them as 31 equally weighted points |

## Photograph contrasts by CONTROL stratum (no pairs exist: stratum-weighted contrasts)

| stratum | n CONTROL | n AESTHETIC involved | construction | r(x_stratum, x_full) | r with a−c | r with a | r with c | same sign with a−c |
|---|---|---|---|---|---|---|---|---|
| type_and_style | 20 | 20 | 19 strata, each weighted equally: mean over strata of (mean of the AESTHETIC photographs of the stratum − mean of its CONTROL photographs) | +0.530 | +0.026 | -0.456 | -0.467 | 17 |
| type_only | 41 | 63 | 25 strata, each weighted equally: mean over strata of (mean of the AESTHETIC photographs of the stratum − mean of its CONTROL photographs) | +0.795 | +0.632 | +0.305 | -0.075 | 25 |
| random_fill | 28 | 89 | all 89 AESTHETIC vs the 28 random CONTROL (unpaired; no counterpart stratum exists) | +0.897 | +0.709 | -0.157 | -0.578 | 24 |
| matched_61 (20 type+style + 41 type) | 61 | 65 | 44 strata weighted equally | +0.855 | +0.434 | -0.082 | -0.340 | 20 |

Per-descriptor values in `descriptors_profile.csv`. The random-fill contrast has no counterpart set and is reported as 'all AESTHETIC vs the 28 random CONTROL'. None of these contrasts estimates what adapters trained on the sub-groups would do.

## Distances to the photograph profiles (descriptor space, 31 standardised dimensions)

| adapter | seed | target | centroid→centroid | mean image→centroid |
|---|---|---|---|---|
| BASE | 0 | AESTHETIC photographs | 2.675 | 6.151 |
| BASE | 0 | CONTROL photographs | 3.126 | 6.347 |
| AESTHETIC | 1254 | AESTHETIC photographs | 2.441 | 6.141 |
| AESTHETIC | 1254 | CONTROL photographs | 2.947 | 6.339 |
| AESTHETIC | 9865 | AESTHETIC photographs | 2.256 | 6.260 |
| AESTHETIC | 9865 | CONTROL photographs | 2.784 | 6.447 |
| AESTHETIC | 42160 | AESTHETIC photographs | 2.601 | 6.348 |
| AESTHETIC | 42160 | CONTROL photographs | 3.005 | 6.510 |
| CONTROL | 1254 | AESTHETIC photographs | 2.343 | 5.994 |
| CONTROL | 1254 | CONTROL photographs | 2.625 | 6.096 |
| CONTROL | 9865 | AESTHETIC photographs | 1.817 | 5.788 |
| CONTROL | 9865 | CONTROL photographs | 1.967 | 5.818 |
| CONTROL | 42160 | AESTHETIC photographs | 2.250 | 6.050 |
| CONTROL | 42160 | CONTROL photographs | 2.208 | 6.022 |

| adapter | seed | target | Δ mean image→centroid vs BASE | 95% CI (prompts) | p |
|---|---|---|---|---|---|
| AESTHETIC | 1254 | AESTHETIC photographs | -0.010 | -0.216 / +0.204 | 0.9436 |
| AESTHETIC | 1254 | CONTROL photographs | -0.008 | -0.222 / +0.211 | 0.9512 |
| AESTHETIC | 1254 | own minus other corpus | -0.002 | -0.065 / +0.064 | 0.9272 |
| AESTHETIC | 9865 | AESTHETIC photographs | +0.108 | -0.035 / +0.256 | 0.1404 |
| AESTHETIC | 9865 | CONTROL photographs | +0.101 | -0.048 / +0.240 | 0.1748 |
| AESTHETIC | 9865 | own minus other corpus | +0.008 | -0.047 / +0.063 | 0.7784 |
| AESTHETIC | 42160 | AESTHETIC photographs | +0.197 | -0.012 / +0.415 | 0.0688 |
| AESTHETIC | 42160 | CONTROL photographs | +0.163 | -0.055 / +0.392 | 0.1468 |
| AESTHETIC | 42160 | own minus other corpus | +0.033 | -0.023 / +0.090 | 0.2412 |
| CONTROL | 1254 | AESTHETIC photographs | -0.157 | -0.341 / +0.025 | 0.0880 |
| CONTROL | 1254 | CONTROL photographs | -0.251 | -0.442 / -0.064 | 0.0076 |
| CONTROL | 1254 | own minus other corpus | -0.093 | -0.141 / -0.046 | 0.0000 |
| CONTROL | 9865 | AESTHETIC photographs | -0.363 | -0.485 / -0.241 | 0.0000 |
| CONTROL | 9865 | CONTROL photographs | -0.529 | -0.673 / -0.390 | 0.0000 |
| CONTROL | 9865 | own minus other corpus | -0.165 | -0.223 / -0.110 | 0.0000 |
| CONTROL | 42160 | AESTHETIC photographs | -0.101 | -0.275 / +0.077 | 0.2728 |
| CONTROL | 42160 | CONTROL photographs | -0.325 | -0.530 / -0.114 | 0.0024 |
| CONTROL | 42160 | own minus other corpus | -0.223 | -0.296 / -0.150 | 0.0000 |

| adapter | seed | target | Δ centroid→centroid vs BASE | 95% CI (prompts) | p |
|---|---|---|---|---|---|
| AESTHETIC | 1254 | AESTHETIC photographs | -0.235 | -0.496 / +0.070 | 0.1344 |
| AESTHETIC | 1254 | CONTROL photographs | -0.179 | -0.456 / +0.132 | 0.2668 |
| AESTHETIC | 9865 | AESTHETIC photographs | -0.420 | -0.568 / -0.192 | 0.0000 |
| AESTHETIC | 9865 | CONTROL photographs | -0.343 | -0.520 / -0.109 | 0.0044 |
| AESTHETIC | 42160 | AESTHETIC photographs | -0.074 | -0.337 / +0.282 | 0.6580 |
| AESTHETIC | 42160 | CONTROL photographs | -0.121 | -0.383 / +0.201 | 0.4572 |
| CONTROL | 1254 | AESTHETIC photographs | -0.333 | -0.576 / -0.044 | 0.0212 |
| CONTROL | 1254 | CONTROL photographs | -0.502 | -0.734 / -0.220 | 0.0004 |
| CONTROL | 9865 | AESTHETIC photographs | -0.859 | -1.070 / -0.559 | 0.0000 |
| CONTROL | 9865 | CONTROL photographs | -1.160 | -1.382 / -0.858 | 0.0000 |
| CONTROL | 42160 | AESTHETIC photographs | -0.425 | -0.613 / -0.168 | 0.0008 |
| CONTROL | 42160 | CONTROL photographs | -0.918 | -1.125 / -0.631 | 0.0000 |

Negative = closer than BASE. Two metrics, two questions: the mean position of the adapter's images (centroid→centroid) can move toward a profile while the mean distance of the individual images does not change (spread). Report both; the correlation r(x,a) ≈ 0 is neither test.

