"""
Integration step 3 — captions v1 → v2: coverage, materially changed texts, review of the whole set, and what was ADDED
(0→1 / 1→0 / unchanged per descriptor and corpus with the same lexicon of the audit). No new training.
Writes integrazione/caption_v1_v2_transizioni.csv and integrazione/report_caption_v1_v2.md.
"""
import json
import os
import re
import unicodedata

import pandas as pd

from common import AUDIT, PREVIOUS_REPLY, Export, Log, as_bool

OUTI = os.path.join(AUDIT, "integrazione"); log = Log("b03_caption_v1_v2"); E = Export()
A_ds = E.csv("aesthetic_dataset.csv"); C_ds = E.csv("control_dataset.csv"); CAP = E.csv("captions.csv")
snap = {}
for ds, code in (("AESTHETIC", "AESTHETIC"), ("CONTROL", "CONTROL")):
    src = A_ds if ds == "AESTHETIC" else C_ds
    for v in (1, 2):
        d = src[src.dataset_code == f"{code}-v{v}"].set_index("image_code").caption_snapshot; snap[(ds, v)] = d
for ds in ("AESTHETIC", "CONTROL"):
    assert set(snap[(ds, 1)].index) == set(snap[(ds, 2)].index) and len(snap[(ds, 2)]) == 89
cur = CAP[as_bool(CAP.is_current)].set_index("image_code")
rows_cov = []
for ds in ("AESTHETIC", "CONTROL"):
    v1, v2 = snap[(ds, 1)], snap[(ds, 2)].reindex(snap[(ds, 1)].index)
    changed = (v1 != v2); rev = cur.reindex(v2.index)
    n_versions = CAP[CAP.image_code.isin(v2.index)].groupby("image_code").size()
    rows_cov.append(dict(corpus=ds, photographs=89, captions_v2=int(v2.notna().sum()), texts_changed_v1_to_v2=int(changed.sum()), texts_unchanged=int((~changed).sum()),
                         current_caption_equals_v2=int((rev.text == v2).sum()), current_reviewed_flag=int(as_bool(rev.reviewed).sum()), reviewed_by=json.dumps(rev.reviewed_by.value_counts().to_dict()),
                         reviewed_at_min=str(rev.reviewed_at.min()), reviewed_at_max=str(rev.reviewed_at.max()), source_of_current=json.dumps(rev.source.value_counts().to_dict()), model_field_filled=int(rev.model.notna().sum()),
                         caption_versions_per_photo_min_median_max=f"{int(n_versions.min())}/{int(n_versions.median())}/{int(n_versions.max())}", mean_words_v1=round(float(v1.str.split().str.len().mean()), 1), mean_words_v2=round(float(v2.str.split().str.len().mean()), 1)))
COV = pd.DataFrame(rows_cov); log(COV.T.to_string())
# were the unchanged CONTROL texts re-reviewed (reviewed_at after the v1 snapshot)?
v1_frozen = pd.to_datetime(C_ds[C_ds.dataset_code == "CONTROL-v1"].frozen_at.iloc[0], utc=True)
unch = snap[("CONTROL", 1)].index[(snap[("CONTROL", 1)] == snap[("CONTROL", 2)].reindex(snap[("CONTROL", 1)].index)).to_numpy()]
rev_unch = pd.to_datetime(cur.reindex(unch).reviewed_at, utc=True)
log("CONTROL unchanged texts:", len(unch), "| reviewed after the v1 freeze:", int((rev_unch > v1_frozen).sum()), "| reviewed before:", int((rev_unch <= v1_frozen).sum()))
# audit events on captions (full log available in the authors' environment only)
ev = {}
if os.path.exists(os.path.join(E.folder, "audit_log.csv")):
    A = E.csv("audit_log.csv"); cc = A[A.action == "caption.changed"]; cr = A[A.action == "caption.reviewed"]
    ev = dict(caption_changed=len(cc), caption_changed_span=f"{cc.created_at.min()} → {cc.created_at.max()}", caption_changed_by=cc.user.value_counts().to_dict(), caption_reviewed=len(cr), caption_reviewed_span=f"{cr.created_at.min()} → {cr.created_at.max()}", caption_reviewed_by=cr.user.value_counts().to_dict())
    log(json.dumps(ev))
# lexicon transitions
LEX = json.load(open(os.path.join(PREVIOUS_REPLY, "caption_lexicon_v1.json"), encoding="utf-8"))
norm = lambda s: unicodedata.normalize("NFKC", s).lower().translate(str.maketrans("–—−", "---"))
def present(text, patterns):
    t = norm(text)
    for p in patterns:
        for m in re.finditer(p, t):
            clause = re.split(r"[,.;:!?]|\bbut\b|\bhowever\b", t[:m.start()])[-1]; clause = re.sub(r"\bnot only\b", "", clause)
            if not re.search(r"\b(?:no|not|without|lack|lacking|absence|absent|never)\b", clause): return True
    return False
rows = []
for f in LEX["features"]:
    if not f["patterns"]: continue
    for ds in ("AESTHETIC", "CONTROL"):
        v1, v2 = snap[(ds, 1)], snap[(ds, 2)].reindex(snap[(ds, 1)].index)
        p1 = v1.apply(lambda t: present(t, f["patterns"])); p2 = v2.apply(lambda t: present(t, f["patterns"]))
        rows.append(dict(feature=f["feature"], corpus=ds, present_v1=int(p1.sum()), present_v2=int(p2.sum()), added_0_to_1=int((~p1 & p2).sum()), removed_1_to_0=int((p1 & ~p2).sum()), unchanged_present=int((p1 & p2).sum()), unchanged_absent=int((~p1 & ~p2).sum())))
TR = pd.DataFrame(rows); TR.to_csv(os.path.join(OUTI, "caption_v1_v2_transizioni.csv"), index=False)
piv = TR.pivot(index="feature", columns="corpus", values=["present_v1", "present_v2", "added_0_to_1", "removed_1_to_0"])
L = ["# Captions v1 → v2: coverage, changes, review, additions (documentation, no new training)", "",
     "## 1. Coverage and materially changed texts", "", "| field | AESTHETIC | CONTROL |", "|---|---|---|", *[f"| {c} | {COV.iloc[0][c]} | {COV.iloc[1][c]} |" for c in COV.columns if c != "corpus"], "",
     f"Three distinct facts: (1) final coverage: 89 + 89 photographs, each with a frozen v2 caption; (2) texts materially different between the v1 and v2 snapshots: AESTHETIC {int(COV.set_index('corpus').loc['AESTHETIC', 'texts_changed_v1_to_v2'])}/89, CONTROL {int(COV.set_index('corpus').loc['CONTROL', 'texts_changed_v1_to_v2'])}/89; "
     f"(3) review: every one of the 178 current captions carries `reviewed = true` with a reviewer account and a timestamp; of the {len(unch)} CONTROL texts left unchanged, {int((rev_unch > v1_frozen).sum())} carry a review timestamp later than the v1 freeze (re-confirmed without modification) and {int((rev_unch <= v1_frozen).sum())} carry only the review timestamp of the v1 stage. "
     "An unchanged text does not prove it was ignored, but the records contain NO event of re-reading or re-confirmation of those 27 texts during the v2 rewrite: whether they were re-read under the v2 instructions can only be stated by the authors.", "",
     "What the records say about the workflow: every photograph has 1–9 caption versions (Italian drafts first, e.g. 'fotografia esterna di una scuola…', then English texts); all 178 current captions have `source = Imported` (CSV import) and an empty `model` field; review flags set by two staff accounts" + (f"; {ev.get('caption_changed')} `caption.changed` and {ev.get('caption_reviewed')} `caption.reviewed` events between 27 Sep 13:48 and 28 Sep 01:29 UTC" if ev else "") + ". "
     "NOT in the records: who wrote the English texts (person or tool), tool and version, the instructions given for the v2 rewrite, and whether the same instructions were applied to the 27 CONTROL texts that were confirmed unchanged.", "",
     "## 2. What was added or removed in v2 (same lexicon as the audit; counts of captions)", "",
     "| descriptor | A v1 | A v2 | A added 0→1 | A removed 1→0 | C v1 | C v2 | C added 0→1 | C removed 1→0 |", "|---|---|---|---|---|---|---|---|---|"]
for feat in piv.index:
    g = lambda col, c: int(piv.loc[feat, (col, c)])
    L.append(f"| {feat} | {g('present_v1', 'AESTHETIC')} | {g('present_v2', 'AESTHETIC')} | {g('added_0_to_1', 'AESTHETIC')} | {g('removed_1_to_0', 'AESTHETIC')} | {g('present_v1', 'CONTROL')} | {g('present_v2', 'CONTROL')} | {g('added_0_to_1', 'CONTROL')} | {g('removed_1_to_0', 'CONTROL')} |")
L += ["", "Final frequencies are not frequencies of additions: the 'added' columns count captions where a lexical group appears in v2 and not in v1. The audit-log note for v2 ('captions describing vegetation, sky and light') is visible in the greenery/sunny/brightness rows if the additions concentrate there.", "",
      "## 3. Single collected question for the authors", "",
      "For the 178 captions (v1 English texts and the v2 rewrite): who produced the texts (person/tool and version), with which written instructions, were the instructions identical for AESTHETIC and CONTROL, and were all 89 CONTROL texts re-read under the v2 instructions (27 were confirmed unchanged)? The records give coverage, timestamps and reviewer accounts only.", ""]
open(os.path.join(OUTI, "report_caption_v1_v2.md"), "w", encoding="utf-8").write("\n".join(L)); COV.to_csv(os.path.join(OUTI, "caption_v1_v2_copertura.csv"), index=False); log("done")
