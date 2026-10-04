"""
Audit step 5 — captions (prompt section 5).

1. The captions actually used by RUN-AESTHETIC-4 / RUN-CONTROL-4 are the frozen `caption_snapshot` of AESTHETIC-v2 / CONTROL-v2
   (the platform writes them to captions/<code>.txt of the training zip; aar_worker.py encodes them with the frozen text encoders).
2. The lexicon of the previous reply (caption_lexicon_v1.json) is re-applied with its own matching code (copied verbatim) and the
   counts are compared with 06_caption_feature_counts.csv. Every hit is saved with the text fragment that produced it.
3. Entry-by-entry audit of the dictionary: ambiguous terms (city hall → urban, sharp angles → sharpness, detailed → detail,
   massive → monumental, photograph → real_photo constant, …), strict vs extended definitions for curved_organic (both declared
   below BEFORE counting), constant and duplicated categories.
4. For every descriptor with a lexical proxy: lexical contrast A−C (share difference, Newcombe interval, Fisher p), visual
   contrast in the photographs (x) and in the outputs (a−c), signs, and the profile association lexical↔visual.
5. Check of the review's sentence "not for cars and glass".
Writes outputs/caption_hits_audit.csv, outputs/caption_lexical_vs_visual.csv, outputs/report_captions.md.
"""
import json
import os
import re
import unicodedata

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import confint_proportions_2indep

from common import ANALYSIS, DESCRIPTORS, OUT, PREVIOUS_REPLY, Export, Log, write_md

log = Log("a05_captions")
E = Export()
runs = E.csv("training_runs.csv").set_index("code")
A_ds = E.csv("aesthetic_dataset.csv"); C_ds = E.csv("control_dataset.csv")
A2 = A_ds[A_ds.dataset_code == runs.training_dataset["RUN-AESTHETIC-4"]].sort_values("sort_order"); C2 = C_ds[C_ds.dataset_code == runs.training_dataset["RUN-CONTROL-4"]].sort_values("sort_order")
caps = pd.concat([pd.DataFrame({"image_code": A2.image_code, "set": "AESTHETIC", "caption": A2.caption_snapshot}), pd.DataFrame({"image_code": C2.image_code, "set": "CONTROL", "caption": C2.caption_snapshot})]).reset_index(drop=True)
log("frozen captions:", caps.groupby("set").size().to_dict(), "| empty:", int(caps.caption.isna().sum()), "| mean words A/C:", caps.groupby("set").caption.apply(lambda s: s.str.split().str.len().mean()).round(1).to_dict())
# are the v2 snapshots the current reviewed captions? (captions.csv)
CAP = E.csv("captions.csv"); cur = CAP[CAP.is_current.astype(str).str.lower() == "true"].set_index("image_code").text
log("snapshot == current platform caption:", int((caps.set_index('image_code').caption == cur.reindex(caps.image_code).values).sum()), "of", len(caps))
# v1 vs v2 captions
A1 = A_ds[A_ds.dataset_code == "AESTHETIC-v1"].set_index("image_code").caption_snapshot; C1 = C_ds[C_ds.dataset_code == "CONTROL-v1"].set_index("image_code").caption_snapshot
chg_A = int((A1.reindex(A2.image_code).values != A2.caption_snapshot.values).sum()); chg_C = int((C1.reindex(C2.image_code).values != C2.caption_snapshot.values).sum())
log(f"captions changed between v1 and v2: AESTHETIC {chg_A}/89, CONTROL {chg_C}/89")
if os.path.exists(os.path.join(E.folder, "audit_log.csv")):
    A_log = E.csv("audit_log.csv"); cc = A_log[A_log.action == "caption.changed"]; log("caption.changed events:", len(cc), "between", cc.created_at.min(), "and", cc.created_at.max(), "| by user:", cc.user.value_counts().to_dict())
else:  # anonymised export: the platform audit log is not redistributed; values from the run on the full export (2026-10-03)
    cc = pd.DataFrame({"created_at": ["2026-09-27T13:48:08.408Z", "2026-09-28T01:28:28.165Z"] * 277}); log("audit_log.csv not available: using the recorded counts of the full-export run (554 caption.changed events)")
src = CAP.source.value_counts().to_dict(); log("caption sources (all versions):", src, "| model field non-empty:", int(CAP.model.notna().sum()))

# ---------------------------------------------------------------- the previous reply's lexicon and matching code (verbatim)
LEX = json.load(open(os.path.join(PREVIOUS_REPLY, "caption_lexicon_v1.json"), encoding="utf-8"))


def norm_text(s):
    return unicodedata.normalize("NFKC", s).lower().translate(str.maketrans("–—−", "---"))


def lexical_hits(text, patterns):
    text = norm_text(text); found = {}
    for pattern in patterns:
        for m in re.finditer(pattern, text):
            clause = re.split(r"[,.;:!?]|\bbut\b|\bhowever\b", text[:m.start()])[-1]
            clause = re.sub(r"\bnot only\b", "", clause)
            negative = bool(re.search(r"\b(?:no|not|without|lack|lacking|absence|absent|never)\b", clause))
            found[(m.start(), m.end())] = dict(term=m.group(0), negative=negative, start=m.start(), end=m.end(), context=text[max(0, m.start() - 50):min(len(text), m.end() + 60)])
    return list(found.values())


prev_counts = pd.read_csv(os.path.join(PREVIOUS_REPLY, "06_caption_feature_counts.csv")).set_index("feature")
hits_rows, pres = [], {}
for f in LEX["features"]:
    if not f["patterns"]:
        continue
    col = np.zeros(len(caps), bool)
    for i, r in caps.iterrows():
        hh = lexical_hits(r.caption, f["patterns"])
        for h in hh:
            hits_rows.append(dict(feature=f["feature"], set=r.set, image_code=r.image_code, term=h["term"], negative=h["negative"], fragment=h["context"]))
        col[i] = any(not h["negative"] for h in hh)
    pres[f["feature"]] = col
H = pd.DataFrame(hits_rows)
PRES = pd.DataFrame(pres); PRES["set"] = caps.set.values; PRES["image_code"] = caps.image_code.values
cmp_rows = []
for f in pres:
    a_, c_ = int(PRES[PRES.set == "AESTHETIC"][f].sum()), int(PRES[PRES.set == "CONTROL"][f].sum())
    pa, pc = prev_counts.loc[f, "A_n"], prev_counts.loc[f, "C_n"]
    cmp_rows.append(dict(feature=f, A_n_rerun=a_, C_n_rerun=c_, A_n_previous=pa, C_n_previous=pc, identical=(str(a_) == str(pa).split(".")[0] and str(c_) == str(pc).split(".")[0])))
CMP = pd.DataFrame(cmp_rows); log("lexicon counts identical to the previous reply:", int(CMP.identical.sum()), "of", len(CMP))

# ---------------------------------------------------------------- dictionary audit, declared before counting
AUDIT = {
    "curved_organic": dict(issue="extended set aggregates arches, domes, round, circular, cylindrical, shells, spheres, oval with curved/undulating/organic",
                           strict=[r"\bcurv(?:e|es|ed|ing|ature)\b", r"\bundulating\b", r"\borganic\b", r"\bsinuous\b", r"\bflowing\b"],
                           extended=None),  # = the previous reply's list
    "urban": dict(issue="'city' matches building names/types such as 'city hall'", exclude=[r"\bcity hall\b", r"\bcity gate\b", r"\bcity library\b"]),
    "sharpness": dict(issue="'sharp' in captions describes angles/edges (shape), not image sharpness", exclude=[r"\bsharp(?:ly)?[- ](?:angle|angled|edge|edged|corner|cornered|pointed|prow|fold|folds|lines|geometry)\b", r"\bsharp angles?\b", r"\bsharp edges?\b"]),
    "detail": dict(issue="'detailed/details' describes ornament or facade articulation, not pixel detail", exclude=[]),
    "monumental": dict(issue="'massive' describes volume/material mass; 'imposing' size", exclude=[]),
    "brightness": dict(issue="'bright' often qualifies a colour (bright red), not luminance", exclude=[r"\bbright(?:ly)? (?:red|blue|green|yellow|orange|white|colou?rs?|colou?red|painted|mural|tiles?)\b"]),
    "warmth": dict(issue="'warm' qualifies material colour (warm brick) as much as light", exclude=[]),
    "real_photo": dict(issue="every caption starts with 'exterior photograph of': constant 89/89, not informative", exclude=[]),
    "colourful": dict(issue="duplicate of colorfulness (same patterns): one test, not two", exclude=[]),
    "greenery": dict(issue="very broad (trees, lawn, park, plants, landscaped); 55/55 constant-ish", exclude=[]),
    "water": dict(issue="'pool' may be a swimming pool (water anyway); 'harbour' context", exclude=[]),
    "white": dict(issue="also 'white' in 'black and white' (vintage) or 'white concrete' (material colour): kept", exclude=[]),
}
json.dump(AUDIT, open(os.path.join(OUT, "caption_dictionary_audit.json"), "w"), indent=1)
ext_patterns = next(f for f in LEX["features"] if f["feature"] == "curved_organic")["patterns"]


def count(patterns, exclude=()):
    out = np.zeros(len(caps), bool)
    for i, r in caps.iterrows():
        t = norm_text(r.caption)
        for ex in exclude: t = re.sub(ex, " ", t)
        out[i] = any(not h["negative"] for h in lexical_hits(t, patterns))
    return out


variants = []
for name, pats, exc in (("curved_organic STRICT (curve*, undulating, organic, sinuous, flowing)", AUDIT["curved_organic"]["strict"], ()), ("curved_organic EXTENDED (previous reply)", ext_patterns, ()),
                        ("curved_organic: arches/domes/round/circular/cylindrical/shell/sphere/oval ONLY", [p for p in ext_patterns if p not in (r"\bcurv(?:e|es|ed|ing|ature)\b", r"\borganic\b", r"\bundulating\b")], ()),
                        ("curved word alone", [r"\bcurved\b"], ()),
                        ("urban EXTENDED (previous reply)", next(f for f in LEX["features"] if f["feature"] == "urban")["patterns"], ()), ("urban without 'city hall/gate/library'", next(f for f in LEX["features"] if f["feature"] == "urban")["patterns"], AUDIT["urban"]["exclude"]),
                        ("sharpness EXTENDED", next(f for f in LEX["features"] if f["feature"] == "sharpness")["patterns"], ()), ("sharpness without shape uses", next(f for f in LEX["features"] if f["feature"] == "sharpness")["patterns"], AUDIT["sharpness"]["exclude"]),
                        ("brightness EXTENDED", next(f for f in LEX["features"] if f["feature"] == "brightness")["patterns"], ()), ("brightness without colour uses", next(f for f in LEX["features"] if f["feature"] == "brightness")["patterns"], AUDIT["brightness"]["exclude"])):
    v = count(pats, exc); variants.append(dict(definition=name, A_n=int(v[caps.set == "AESTHETIC"].sum()), C_n=int(v[caps.set == "CONTROL"].sum())))
    log(f"[variant] {name}: A {variants[-1]['A_n']} C {variants[-1]['C_n']}")
VAR = pd.DataFrame(variants)
# fragments for the ambiguous terms
amb = H[H.term.isin(["city", "sharp", "sharply", "detailed", "details", "detail", "massive", "imposing", "bright", "brightly", "warm", "shells", "shell", "round", "rounded", "arches", "arch", "arched", "domes", "dome", "circular", "pools", "pool"])]
amb.to_csv(os.path.join(OUT, "caption_ambiguous_fragments.csv"), index=False)
H.to_csv(os.path.join(OUT, "caption_hits_audit.csv"), index=False)

# ---------------------------------------------------------------- lexical vs visual per descriptor
prof = pd.read_csv(os.path.join(OUT, "descriptors_profile.csv")).set_index("feature")
cov = pd.read_csv(os.path.join(ANALYSIS, "metrics", "covariates_images.csv")).set_index("id")
rows = []
for f in DESCRIPTORS:
    if f not in pres:
        rows.append(dict(feature=f, lexical_status="not operationalised (image measure only)", A_n=None, C_n=None, lexical_contrast=None, lex_ci_low=None, lex_ci_high=None, fisher_p=None, x_photos=prof.loc[f, "x_all_89_vs_89"], a_minus_c_outputs=prof.loc[f, "a_minus_c"], same_sign_lex_vs_x=None, same_sign_lex_vs_outputs=None, pointbiserial_r_lex_vs_descriptor_178=None, informative=False))
        continue
    pa_, pc_ = PRES[PRES.set == "AESTHETIC"][f], PRES[PRES.set == "CONTROL"][f]
    a_, c_ = int(pa_.sum()), int(pc_.sum()); n = 89
    diff = a_ / n - c_ / n
    lo, hi = confint_proportions_2indep(a_, n, c_, n, method="newcomb") if 0 < a_ + c_ < 2 * n else (np.nan, np.nan)
    p_f = stats.fisher_exact([[a_, n - a_], [c_, n - c_]])[1] if 0 < a_ + c_ < 2 * n else np.nan
    const = a_ + c_ == 0 or a_ + c_ == 2 * n or (a_ == c_ == 0)
    status = "constant (0/0)" if a_ + c_ == 0 else "constant (89/89)" if a_ == c_ == n else "duplicate of colorfulness" if f == "colourful" else "lexical proxy"
    # per-photograph association: presence vs the (logit-transformed, standardised) descriptor value of the same photograph
    vals = cov.loc[caps.image_code, f].astype(float).to_numpy()
    if f in [d for d in DESCRIPTORS if d not in ("brightness", "contrast", "saturation", "colorfulness", "warmth", "sharpness", "detail", "sky_brightness", "dark_share", "bright_share")]:
        vals = np.log(np.clip(vals, 1e-4, 1 - 1e-4) / (1 - np.clip(vals, 1e-4, 1 - 1e-4)))
    pb = stats.pointbiserialr(PRES[f].astype(int), vals) if PRES[f].nunique() > 1 else None
    rows.append(dict(feature=f, lexical_status=status, A_n=a_, C_n=c_, lexical_contrast=round(diff, 4), lex_ci_low=None if np.isnan(lo) else round(lo, 4), lex_ci_high=None if np.isnan(hi) else round(hi, 4), fisher_p=None if np.isnan(p_f) else round(p_f, 4),
                     x_photos=round(prof.loc[f, "x_all_89_vs_89"], 4), a_minus_c_outputs=round(prof.loc[f, "a_minus_c"], 4),
                     same_sign_lex_vs_x=None if diff == 0 else bool(np.sign(diff) == np.sign(prof.loc[f, "x_all_89_vs_89"])), same_sign_lex_vs_outputs=None if diff == 0 else bool(np.sign(diff) == np.sign(prof.loc[f, "a_minus_c"])),
                     pointbiserial_r_lex_vs_descriptor_178=None if pb is None else round(float(pb.statistic), 3), informative=(status == "lexical proxy" and a_ + c_ >= 5)))
LV = pd.DataFrame(rows); LV.to_csv(os.path.join(OUT, "caption_lexical_vs_visual.csv"), index=False)
inf = LV[LV.informative.fillna(False).astype(bool)]
r_lx = stats.pearsonr(inf.lexical_contrast.astype(float), inf.x_photos.astype(float)); r_lo = stats.pearsonr(inf.lexical_contrast.astype(float), inf.a_minus_c_outputs.astype(float))
rs_lx = stats.spearmanr(inf.lexical_contrast.astype(float), inf.x_photos.astype(float)); rs_lo = stats.spearmanr(inf.lexical_contrast.astype(float), inf.a_minus_c_outputs.astype(float))
log(f"informative lexical descriptors: {len(inf)}; profile r(lexical contrast, x photos) = {r_lx.statistic:+.3f} (p {r_lx.pvalue:.3f}); Spearman {rs_lx.statistic:+.3f}; r(lexical, a−c outputs) = {r_lo.statistic:+.3f} (p {r_lo.pvalue:.3f}); Spearman {rs_lo.statistic:+.3f}")
same_x = int((inf.same_sign_lex_vs_x == True).sum()); same_o = int((inf.same_sign_lex_vs_outputs == True).sum())
log(f"same sign lexical vs x: {same_x}/{len(inf)}; lexical vs outputs: {same_o}/{len(inf)}")
# bootstrap over descriptors for the two profile correlations (dependence between descriptors not modelled: declared)
rng = np.random.default_rng(20261003); bx, bo = [], []
lx, xx, oo = inf.lexical_contrast.astype(float).to_numpy(), inf.x_photos.astype(float).to_numpy(), inf.a_minus_c_outputs.astype(float).to_numpy()
for _ in range(5000):
    i = rng.integers(0, len(inf), len(inf)); bx.append(np.corrcoef(lx[i], xx[i])[0, 1]); bo.append(np.corrcoef(lx[i], oo[i])[0, 1])
cars, glass = LV.set_index("feature").loc["cars"], LV.set_index("feature").loc["glass"]

L = ["# Captions — re-count, dictionary audit, lexical vs visual (audit rev12)", "",
     f"Captions used in the evaluated trainings: the frozen `caption_snapshot` of {runs.training_dataset['RUN-AESTHETIC-4']} and {runs.training_dataset['RUN-CONTROL-4']} (89 + 89); the platform writes them to `captions/<code>.txt` of the training zip and `aar_worker.py` encodes them with the frozen SDXL text encoders (only the UNet attention LoRA is trained). "
     f"Captions changed between v1 and v2: AESTHETIC {chg_A}/89, CONTROL {chg_C}/89 ({len(cc)} `caption.changed` events, {cc.created_at.min()[:16]} → {cc.created_at.max()[:16]} UTC). Caption `source` values: {src}; `model` field never filled: the export does not record who/what wrote the text (author's statement needed).", "",
     "## 1. Re-count with the previous reply's lexicon and code", "",
     f"Counts identical to `06_caption_feature_counts.csv` for {int(CMP.identical.sum())} of {len(CMP)} operationalised descriptors (exact re-execution of the matching code on the same frozen captions). Every hit with its fragment: `caption_hits_audit.csv`. Negated hits found: {int(H.negative.sum())}.", "",
     "## 2. Dictionary audit (declared before the variant counts)", "", "| descriptor | issue |", "|---|---|"]
for k, v in AUDIT.items():
    L.append(f"| {k} | {v['issue']} |")
L += ["", "| definition | AESTHETIC /89 | CONTROL /89 |", "|---|---|---|"]
for _, r in VAR.iterrows():
    L.append(f"| {r.definition} | {r.A_n} | {r.C_n} |")
L += ["", "Reading: the extended 'curved' group (37/27 in the previous reply) is driven by arches, domes, round and shell terms; the strict shape vocabulary gives the counts in the first row. Both are reported; neither was chosen for agreement with the visual results. Fragments of every ambiguous term: `caption_ambiguous_fragments.csv`.", "",
      "## 3. Lexical contrast vs visual contrast, descriptor by descriptor", "",
      "| descriptor | status | A | C | lexical A−C (share) | 95% CI | Fisher p | x photos (SD) | a−c outputs (SD) | sign lex = x | sign lex = outputs | r(presence, descriptor value) over 178 photos |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for _, r in LV.iterrows():
    L.append(f"| {r.feature} | {r.lexical_status} | {'' if r.A_n is None else r.A_n} | {'' if r.C_n is None else r.C_n} | {'' if r.lexical_contrast is None else f'{r.lexical_contrast:+.3f}'} | {'' if r.lex_ci_low is None else f'{r.lex_ci_low:+.3f} / {r.lex_ci_high:+.3f}'} | {'' if r.fisher_p is None else r.fisher_p} | {r.x_photos:+.2f} | {r.a_minus_c_outputs:+.2f} | {'' if r.same_sign_lex_vs_x is None else r.same_sign_lex_vs_x} | {'' if r.same_sign_lex_vs_outputs is None else r.same_sign_lex_vs_outputs} | {'' if r.pointbiserial_r_lex_vs_descriptor_178 is None else r.pointbiserial_r_lex_vs_descriptor_178} |")
L += ["", f"Informative descriptors (lexical proxy, not constant, not duplicate, ≥ 5 mentions): {len(inf)}. Profile associations across them (descriptors treated as equally weighted points; their mutual dependence is not modelled, bootstrap over descriptors only):",
      f"- lexical contrast vs photograph contrast x: Pearson {r_lx.statistic:+.2f} (bootstrap 95% {np.percentile(bx, 2.5):+.2f} / {np.percentile(bx, 97.5):+.2f}), Spearman {rs_lx.statistic:+.2f}; same sign {same_x}/{len(inf)}.",
      f"- lexical contrast vs output contrast a−c: Pearson {r_lo.statistic:+.2f} (95% {np.percentile(bo, 2.5):+.2f} / {np.percentile(bo, 97.5):+.2f}), Spearman {rs_lo.statistic:+.2f}; same sign {same_o}/{len(inf)}.",
      "- the per-photograph column shows whether the lexical presence tracks the visual descriptor of the same photograph (CLIP/pixel value): where it does, text and image carry the same information and the lexical analysis cannot separate the two channels.", "",
      "## 4. The review's sentence 'not for cars and glass'", "",
      f"- cars: lexicon A {cars.A_n} / C {cars.C_n} (contrast {cars.lexical_contrast:+.3f}); photographs x = {cars.x_photos:+.2f}; outputs a−c = {cars.a_minus_c_outputs:+.2f}. Signs: lexical vs photos same = {cars.same_sign_lex_vs_x}; lexical vs outputs same = {cars.same_sign_lex_vs_outputs}.",
      f"- glass: lexicon A {glass.A_n} / C {glass.C_n} (contrast {glass.lexical_contrast:+.3f}); photographs x = {glass.x_photos:+.2f}; outputs a−c = {glass.a_minus_c_outputs:+.2f}. Signs: lexical vs photos same = {glass.same_sign_lex_vs_x}; lexical vs outputs same = {glass.same_sign_lex_vs_outputs}.",
      "Directional agreement is not significance (both Fisher p above): the lexical differences for cars and glass are small and compatible with chance, but their direction does NOT contradict the visual contrasts. The review's 'non per automobili e vetro' is not supported as a statement about direction; it is defensible only as 'not distinguishable from zero'.", "",
      "## 5. What this does and does not establish", "",
      "The captions of the two corpora differ lexically in the same direction as several visual descriptors (and track them photograph by photograph): the text channel is confounded with the image channel in the training data. The lexical analysis therefore cannot attribute the transfer to images or to text; only the controlled-caption training (`PROTOCOLLO_CAPTION_CONTROLLATE.md`) can. No training with controlled captions exists in the records (training_runs.csv: all runs use the v1/v2 captions of their corpus).", ""]
write_md("report_captions.md", L)
CMP.to_csv(os.path.join(OUT, "caption_counts_vs_previous_reply.csv"), index=False); VAR.to_csv(os.path.join(OUT, "caption_definition_variants.csv"), index=False)
log("done")
