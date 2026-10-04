# Captions — re-count, dictionary audit, lexical vs visual (audit rev12)

Captions used in the evaluated trainings: the frozen `caption_snapshot` of AESTHETIC-v2 and CONTROL-v2 (89 + 89); the platform writes them to `captions/<code>.txt` of the training zip and `aar_worker.py` encodes them with the frozen SDXL text encoders (only the UNet attention LoRA is trained). Captions changed between v1 and v2: AESTHETIC 89/89, CONTROL 62/89 (554 `caption.changed` events, 2026-09-27T13:48 → 2026-09-28T01:28 UTC). Caption `source` values: {'Imported': 329, 'Manual': 225}; `model` field never filled: the export does not record who/what wrote the text (author's statement needed).

## 1. Re-count with the previous reply's lexicon and code

Counts identical to `06_caption_feature_counts.csv` for 28 of 28 operationalised descriptors (exact re-execution of the matching code on the same frozen captions). Every hit with its fragment: `caption_hits_audit.csv`. Negated hits found: 0.

## 2. Dictionary audit (declared before the variant counts)

| descriptor | issue |
|---|---|
| curved_organic | extended set aggregates arches, domes, round, circular, cylindrical, shells, spheres, oval with curved/undulating/organic |
| urban | 'city' matches building names/types such as 'city hall' |
| sharpness | 'sharp' in captions describes angles/edges (shape), not image sharpness |
| detail | 'detailed/details' describes ornament or facade articulation, not pixel detail |
| monumental | 'massive' describes volume/material mass; 'imposing' size |
| brightness | 'bright' often qualifies a colour (bright red), not luminance |
| warmth | 'warm' qualifies material colour (warm brick) as much as light |
| real_photo | every caption starts with 'exterior photograph of': constant 89/89, not informative |
| colourful | duplicate of colorfulness (same patterns): one test, not two |
| greenery | very broad (trees, lawn, park, plants, landscaped); 55/55 constant-ish |
| water | 'pool' may be a swimming pool (water anyway); 'harbour' context |
| white | also 'white' in 'black and white' (vintage) or 'white concrete' (material colour): kept |

| definition | AESTHETIC /89 | CONTROL /89 |
|---|---|---|
| curved_organic STRICT (curve*, undulating, organic, sinuous, flowing) | 20 | 14 |
| curved_organic EXTENDED (previous reply) | 37 | 27 |
| curved_organic: arches/domes/round/circular/cylindrical/shell/sphere/oval ONLY | 19 | 17 |
| curved word alone | 16 | 14 |
| urban EXTENDED (previous reply) | 14 | 12 |
| urban without 'city hall/gate/library' | 14 | 12 |
| sharpness EXTENDED | 2 | 0 |
| sharpness without shape uses | 1 | 0 |
| brightness EXTENDED | 4 | 1 |
| brightness without colour uses | 1 | 1 |

Reading: the extended 'curved' group (37/27 in the previous reply) is driven by arches, domes, round and shell terms; the strict shape vocabulary gives the counts in the first row. Both are reported; neither was chosen for agreement with the visual results. Fragments of every ambiguous term: `caption_ambiguous_fragments.csv`.

## 3. Lexical contrast vs visual contrast, descriptor by descriptor

| descriptor | status | A | C | lexical A−C (share) | 95% CI | Fisher p | x photos (SD) | a−c outputs (SD) | sign lex = x | sign lex = outputs | r(presence, descriptor value) over 178 photos |
|---|---|---|---|---|---|---|---|---|---|---|---|
| brightness | lexical proxy | 4.0 | 1.0 | +0.034 | -0.023 / +0.099 | 0.3679 | +0.03 | -0.23 | True | False | -0.057 |
| contrast | constant (0/0) | 0.0 | 0.0 | +0.000 | +nan / +nan | nan | -0.37 | -0.15 |  |  | nan |
| saturation | constant (0/0) | 0.0 | 0.0 | +0.000 | +nan / +nan | nan | +0.22 | +0.28 |  |  | nan |
| colorfulness | lexical proxy | 1.0 | 2.0 | -0.011 | -0.068 / +0.041 | 1.0 | +0.11 | +0.12 | False | False | 0.116 |
| warmth | lexical proxy | 2.0 | 0.0 | +0.022 | -0.022 / +0.078 | 0.4972 | +0.05 | -0.19 | True | False | 0.02 |
| sharpness | lexical proxy | 2.0 | 0.0 | +0.022 | -0.022 / +0.078 | 0.4972 | +0.08 | +0.11 | True | True | -0.065 |
| detail | constant (0/0) | 0.0 | 0.0 | +0.000 | +nan / +nan | nan | +0.03 | +0.13 |  |  | nan |
| sky_brightness | not operationalised (image measure only) | nan | nan | +nan | +nan / +nan | nan | -0.19 | -0.21 |  |  | nan |
| dark_share | not operationalised (image measure only) | nan | nan | +nan | +nan / +nan | nan | -0.13 | +0.10 |  |  | nan |
| bright_share | not operationalised (image measure only) | nan | nan | +nan | +nan / +nan | nan | -0.03 | -0.06 |  |  | nan |
| whole_building | constant (0/0) | 0.0 | 0.0 | +0.000 | +nan / +nan | nan | -0.02 | -0.14 |  |  | nan |
| low_angle | lexical proxy | 20.0 | 12.0 | +0.090 | -0.024 / +0.202 | 0.1712 | +0.41 | +0.20 | True | True | 0.076 |
| sunny | lexical proxy | 1.0 | 1.0 | +0.000 | -0.051 / +0.051 | 1.0 | +0.00 | +0.10 |  |  | 0.057 |
| vintage_photo | lexical proxy | 0.0 | 1.0 | -0.011 | -0.061 / +0.031 | 1.0 | -0.26 | -0.20 | True | True | 0.119 |
| real_photo | constant (89/89) | 89.0 | 89.0 | +0.000 | +nan / +nan | nan | +0.07 | +0.18 |  |  | nan |
| people | lexical proxy | 15.0 | 9.0 | +0.067 | -0.035 / +0.170 | 0.2724 | -0.13 | -0.16 | False | False | 0.306 |
| cars | lexical proxy | 6.0 | 8.0 | -0.022 | -0.108 / +0.062 | 0.7818 | -0.41 | -0.22 | True | True | 0.231 |
| greenery | lexical proxy | 55.0 | 55.0 | +0.000 | -0.140 / +0.140 | 1.0 | +0.10 | -0.02 |  |  | 0.302 |
| water | lexical proxy | 28.0 | 10.0 | +0.202 | +0.083 / +0.316 | 0.0016 | +0.06 | +0.01 | True | True | 0.463 |
| urban | lexical proxy | 14.0 | 12.0 | +0.022 | -0.083 / +0.128 | 0.8323 | -0.26 | -0.09 | False | False | 0.265 |
| interior | lexical proxy | 1.0 | 0.0 | +0.011 | -0.031 / +0.061 | 1.0 | +0.45 | +0.09 | True | True | 0.279 |
| iconic_design | constant (0/0) | 0.0 | 0.0 | +0.000 | +nan / +nan | nan | +0.58 | +0.19 |  |  | nan |
| complex_form | lexical proxy | 6.0 | 7.0 | -0.011 | -0.094 / +0.071 | 1.0 | +0.35 | +0.17 | False | False | 0.13 |
| curved_organic | lexical proxy | 37.0 | 27.0 | +0.112 | -0.028 / +0.247 | 0.1595 | +0.61 | +0.10 | True | True | 0.505 |
| monumental | lexical proxy | 0.0 | 1.0 | -0.011 | -0.061 / +0.031 | 1.0 | +0.42 | +0.11 | False | False | 0.132 |
| contemporary | constant (0/0) | 0.0 | 0.0 | +0.000 | +nan / +nan | nan | +0.43 | +0.29 |  |  | nan |
| glass | lexical proxy | 44.0 | 38.0 | +0.067 | -0.078 / +0.209 | 0.4522 | +0.37 | +0.09 | True | True | 0.403 |
| concrete | lexical proxy | 17.0 | 27.0 | -0.112 | -0.235 / +0.015 | 0.1173 | -0.58 | -0.10 | True | True | 0.147 |
| wood | lexical proxy | 8.0 | 4.0 | +0.045 | -0.033 / +0.127 | 0.3708 | -0.01 | -0.13 | False | False | 0.162 |
| white | lexical proxy | 46.0 | 41.0 | +0.056 | -0.089 / +0.198 | 0.5488 | -0.05 | -0.08 | False | False | 0.209 |
| colourful | duplicate of colorfulness | 1.0 | 2.0 | -0.011 | -0.068 / +0.041 | 1.0 | +0.11 | +0.01 | False | False | 0.331 |

Informative descriptors (lexical proxy, not constant, not duplicate, ≥ 5 mentions): 13. Profile associations across them (descriptors treated as equally weighted points; their mutual dependence is not modelled, bootstrap over descriptors only):
- lexical contrast vs photograph contrast x: Pearson +0.57 (bootstrap 95% -0.01 / +0.90), Spearman +0.59; same sign 7/13.
- lexical contrast vs output contrast a−c: Pearson +0.32 (95% -0.11 / +0.70), Spearman +0.42; same sign 6/13.
- the per-photograph column shows whether the lexical presence tracks the visual descriptor of the same photograph (CLIP/pixel value): where it does, text and image carry the same information and the lexical analysis cannot separate the two channels.

## 4. The review's sentence 'not for cars and glass'

- cars: lexicon A 6.0 / C 8.0 (contrast -0.022); photographs x = -0.41; outputs a−c = -0.22. Signs: lexical vs photos same = True; lexical vs outputs same = True.
- glass: lexicon A 44.0 / C 38.0 (contrast +0.067); photographs x = +0.37; outputs a−c = +0.09. Signs: lexical vs photos same = True; lexical vs outputs same = True.
Directional agreement is not significance (both Fisher p above): the lexical differences for cars and glass are small and compatible with chance, but their direction does NOT contradict the visual contrasts. The review's 'non per automobili e vetro' is not supported as a statement about direction; it is defensible only as 'not distinguishable from zero'.

## 5. What this does and does not establish

The captions of the two corpora differ lexically in the same direction as several visual descriptors (and track them photograph by photograph): the text channel is confounded with the image channel in the training data. The lexical analysis therefore cannot attribute the transfer to images or to text; only the controlled-caption training (`PROTOCOLLO_CAPTION_CONTROLLATE.md`) can. No training with controlled captions exists in the records (training_runs.csv: all runs use the v1/v2 captions of their corpus).

