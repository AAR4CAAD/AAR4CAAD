# DINOv2: direction adjusted for period, area, building type and style — two geometries

Specification fixed before the run: `SPEC_dino_aggiustamento_completo.json`. G1 = original outputs projected on the adjusted photograph direction (as in the audit). G2 = common linear transformation T = I − Π estimated on the photographs and applied identically to photographs and outputs; only in G2 are distances comparable. P, R and distances of the two geometries are never mixed. Intervals: bootstrap over the 48 prompts, conditional on the estimated direction. The mean of the three seeds is a descriptive summary of these six adapters.

## Directions

| direction | geometry | d | cos with original | note |
|---|---|---|---|---|
| (i) original | G1 | 0.2352 | +1.000 | rank(X)=0 of 0 columns; mean R2 of covariate model 0.000 |
| (i) original | G2 | 0.2352 | +1.000 | directions removed 0 of 768; share of photograph variance removed 0.000 |
| (ii) period + area | G1 | 0.2092 | +0.982 | rank(X)=12 of 12 columns; mean R2 of covariate model 0.067 |
| (ii) period + area | G2 | 0.1623 | +0.690 | directions removed 11 of 768; share of photograph variance removed 0.186 |
| (iii) period + area + type + style | G1 | 0.1603 | +0.925 | rank(X)=88 of 88 columns; mean R2 of covariate model 0.257 |
| (iii) period + area + type + style | G2 | 0.1005 | +0.427 | directions removed 87 of 768; share of photograph variance removed 0.574 |

## Projections and R per training seed

| direction | geometry | seed | P A−C | P A−BASE | P C−BASE | R |
|---|---|---|---|---|---|---|
| (i) original | G1 | 1254 | +0.0435 [+0.0278, +0.0617] | +0.0416 [+0.0261, +0.0586] | -0.0019 [-0.0120, +0.0087] | +0.1849 [+0.1183, +0.2624] |
| (i) original | G1 | 9865 | +0.0412 [+0.0259, +0.0580] | +0.0413 [+0.0255, +0.0589] | +0.0001 [-0.0121, +0.0123] | +0.1754 [+0.1101, +0.2467] |
| (i) original | G1 | 42160 | +0.0504 [+0.0352, +0.0676] | +0.0320 [+0.0184, +0.0461] | -0.0185 [-0.0317, -0.0049] | +0.2145 [+0.1497, +0.2873] |
| (i) original | G1 | mean of the three seeds (descriptive) | +0.0451 [+0.0321, +0.0594] | n/a | n/a | +0.1916 [+0.1365, +0.2527] |
| (i) original | G2 | 1254 | +0.0435 [+0.0278, +0.0617] | +0.0416 [+0.0264, +0.0590] | -0.0019 [-0.0120, +0.0085] | +0.1849 [+0.1180, +0.2624] |
| (i) original | G2 | 9865 | +0.0412 [+0.0260, +0.0586] | +0.0413 [+0.0250, +0.0588] | +0.0001 [-0.0118, +0.0126] | +0.1754 [+0.1106, +0.2490] |
| (i) original | G2 | 42160 | +0.0504 [+0.0354, +0.0677] | +0.0320 [+0.0186, +0.0463] | -0.0185 [-0.0319, -0.0053] | +0.2145 [+0.1504, +0.2879] |
| (i) original | G2 | mean of the three seeds (descriptive) | +0.0451 [+0.0320, +0.0591] | n/a | n/a | +0.1916 [+0.1361, +0.2512] |
| (ii) period + area | G1 | 1254 | +0.0437 [+0.0289, +0.0603] | +0.0383 [+0.0231, +0.0550] | -0.0054 [-0.0145, +0.0040] | +0.2088 [+0.1383, +0.2884] |
| (ii) period + area | G1 | 9865 | +0.0380 [+0.0223, +0.0536] | +0.0391 [+0.0235, +0.0559] | +0.0012 [-0.0105, +0.0125] | +0.1815 [+0.1066, +0.2561] |
| (ii) period + area | G1 | 42160 | +0.0454 [+0.0312, +0.0613] | +0.0306 [+0.0178, +0.0445] | -0.0148 [-0.0270, -0.0026] | +0.2169 [+0.1491, +0.2929] |
| (ii) period + area | G1 | mean of the three seeds (descriptive) | +0.0423 [+0.0299, +0.0555] | n/a | n/a | +0.2024 [+0.1428, +0.2652] |
| (ii) period + area | G2 | 1254 | +0.0274 [+0.0188, +0.0365] | +0.0079 [-0.0015, +0.0186] | -0.0195 [-0.0269, -0.0120] | +0.1688 [+0.1159, +0.2249] |
| (ii) period + area | G2 | 9865 | +0.0181 [+0.0082, +0.0284] | +0.0073 [-0.0033, +0.0188] | -0.0108 [-0.0200, -0.0017] | +0.1117 [+0.0505, +0.1750] |
| (ii) period + area | G2 | 42160 | +0.0201 [+0.0106, +0.0312] | +0.0062 [-0.0039, +0.0165] | -0.0138 [-0.0214, -0.0061] | +0.1235 [+0.0654, +0.1922] |
| (ii) period + area | G2 | mean of the three seeds (descriptive) | +0.0219 [+0.0148, +0.0296] | n/a | n/a | +0.1347 [+0.0912, +0.1822] |
| (iii) period + area + type + style | G1 | 1254 | +0.0427 [+0.0287, +0.0588] | +0.0359 [+0.0224, +0.0511] | -0.0068 [-0.0158, +0.0022] | +0.2664 [+0.1789, +0.3667] |
| (iii) period + area + type + style | G1 | 9865 | +0.0355 [+0.0215, +0.0500] | +0.0328 [+0.0192, +0.0477] | -0.0027 [-0.0131, +0.0081] | +0.2216 [+0.1343, +0.3119] |
| (iii) period + area + type + style | G1 | 42160 | +0.0439 [+0.0311, +0.0581] | +0.0268 [+0.0152, +0.0395] | -0.0171 [-0.0283, -0.0059] | +0.2740 [+0.1939, +0.3623] |
| (iii) period + area + type + style | G1 | mean of the three seeds (descriptive) | +0.0407 [+0.0297, +0.0525] | n/a | n/a | +0.2540 [+0.1850, +0.3277] |
| (iii) period + area + type + style | G2 | 1254 | +0.0148 [+0.0085, +0.0210] | +0.0074 [+0.0012, +0.0136] | -0.0074 [-0.0119, -0.0024] | +0.1471 [+0.0843, +0.2088] |
| (iii) period + area + type + style | G2 | 9865 | +0.0089 [+0.0022, +0.0155] | +0.0016 [-0.0040, +0.0068] | -0.0073 [-0.0132, -0.0015] | +0.0885 [+0.0219, +0.1539] |
| (iii) period + area + type + style | G2 | 42160 | +0.0106 [+0.0058, +0.0155] | +0.0045 [-0.0013, +0.0103] | -0.0061 [-0.0106, -0.0012] | +0.1057 [+0.0578, +0.1537] |
| (iii) period + area + type + style | G2 | mean of the three seeds (descriptive) | +0.0114 [+0.0075, +0.0155] | n/a | n/a | +0.1138 [+0.0743, +0.1544] |

## Distances in G2 (ΔD vs BASE; negative = closer)

| direction | seed | adapter | own, per-image | other, per-image | own − other | own, centroid | other, centroid |
|---|---|---|---|---|---|---|---|
| (i) original | 1254 | AESTHETIC | -0.0148 [-0.0205, -0.0092] | -0.0037 [-0.0083, +0.0008] | -0.0111 [-0.0160, -0.0068] | -0.0525 [-0.0645, -0.0349] | -0.0277 [-0.0404, -0.0105] |
| (i) original | 1254 | CONTROL | -0.0071 [-0.0124, -0.0023] | -0.0065 [-0.0119, -0.0015] | -0.0006 [-0.0033, +0.0021] | -0.0415 [-0.0522, -0.0255] | -0.0354 [-0.0479, -0.0197] |
| (i) original | 9865 | AESTHETIC | -0.0081 [-0.0144, -0.0017] | +0.0031 [-0.0026, +0.0085] | -0.0112 [-0.0159, -0.0067] | -0.0395 [-0.0543, -0.0200] | -0.0143 [-0.0291, +0.0039] |
| (i) original | 9865 | CONTROL | +0.0013 [-0.0031, +0.0058] | +0.0009 [-0.0043, +0.0060] | +0.0004 [-0.0029, +0.0037] | -0.0534 [-0.0663, -0.0318] | -0.0470 [-0.0612, -0.0262] |
| (i) original | 42160 | AESTHETIC | -0.0095 [-0.0154, -0.0040] | -0.0010 [-0.0063, +0.0041] | -0.0085 [-0.0125, -0.0048] | -0.0493 [-0.0596, -0.0343] | -0.0314 [-0.0418, -0.0143] |
| (i) original | 42160 | CONTROL | -0.0025 [-0.0065, +0.0013] | +0.0019 [-0.0031, +0.0072] | -0.0045 [-0.0079, -0.0010] | -0.0086 [-0.0201, +0.0049] | +0.0035 [-0.0104, +0.0190] |
| (ii) period + area | 1254 | AESTHETIC | -0.0112 [-0.0177, -0.0044] | -0.0093 [-0.0157, -0.0027] | -0.0018 [-0.0042, +0.0002] | -0.0327 [-0.0423, -0.0184] | -0.0280 [-0.0380, -0.0135] |
| (ii) period + area | 1254 | CONTROL | -0.0061 [-0.0130, +0.0003] | -0.0022 [-0.0095, +0.0045] | -0.0039 [-0.0055, -0.0025] | -0.0361 [-0.0476, -0.0197] | -0.0233 [-0.0352, -0.0085] |
| (ii) period + area | 9865 | AESTHETIC | +0.0010 [-0.0062, +0.0083] | +0.0030 [-0.0044, +0.0102] | -0.0020 [-0.0044, +0.0003] | -0.0132 [-0.0251, +0.0011] | -0.0090 [-0.0209, +0.0060] |
| (ii) period + area | 9865 | CONTROL | +0.0090 [+0.0019, +0.0165] | +0.0108 [+0.0033, +0.0185] | -0.0018 [-0.0036, +0.0001] | -0.0294 [-0.0408, -0.0114] | -0.0222 [-0.0344, -0.0049] |
| (ii) period + area | 42160 | AESTHETIC | -0.0032 [-0.0098, +0.0035] | -0.0017 [-0.0081, +0.0049] | -0.0015 [-0.0038, +0.0006] | -0.0292 [-0.0380, -0.0154] | -0.0257 [-0.0347, -0.0114] |
| (ii) period + area | 42160 | CONTROL | +0.0002 [-0.0065, +0.0068] | +0.0028 [-0.0043, +0.0096] | -0.0025 [-0.0041, -0.0009] | +0.0032 [-0.0092, +0.0164] | +0.0108 [-0.0019, +0.0235] |
| (iii) period + area + type + style | 1254 | AESTHETIC | -0.0119 [-0.0192, -0.0044] | -0.0105 [-0.0178, -0.0026] | -0.0014 [-0.0024, -0.0003] | -0.0233 [-0.0313, -0.0115] | -0.0188 [-0.0268, -0.0079] |
| (iii) period + area + type + style | 1254 | CONTROL | -0.0093 [-0.0171, -0.0012] | -0.0082 [-0.0165, -0.0001] | -0.0011 [-0.0019, -0.0003] | -0.0187 [-0.0293, -0.0073] | -0.0150 [-0.0253, -0.0035] |
| (iii) period + area + type + style | 9865 | AESTHETIC | +0.0000 [-0.0099, +0.0104] | +0.0005 [-0.0099, +0.0106] | -0.0005 [-0.0014, +0.0004] | -0.0121 [-0.0213, -0.0008] | -0.0110 [-0.0199, +0.0001] |
| (iii) period + area + type + style | 9865 | CONTROL | +0.0005 [-0.0079, +0.0089] | +0.0015 [-0.0068, +0.0103] | -0.0010 [-0.0019, -0.0002] | -0.0202 [-0.0292, -0.0074] | -0.0165 [-0.0265, -0.0034] |
| (iii) period + area + type + style | 42160 | AESTHETIC | -0.0049 [-0.0136, +0.0042] | -0.0040 [-0.0128, +0.0054] | -0.0009 [-0.0018, +0.0000] | -0.0195 [-0.0278, -0.0084] | -0.0167 [-0.0250, -0.0053] |
| (iii) period + area + type + style | 42160 | CONTROL | -0.0023 [-0.0114, +0.0066] | -0.0013 [-0.0105, +0.0076] | -0.0009 [-0.0016, -0.0002] | +0.0041 [-0.0061, +0.0144] | +0.0071 [-0.0028, +0.0166] |

## Denominator stability (resampling of the two photograph sets; not a CI of R)

| direction | geometry | 2.5% | 97.5% |
|---|---|---|---|
| (i) original | G1 | 0.2320 | 0.3164 |
| (i) original | G2 | 0.2320 | 0.3164 |
| (ii) period + area | G1 | 0.2090 | 0.2806 |
| (ii) period + area | G2 | 0.1729 | 0.2267 |
| (iii) period + area + type + style | G1 | 0.1466 | 0.1988 |
| (iii) period + area + type + style | G2 | 0.1001 | 0.1266 |

## Reading

- G1 answers: does the output contrast align with the part of the photograph contrast not explained by the recorded covariates? The denominator changes with the adjustment, so R changes even if P does not.
- G2 removes from BOTH photographs and outputs the embedding directions along which the covariates shift the photographs; the number of removed directions grows with the covariates (type + style add many dummies), and genuine corpus differences aligned with those directions are removed too: attenuation under (iii) is expected by construction and is not evidence against transfer. Only G2 supports distance comparisons.
- Limits: linear additive adjustment on catalogue strings with pooled rare levels; no alias merging; A and C share few style categories (15) — the adjustment is partly a between-category contrast, not an identification of a preference effect.
