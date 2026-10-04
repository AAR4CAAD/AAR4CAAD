# Documentation items (audit rev12)

## 1. The 'five summary measures' of the VLM sentence (manuscript 5.2)

They exist and are identifiable: `analysis/ANALYSIS_PLAN.md` §8.6 names, BEFORE the replication VLM run (dated note 2026-10-02), the five measures that had a contrast with interval above zero in the original VLM analysis (`vlm_report/report_vlm.md` §7): representation_quality, proportional_coherence, component_coherence, material_rendering, photographic_composition. `replication_vlm_analysis.py` carries them as `NAMED`. The question fixed in advance: does each reappear with a positive sign for the three paired training seeds? Result (`report_replication_vlm.md` §1, three-model z, mean of the three seeds):

| measure | original 159 triplets (z) | mean of the three seeds (95% CI) |
|---|---|---|
| representation_quality | see report_vlm.md §7 | -0.056 (-0.182 / +0.073) |
| proportional_coherence | see report_vlm.md §7 | -0.046 (-0.156 / +0.059) |
| component_coherence | see report_vlm.md §7 | -0.130 (-0.245 / -0.019) |
| material_rendering | see report_vlm.md §7 | +0.001 (-0.118 / +0.119) |
| photographic_composition | see report_vlm.md §7 | -0.027 (-0.180 / +0.131) |

Consequence for the manuscript: do NOT delete the sentence; replace 'cinque misure riassuntive' with the five names (the four items of the rubric and the composite `representation_quality`), say where they were named in advance and that none keeps a positive sign across the three seeds. The nine rubric items and the two composites are in `vlm/rubric_v1.txt` and `ANALYSIS_PLAN.md` §7.

## 2. Second screening

No second screening exists in the records: the 48 defect flags were saved by one account (`admin@research.local`) between 13:25 and 15:14 UTC on 2026-09-28 (`manual_correction` events) and the rule applied at 15:29–15:31. Defect categories used: {'Perspective': 23, 'Deformation': 21, 'Artefacts': 3, 'WrongSubject': 2}. Material for an independent screener is in `outputs/second_screening/` (576 full-size images, random order, codes S001–S576, defect sheet, instructions); the key is `outputs/second_screening_key_DO_NOT_USE.csv`. No evaluation has been generated; a VLM is not a substitute. This will be a retrospective agreement study.

## 3. How the 600 photographs were chosen — what is documented

- Inclusion criteria written before the collection: `AAR_LNCS_15_pagine.docx` (file dated 2026-09-25 13:41, 11 minutes after the import of batch 1 at 13:30) states: realised works from 1919–1920 to today, source exclusively Wikimedia Commons, admission motivated by presence in the literature, critical recognition, award or typological/constructive relevance, explicit attention to industrial architecture, one photograph per work, legible whole building, no drawings/renders/details/degraded files. It also planned a CONTROL 'comparable by period and type' and 'the same caption procedure for both samples'.
- Per-work justification: `image_metadata.award_or_relevance` filled for 600 of 600 works (e.g. ['inverted-pyramid landmark of Bratislava', 'Pritzker Prize architect; first Gehry building in Europe', 'Pritzker Prize architect; canonical postmodern museum']); `notes` for 155 works with kinds {'Commons assessment': 79, 'seed from the batch-1 list': 70, 'pre-1919 precedent explicitly named in the brief': 1, 'best available free exterior view; railing in foreground': 1, 'historical photograph': 1, "seed originally Unité d'Habitation Marseille; replaced by the Berlin Unité for licensing reasons": 1, 'only usable free exterior; overhead cables cross the frame': 1, 'building occupies a small part of the frame': 1}. The notes mention a **'brief'** ('named reference in brief', 'pre-1919 precedent explicitly named in the brief') and a **'batch-1 list'** with a 'balancing step': these documents (the brief and the candidate lists) are NOT in the repository, the export or the Downloads folder searched.
- Two batches: 300 photographs imported 2026-09-25 13:30 (batch 1) and 300 on 2026-09-26 13:45 (batch 2, `corpus.extended`, anchor share 0.34, reason 'penso sia sensato aggiungere'), during phase 1 with protocol version 2.
- Not recorded anywhere: who compiled the candidate lists (author, assistant, LLM), from which sources, how many candidates were discarded, and who approved each photograph. Only the authors can state this; the audit must not infer it.

## 4. Ethics, conflicts, repository

No institutional approval or exemption document exists in the materials; the consent text and the anonymous design are documented (`protocol/consent_text.md` in the supplement). Conflicts of interest: placeholder in the manuscript, no author statement available. Anonymous repository: a build exists (`arch300-anonymous-supplement`, currently published under a personal account, not yet anonymous); the URL to cite must be the anonymous host chosen by the authors. None of these is closable by the audit.

