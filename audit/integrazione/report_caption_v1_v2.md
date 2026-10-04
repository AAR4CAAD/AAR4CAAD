# Captions v1 → v2: coverage, changes, review, additions (documentation, no new training)

## 1. Coverage and materially changed texts

| field | AESTHETIC | CONTROL |
|---|---|---|
| photographs | 89 | 89 |
| captions_v2 | 89 | 89 |
| texts_changed_v1_to_v2 | 89 | 62 |
| texts_unchanged | 0 | 27 |
| current_caption_equals_v2 | 89 | 89 |
| current_reviewed_flag | 89 | 89 |
| reviewed_by | {"admin@research.local": 89} | {"admin@research.local": 62, "researcher@research.local": 27} |
| reviewed_at_min | 2026-09-28T01:28:46.447Z | 2026-09-27T20:48:19.387Z |
| reviewed_at_max | 2026-09-28T01:28:47.162Z | 2026-09-28T01:29:17.725Z |
| source_of_current | {"Imported": 89} | {"Imported": 89} |
| model_field_filled | 0 | 0 |
| caption_versions_per_photo_min_median_max | 3/4/9 | 1/2/4 |
| mean_words_v1 | 27.2 | 33.7 |
| mean_words_v2 | 35.3 | 35.1 |

Three distinct facts: (1) final coverage: 89 + 89 photographs, each with a frozen v2 caption; (2) texts materially different between the v1 and v2 snapshots: AESTHETIC 89/89, CONTROL 62/89; (3) review: every one of the 178 current captions carries `reviewed = true` with a reviewer account and a timestamp; of the 27 CONTROL texts left unchanged, 0 carry a review timestamp later than the v1 freeze (re-confirmed without modification) and 27 carry only the review timestamp of the v1 stage. An unchanged text does not prove it was ignored, but the records contain NO event of re-reading or re-confirmation of those 27 texts during the v2 rewrite: whether they were re-read under the v2 instructions can only be stated by the authors.

What the records say about the workflow: every photograph has 1–9 caption versions (Italian drafts first, e.g. 'fotografia esterna di una scuola…', then English texts); all 178 current captions have `source = Imported` (CSV import) and an empty `model` field; review flags set by two staff accounts; 554 `caption.changed` and 444 `caption.reviewed` events between 27 Sep 13:48 and 28 Sep 01:29 UTC. NOT in the records: who wrote the English texts (person or tool), tool and version, the instructions given for the v2 rewrite, and whether the same instructions were applied to the 27 CONTROL texts that were confirmed unchanged.

## 2. What was added or removed in v2 (same lexicon as the audit; counts of captions)

| descriptor | A v1 | A v2 | A added 0→1 | A removed 1→0 | C v1 | C v2 | C added 0→1 | C removed 1→0 |
|---|---|---|---|---|---|---|---|---|
| brightness | 1 | 4 | 4 | 1 | 7 | 1 | 0 | 6 |
| cars | 0 | 6 | 6 | 0 | 7 | 8 | 1 | 0 |
| colorfulness | 0 | 1 | 1 | 0 | 2 | 2 | 0 | 0 |
| colourful | 0 | 1 | 1 | 0 | 2 | 2 | 0 | 0 |
| complex_form | 12 | 6 | 2 | 8 | 7 | 7 | 1 | 1 |
| concrete | 31 | 17 | 2 | 16 | 27 | 27 | 1 | 1 |
| contemporary | 10 | 0 | 0 | 10 | 3 | 0 | 0 | 3 |
| contrast | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| curved_organic | 29 | 37 | 13 | 5 | 26 | 27 | 1 | 0 |
| detail | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| glass | 47 | 44 | 6 | 9 | 38 | 38 | 1 | 1 |
| greenery | 19 | 55 | 37 | 1 | 54 | 55 | 1 | 0 |
| iconic_design | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| interior | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| low_angle | 15 | 20 | 6 | 1 | 12 | 12 | 0 | 0 |
| monumental | 2 | 0 | 0 | 2 | 2 | 1 | 0 | 1 |
| people | 2 | 15 | 13 | 0 | 8 | 9 | 1 | 0 |
| real_photo | 89 | 89 | 0 | 0 | 89 | 89 | 0 | 0 |
| saturation | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| sharpness | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| sunny | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 0 |
| urban | 50 | 14 | 3 | 39 | 15 | 12 | 0 | 3 |
| vintage_photo | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| warmth | 2 | 2 | 2 | 2 | 1 | 0 | 0 | 1 |
| water | 17 | 28 | 11 | 0 | 10 | 10 | 0 | 0 |
| white | 15 | 46 | 32 | 1 | 29 | 41 | 12 | 0 |
| whole_building | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| wood | 8 | 8 | 0 | 0 | 4 | 4 | 0 | 0 |

Final frequencies are not frequencies of additions: the 'added' columns count captions where a lexical group appears in v2 and not in v1. The audit-log note for v2 ('captions describing vegetation, sky and light') is visible in the greenery/sunny/brightness rows if the additions concentrate there.

## 3. Single collected question for the authors

For the 178 captions (v1 English texts and the v2 rewrite): who produced the texts (person/tool and version), with which written instructions, were the instructions identical for AESTHETIC and CONTROL, and were all 89 CONTROL texts re-read under the v2 instructions (27 were confirmed unchanged)? The records give coverage, timestamps and reviewer accounts only.
