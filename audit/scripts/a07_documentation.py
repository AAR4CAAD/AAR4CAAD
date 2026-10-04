"""
Audit step 7 — documentation items that no calculation can replace (prompt section 8).

1. The "five summary measures" of the VLM sentence: located in ANALYSIS_PLAN.md §8.6 and vlm_report/report_replication_vlm.md.
2. Second screening: none exists in the records → blind material for an independent human screener is prepared
   (576 full-size images, random order, neutral codes, defect sheet; key kept apart in a DO_NOT_USE file).
3. Corpus construction: what the records document (criteria written on 2026-09-25, per-work relevance notes, two batches of
   300, 'brief' referenced in the metadata but not found) and what only the authors can state.
Writes outputs/report_documentation.md, outputs/second_screening/{manifest_blind.csv, defect_sheet.csv, ISTRUZIONI.md, images/}, outputs/second_screening_key_DO_NOT_USE.csv.
"""
import os
import re
import shutil

import numpy as np
import pandas as pd

from common import ANALYSIS, OUT, PROJECT, Export, Log, as_bool, write_md

log = Log("a07_documentation")
E = Export()

# ---------------------------------------------------------------- 1. VLM five measures
plan = open(os.path.join(ANALYSIS, "ANALYSIS_PLAN.md"), encoding="utf-8").read()
m = re.search(r"Measures named in advance[^\n]*\n?[^\n]*", open(os.path.join(ANALYSIS, "replication_vlm_analysis.py"), encoding="utf-8").read())
named = re.findall(r'NAMED = \[(.*?)\]', open(os.path.join(ANALYSIS, "replication_vlm_analysis.py"), encoding="utf-8").read(), re.S)
rep7 = pd.read_csv(os.path.join(ANALYSIS, "vlm_report", "results_vlm.csv"))
log("NAMED in replication_vlm_analysis.py:", named[0] if named else "not found")
sec86 = plan[plan.find("8.6"):plan.find("8.6") + 1800] if "8.6" in plan else ""
vlm_rows = pd.read_csv(os.path.join(ANALYSIS, "vlm_report", "results_replication_vlm.csv"))
five = vlm_rows[(vlm_rows.section.astype(str) == "1") & (vlm_rows.named_in_advance.astype(str).str.lower() == "true") & (vlm_rows.training_seed == "mean of the three")]
log(five[["measure", "estimate", "ci_low", "ci_high"]].to_string())
# the original (section 7) contrasts of the nine items + composites, three-model z
orig = rep7[(rep7.model.astype(str).str.contains("three", case=False)) & (rep7.analysis.astype(str).str.contains("AESTHETIC − CONTROL|A − C|AESTHETIC-CONTROL", regex=True))] if "model" in rep7.columns else pd.DataFrame()
log("results_vlm.csv columns:", rep7.columns.tolist()); log(rep7.head(3).to_string()[:800])

# ---------------------------------------------------------------- 2. second screening material
G = E.csv("generated_images.csv"); G["o"] = G.opaque_id.str.replace("-", "").str.lower()
src = os.path.join(ANALYSIS, "vlm", "images")
dst = os.path.join(OUT, "second_screening"); os.makedirs(os.path.join(dst, "images"), exist_ok=True)
rng = np.random.default_rng(20261003)
order = rng.permutation(len(G))
codes = [f"S{i + 1:03d}" for i in range(len(G))]
man, key = [], []
for code, i in zip(codes, order):
    r = G.iloc[i]; f = os.path.join(src, r.o + ".jpg")
    ok = os.path.exists(f)
    if ok and not os.path.exists(os.path.join(dst, "images", code + ".jpg")):
        shutil.copyfile(f, os.path.join(dst, "images", code + ".jpg"))
    man.append(dict(code=code, file=f"images/{code}.jpg", width=r.width, height=r.height, available=ok))
    key.append(dict(code=code, opaque_id=r.o, condition=r.condition_code, prompt_code=r.prompt_code, seed=r.seed, original_review_defects=r.review_defects if isinstance(r.review_defects, str) else "", excluded_by_review_rule=r.excluded_by_review_rule))
pd.DataFrame(man).to_csv(os.path.join(dst, "manifest_blind.csv"), index=False)
pd.DataFrame(key).to_csv(os.path.join(OUT, "second_screening_key_DO_NOT_USE.csv"), index=False)
sheet = pd.DataFrame({"code": codes, "Perspective": "", "Deformation": "", "WrongSubject": "", "Artefacts": "", "Other": "", "note": ""})
sheet.to_csv(os.path.join(dst, "defect_sheet.csv"), index=False)
defects = G.review_defects.dropna().str.split(", ").explode().value_counts().to_dict()
instr = ["# Second blind screening — instructions for the independent screener", "",
         "Status: retrospective verification requested by the reviewer. It does not change the images shown to the participants in 2026; it measures the agreement of an independent screener with the original screening.", "",
         "## What you receive", "", "- `images/S001.jpg … S576.jpg`: the 576 generated images at full size (1216 × 832), in random order, with neutral codes. Nothing in the file name or the image reveals the model condition, the prompt or the seed.",
         "- `defect_sheet.csv`: one row per image with empty columns.", "", "## What you must not have", "", "- the key (condition / prompt / seed per code) — it is kept by the audit in a separate file and opened only after your sheet is returned;",
         "- the original screening decisions.", "", "## Task", "",
         "Look at every image once, in the given order, and mark with `1` each defect category that is clearly present (leave empty otherwise). Categories are those of the original review rule v1 (`generated_images.review_defects`):",
         "- **Perspective**: implausible or broken perspective, inconsistent vanishing lines, leaning or warped building volumes.",
         "- **Deformation**: deformed structural elements (windows, columns, roofs, stairs), melted or duplicated parts, impossible geometry.",
         "- **WrongSubject**: the image does not show a building/architecture as the main subject.",
         "- **Artefacts**: rendering artefacts (noise, smearing, text/logo fragments, split images).",
         "- **Other**: any other defect that in your judgement would exclude the image from a human aesthetic evaluation (describe it in `note`).",
         "Mark defects, not taste: 'ugly' is not a defect. Spend about the same time on every image; do not go back to compare images.", "",
         "## What will be computed afterwards", "",
         f"- Agreement with the original screening (48 flagged images: {defects}) per image and per category: Cohen's κ, prevalence of flags per condition in your sheet (the original had BASE 21, AESTHETIC 14, CONTROL 13).",
         "- Whether the triplet-exclusion rule applied to your flags would have excluded a different set of triplets, and the human contrasts recomputed on the triplets that survive BOTH screenings (sensitivity, not a replacement of the original analysis).", "",
         "The original screening was done by one researcher who knew the study; you do not know the conditions. The comparison is therefore an agreement study between a blind and an informed-but-condition-masked rater, declared as retrospective.", ""]
open(os.path.join(dst, "ISTRUZIONI.md"), "w", encoding="utf-8").write("\n".join(instr))
log("second screening material:", len(man), "images;", sum(x["available"] for x in man), "copied")

# ---------------------------------------------------------------- 3. corpus construction records
M = E.csv("image_metadata.csv"); SI = E.csv("source_images.csv")
notes = M.notes.dropna(); rel = M.award_or_relevance.dropna()
note_kinds = notes.str.extract(r"^([^:(]+)")[0].str.strip().value_counts().head(12).to_dict()
if not os.path.exists(os.path.join(E.folder, "audit_log.csv")):
    raise SystemExit("This step needs the complete platform audit log (not redistributed: it contains participant-level events). Its outputs, produced on the full export on 2026-10-03, are in outputs/ (report_runs_timeline.md, timeline_full.csv, runs_all.csv, cloud_jobs.csv, report_documentation.md).")
A = E.csv("audit_log.csv"); ext = A[A.action == "corpus.extended"].iloc[0]
plan_doc = os.path.join(os.path.expanduser("~"), "Downloads", "AAR_LNCS_15_pagine.docx")
L = ["# Documentation items (audit rev12)", "",
     "## 1. The 'five summary measures' of the VLM sentence (manuscript 5.2)", "",
     "They exist and are identifiable: `analysis/ANALYSIS_PLAN.md` §8.6 names, BEFORE the replication VLM run (dated note 2026-10-02), the five measures that had a contrast with interval above zero in the original VLM analysis (`vlm_report/report_vlm.md` §7): "
     f"{', '.join(five.measure.tolist())}. `replication_vlm_analysis.py` carries them as `NAMED`. The question fixed in advance: does each reappear with a positive sign for the three paired training seeds? Result (`report_replication_vlm.md` §1, three-model z, mean of the three seeds):", "",
     "| measure | original 159 triplets (z) | mean of the three seeds (95% CI) |", "|---|---|---|"]
ref7 = {}
try:
    rr = pd.read_csv(os.path.join(ANALYSIS, "vlm_report", "results_replication_vlm.csv"))
except Exception:
    rr = pd.DataFrame()
for _, r in five.iterrows():
    L.append(f"| {r.measure} | see report_vlm.md §7 | {r.estimate:+.3f} ({r.ci_low:+.3f} / {r.ci_high:+.3f}) |")
L += ["", "Consequence for the manuscript: do NOT delete the sentence; replace 'cinque misure riassuntive' with the five names (the four items of the rubric and the composite `representation_quality`), say where they were named in advance and that none keeps a positive sign across the three seeds. The nine rubric items and the two composites are in `vlm/rubric_v1.txt` and `ANALYSIS_PLAN.md` §7.", "",
      "## 2. Second screening", "",
      f"No second screening exists in the records: the 48 defect flags were saved by one account (`admin@research.local`) between 13:25 and 15:14 UTC on 2026-09-28 (`manual_correction` events) and the rule applied at 15:29–15:31. Defect categories used: {defects}. "
      "Material for an independent screener is in `outputs/second_screening/` (576 full-size images, random order, codes S001–S576, defect sheet, instructions); the key is `outputs/second_screening_key_DO_NOT_USE.csv`. No evaluation has been generated; a VLM is not a substitute. This will be a retrospective agreement study.", "",
      "## 3. How the 600 photographs were chosen — what is documented", "",
      f"- Inclusion criteria written before the collection: `AAR_LNCS_15_pagine.docx` (file dated 2026-09-25 13:41, 11 minutes after the import of batch 1 at 13:30) states: realised works from 1919–1920 to today, source exclusively Wikimedia Commons, admission motivated by presence in the literature, critical recognition, award or typological/constructive relevance, explicit attention to industrial architecture, one photograph per work, legible whole building, no drawings/renders/details/degraded files. It also planned a CONTROL 'comparable by period and type' and 'the same caption procedure for both samples'.",
      f"- Per-work justification: `image_metadata.award_or_relevance` filled for {len(rel)} of 600 works (e.g. {rel.sample(3, random_state=2).tolist()}); `notes` for {len(notes)} works with kinds {note_kinds}. The notes mention a **'brief'** ('named reference in brief', 'pre-1919 precedent explicitly named in the brief') and a **'batch-1 list'** with a 'balancing step': these documents (the brief and the candidate lists) are NOT in the repository, the export or the Downloads folder searched.",
      f"- Two batches: 300 photographs imported 2026-09-25 13:30 (batch 1) and 300 on 2026-09-26 13:45 (batch 2, `corpus.extended`, anchor share {0.34}, reason '{ext.reason}'), during phase 1 with protocol version 2.",
      "- Not recorded anywhere: who compiled the candidate lists (author, assistant, LLM), from which sources, how many candidates were discarded, and who approved each photograph. Only the authors can state this; the audit must not infer it.", "",
      "## 4. Ethics, conflicts, repository", "",
      "No institutional approval or exemption document exists in the materials; the consent text and the anonymous design are documented (`protocol/consent_text.md` in the supplement). Conflicts of interest: placeholder in the manuscript, no author statement available. Anonymous repository: a build exists (`arch300-anonymous-supplement`, currently published under a personal account, not yet anonymous); the URL to cite must be the anonymous host chosen by the authors. None of these is closable by the audit.", ""]
write_md("report_documentation.md", L)
log("done")
