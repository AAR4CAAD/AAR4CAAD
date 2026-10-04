"""
Audit step 4 — the 31 descriptors (prompt sections 2, 4B and 6).

Reproduction: x (photographs A−C), a (A−BASE), c (C−BASE), r(x,a−c)=+0.71, r(x,a)=−0.01, r(x,c)=−0.43, sign counts, the
0.21/0.07 "shared/specific" components and the identity r(x,(a−c)/2) = r(x,a−c).
New: covariance decomposition Cov(x,a−c)=Cov(x,a)−Cov(x,c) with uncertainty (bootstrap over prompts for a,c; over descriptors
for the profile statistics); photograph contrasts by CONTROL stratum (type+style 20, type 41, random 28) — stratum-weighted,
NOT pairs; distances of BASE and adapters to the two photograph profiles in the standardised descriptor space.

Writes outputs/descriptors_profile.csv, outputs/descriptors_by_stratum.csv, outputs/descriptors_distances.csv, outputs/report_descriptors.md.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

from common import ANALYSIS, CONTENT, DESCRIPTORS, EXPORT_REP_ZIP, FRAMING, OUT, PHOTO, REPLICATION_EXCLUDED, SEED, Export, Log, as_bool, descriptor_matrix, write_md

log = Log("a04_descriptors")
rng = np.random.default_rng(SEED)
N_BOOT = 5000
E = Export(); ER = Export(EXPORT_REP_ZIP)
cov = pd.read_csv(os.path.join(ANALYSIS, "metrics", "covariates_images.csv")).set_index("id")
SI = E.csv("source_images.csv"); photos = list(SI.image_code)
runs = E.csv("training_runs.csv").set_index("code")
A_ds = E.csv("aesthetic_dataset.csv"); C_ds = E.csv("control_dataset.csv")
aes = list(A_ds[A_ds.dataset_code == runs.training_dataset["RUN-AESTHETIC-4"]].sort_values("sort_order").image_code)
ctl = list(C_ds[C_ds.dataset_code == runs.training_dataset["RUN-CONTROL-4"]].sort_values("sort_order").image_code)
cols = DESCRIPTORS

# standardisation on the 600 photographs (historical)
Zraw = descriptor_matrix(cov, photos); mu, sd = Zraw.mean(), Zraw.std().replace(0, 1)
Zp = ((Zraw - mu) / sd)[cols]
Zp.index = photos
x = Zp.loc[aes].mean() - Zp.loc[ctl].mean()

G = E.csv("generated_images.csv"); G["o"] = G.opaque_id.str.replace("-", "").str.lower(); G["cell"] = G.prompt_code + "_" + G.seed.astype(str)
GR = ER.csv("generated_images.csv"); GR["o"] = GR.opaque_id.str.replace("-", "").str.lower(); GR["cell"] = GR.prompt_code + "_" + GR.seed.astype(str)
runsR = ER.csv("training_runs.csv").set_index("code")
G = G[G.generation_plan_id.isin(G[G.training_run.isin(["RUN-AESTHETIC-4", "RUN-CONTROL-4"])].generation_plan_id)]  # main plans only
cells = sorted(G.cell.unique()); prompt_of = np.array([c.rsplit("_", 1)[0] for c in cells]); shown = np.array([c in set(G[(G.condition_code == "BASE") & ~as_bool(G.excluded_by_review_rule)].cell) for c in cells])


def Z(cond, run=None, GG=G):
    s = GG[GG.condition_code == cond] if run is None else GG[GG.training_run == run]
    o = s.drop_duplicates("cell").set_index("cell").o.reindex(cells); assert o.notna().all()
    return ((descriptor_matrix(cov, o.to_numpy()) - mu) / sd)[cols].to_numpy()


ZB = Z("BASE"); adapters = {("AESTHETIC", 1254): Z("AESTHETIC", "RUN-AESTHETIC-4"), ("CONTROL", 9865): Z("CONTROL", "RUN-CONTROL-4")}
for code in sorted(r for r in GR.training_run.dropna().unique() if r.startswith("REP-") and r not in REPLICATION_EXCLUDED):
    corpus = "AESTHETIC" if str(runsR.training_dataset[code]).startswith("AESTHETIC") else "CONTROL"
    adapters[(corpus, int(runsR.seed[code]))] = Z(corpus, code, GR)
seeds = sorted({s for _, s in adapters})
dA = {s: adapters[("AESTHETIC", s)] - ZB for s in seeds}; dC = {s: adapters[("CONTROL", s)] - ZB for s in seeds}
a_cells = np.mean([dA[s] for s in seeds], 0); c_cells = np.mean([dC[s] for s in seeds], 0)   # cells × 31, mean over seeds
a, c = a_cells.mean(0), c_cells.mean(0); ac = a - c
xv = x.to_numpy()
rows = []


def rep(section, quantity, reported, value, lo=None, hi=None, n=None, note=""):
    rows.append(dict(section=section, quantity=quantity, reported=reported, recomputed=value, ci_low=lo, ci_high=hi, n=n, note=note))
    log(f"[{section}] {quantity}: reported {reported} | recomputed {value} | CI {lo} {hi} {note}")


def r_boot_desc(y):
    r = np.corrcoef(xv, y)[0, 1]; b = []
    for _ in range(N_BOOT):
        i = rng.integers(0, 31, 31); b.append(np.corrcoef(xv[i], y[i])[0, 1])
    return float(r), float(np.nanpercentile(b, 2.5)), float(np.nanpercentile(b, 97.5))


qs = np.unique(prompt_of); W = np.array([(prompt_of == q).sum() for q in qs])
def prompt_boot_profiles(B=N_BOOT):
    """Resample prompts; return B × 31 profiles of a and c."""
    ma = np.stack([a_cells[prompt_of == q].mean(0) for q in qs]); mc = np.stack([c_cells[prompt_of == q].mean(0) for q in qs])
    i = rng.integers(0, len(qs), (B, len(qs))); w = W[i][:, :, None]
    return (ma[i] * w).sum(1) / w.sum(1), (mc[i] * w).sum(1) / w.sum(1)


r_ac, lo, hi = r_boot_desc(ac); rep("profile", "r(x, a−c)", 0.71, round(r_ac, 3), round(lo, 3), round(hi, 3), 31, "bootstrap over the 31 descriptors (as in the historical figure)")
r_a, lo, hi = r_boot_desc(a); rep("profile", "r(x, a)", -0.01, round(r_a, 3), round(lo, 3), round(hi, 3))
r_c, lo, hi = r_boot_desc(c); rep("profile", "r(x, c)", -0.43, round(r_c, 3), round(lo, 3), round(hi, 3))
rep("profile", "same sign as x: a−c / a / c", "27 / 14 / 13", f"{int((np.sign(ac) == np.sign(xv)).sum())} / {int((np.sign(a) == np.sign(xv)).sum())} / {int((np.sign(c) == np.sign(xv)).sum())}")
rep("profile", "a and c same sign / r(a,c)", "26 / +0.82", f"{int((np.sign(a) == np.sign(c)).sum())} / {np.corrcoef(a, c)[0, 1]:+.2f}")
m_, h_ = (a + c) / 2, (a - c) / 2
rep("profile", "'shared component' 0.21 SD: definition = mean |(a+c)/2|; 'specific' 0.07 = mean |(a−c)/2|", "0.21 / 0.07", f"{np.abs(m_).mean():.3f} / {np.abs(h_).mean():.3f}", note="mean absolute value over the 31 descriptors of the signed cell-mean differences; r(x,m) and r(x,h) below")
rep("profile", "r(x, (a+c)/2) / r(x, (a−c)/2)", "-0.23 / +0.71", f"{np.corrcoef(xv, m_)[0, 1]:+.3f} / {np.corrcoef(xv, h_)[0, 1]:+.3f}", note="r(x,(a−c)/2) = r(x,a−c) EXACTLY: a positive constant does not change a correlation. It is an identity, not independent evidence")
rep("profile", "mean |x| / |a−c| / |a| / |c|", "0.22 / 0.14 / 0.21 / 0.21", f"{np.abs(xv).mean():.2f} / {np.abs(ac).mean():.2f} / {np.abs(a).mean():.2f} / {np.abs(c).mean():.2f}")
# prompt-bootstrap of the profile correlations (uncertainty of a, c given the 31 descriptors)
ba, bc = prompt_boot_profiles()
rb = lambda Y: (float(np.percentile([np.corrcoef(xv, y)[0, 1] for y in Y], 2.5)), float(np.percentile([np.corrcoef(xv, y)[0, 1] for y in Y], 97.5)))
rep("profile", "r(x,a−c): prompt-bootstrap 95%", None, round(r_ac, 3), *[round(v, 3) for v in rb(ba - bc)], note="uncertainty from the prompts, descriptors fixed")
rep("profile", "r(x,a): prompt-bootstrap 95%", None, round(r_a, 3), *[round(v, 3) for v in rb(ba)])
rep("profile", "r(x,c): prompt-bootstrap 95%", None, round(r_c, 3), *[round(v, 3) for v in rb(bc)])

# ---------------------------------------------------------------- covariance decomposition
covf = lambda y: float(np.cov(xv, y, ddof=1)[0, 1])
Cac, Ca, Cc = covf(ac), covf(a), covf(c)
rep("covariance", "Cov(x,a−c) = Cov(x,a) − Cov(x,c)", f"{Cac:.5f}", f"{Ca:.5f} − ({Cc:.5f}) = {Ca - Cc:.5f}", note=f"identity error {abs(Cac - (Ca - Cc)):.1e}")
share_c = -Cc / Cac if Cac != 0 else np.nan
bsh = []
for ya, yc in zip(ba, bc):
    d_ = covf(ya - yc); bsh.append(np.nan if abs(d_) < 1e-9 else -covf(yc) / d_)
bsh2 = []
for _ in range(N_BOOT):
    i = rng.integers(0, 31, 31); d_ = np.cov(xv[i], ac[i], ddof=1)[0, 1]; bsh2.append(np.nan if abs(d_) < 1e-9 else -np.cov(xv[i], c[i], ddof=1)[0, 1] / d_)
rep("covariance", "share of Cov(x,a−c) carried by −Cov(x,c) (the CONTROL term)", None, round(share_c, 3), round(float(np.nanpercentile(bsh, 2.5)), 3), round(float(np.nanpercentile(bsh, 97.5)), 3),
    note=f"prompt bootstrap; descriptor bootstrap {np.nanpercentile(bsh2, 2.5):.2f}–{np.nanpercentile(bsh2, 97.5):.2f}. Shares are ratios of covariances with uncertain denominators: read as 'most of the covariance comes from CONTROL moving against x', not as an exact percentage")
rep("covariance", "share carried by Cov(x,a) (the AESTHETIC term)", None, round(1 - share_c, 3), note="= 1 − the previous row; point estimate near zero or slightly negative because r(x,a) ≈ −0.01")
sl = lambda y: float(np.polyfit(xv, y, 1)[0])
rep("covariance", "slopes of a−c, a, c on x (SD per SD)", None, f"{sl(ac):+.3f} / {sl(a):+.3f} / {sl(c):+.3f}")

# ---------------------------------------------------------------- the review's sentence 'not for cars and glass'
for f in ["curved_organic", "concrete", "low_angle", "cars", "glass", "iconic_design", "contemporary", "monumental", "interior"]:
    j = cols.index(f)
    rep("descriptor signs", f"{f}: x (photos) / a−c / a / c", None, f"{xv[j]:+.2f} / {ac[j]:+.2f} / {a[j]:+.2f} / {c[j]:+.2f}", note="same direction photos→outputs" if np.sign(xv[j]) == np.sign(ac[j]) else "OPPOSITE direction")

# ---------------------------------------------------------------- photograph contrasts by CONTROL stratum (stratum-weighted; no pairs exist)
CC = pd.read_csv(os.path.join(OUT, "control_construction.csv"))
def stratum_contrast(st):
    cc = CC[CC.stratum == st]
    if st == "random_fill":
        return Zp.loc[aes].mean() - Zp.loc[cc.control_image].mean(), len(cc), 89, "all 89 AESTHETIC vs the 28 random CONTROL (unpaired; no counterpart stratum exists)"
    rows_ = []
    for k, grp in cc.groupby("stratum_key"):
        mates = grp.aesthetic_in_same_stratum.iloc[0].split(";")
        rows_.append(Zp.loc[mates].mean() - Zp.loc[grp.control_image].mean())      # one contrast per stratum (A mates mean − C members mean)
    T_ = pd.DataFrame(rows_); n_a = len({m for s_ in cc.aesthetic_in_same_stratum for m in s_.split(";")})
    return T_.mean(), len(cc), n_a, f"{len(rows_)} strata, each weighted equally: mean over strata of (mean of the AESTHETIC photographs of the stratum − mean of its CONTROL photographs)"


strat_rows = []; xs_ = {}
for st in ["type_and_style", "type_only", "random_fill"]:
    xk, nc_, na_, how = stratum_contrast(st); xs_[st] = xk.to_numpy()
    xm61 = None
    r1, l1, h1 = r_boot_desc(xk.to_numpy()[np.argsort(cols)] if False else xk.reindex(cols).to_numpy())
    for lab, y in (("a−c", ac), ("a", a), ("c", c)):
        r_, lo_, hi_ = r_boot_desc(y) if False else (np.corrcoef(xk.reindex(cols).to_numpy(), y)[0, 1], None, None)
        strat_rows.append(dict(stratum=st, n_control=nc_, n_aesthetic=na_, how=how, output_contrast=lab, r_with_x_stratum=round(float(r_), 3), same_sign=int((np.sign(xk.reindex(cols).to_numpy()) == np.sign(y)).sum()), r_x_stratum_vs_x_full=round(float(np.corrcoef(xk.reindex(cols).to_numpy(), xv)[0, 1]), 3), mean_abs_x_stratum=round(float(np.abs(xk).mean()), 3)))
    log(f"[stratum] {st}: n_C {nc_}, n_A {na_}; r(x_stratum, x_full) {np.corrcoef(xk.reindex(cols).to_numpy(), xv)[0, 1]:+.3f}; r with a−c {np.corrcoef(xk.reindex(cols).to_numpy(), ac)[0, 1]:+.3f}, a {np.corrcoef(xk.reindex(cols).to_numpy(), a)[0, 1]:+.3f}, c {np.corrcoef(xk.reindex(cols).to_numpy(), c)[0, 1]:+.3f}")
# matched 61 together (20 + 41)
cc61 = CC[CC.stratum != "random_fill"]; rows61 = []
for k, grp in cc61.groupby(["stratum", "stratum_key"]):
    mates = grp.aesthetic_in_same_stratum.iloc[0].split(";"); rows61.append(Zp.loc[mates].mean() - Zp.loc[grp.control_image].mean())
x61 = pd.DataFrame(rows61).mean().reindex(cols).to_numpy(); xs_["matched_61"] = x61
for lab, y in (("a−c", ac), ("a", a), ("c", c)):
    strat_rows.append(dict(stratum="matched_61 (20 type+style + 41 type)", n_control=61, n_aesthetic=len({m for s_ in cc61.aesthetic_in_same_stratum for m in s_.split(";")}), how=f"{len(rows61)} strata weighted equally", output_contrast=lab, r_with_x_stratum=round(float(np.corrcoef(x61, y)[0, 1]), 3), same_sign=int((np.sign(x61) == np.sign(y)).sum()), r_x_stratum_vs_x_full=round(float(np.corrcoef(x61, xv)[0, 1]), 3), mean_abs_x_stratum=round(float(np.abs(x61).mean()), 3)))
log(f"[stratum] matched_61: r(x61, x_full) {np.corrcoef(x61, xv)[0, 1]:+.3f}; r with a−c {np.corrcoef(x61, ac)[0, 1]:+.3f}, a {np.corrcoef(x61, a)[0, 1]:+.3f}, c {np.corrcoef(x61, c)[0, 1]:+.3f}")
ST = pd.DataFrame(strat_rows); ST.to_csv(os.path.join(OUT, "descriptors_by_stratum.csv"), index=False)
# per-descriptor table of the stratum contrasts
PD = pd.DataFrame({"feature": cols, "block": [("photography" if f in PHOTO else "framing and scene" if f in FRAMING else "architectural content (CLIP)") for f in cols], "x_all_89_vs_89": xv, "x_type_and_style_20": xs_["type_and_style"], "x_type_only_41": xs_["type_only"], "x_matched_61": x61, "x_random_28_vs_all_A": xs_["random_fill"],
                   "a_minus_c": ac, "a_minus_BASE": a, "c_minus_BASE": c})
PD.to_csv(os.path.join(OUT, "descriptors_profile.csv"), index=False)

# ---------------------------------------------------------------- distances to the photograph profiles in descriptor space
pA, pC = Zp.loc[aes].mean().to_numpy(), Zp.loc[ctl].mean().to_numpy()
dist_rows, chg = [], []
def dstats(M, name, seed):
    out = {}
    for tgt, cen in (("AESTHETIC photographs", pA), ("CONTROL photographs", pC)):
        per = np.linalg.norm(M - cen, axis=1); dist_rows.append(dict(adapter=name, training_seed=seed, target=tgt, centroid_to_centroid=float(np.linalg.norm(M.mean(0) - cen)), mean_image_to_centroid=float(per.mean()))); out[tgt] = per
    return out
dB = dstats(ZB, "BASE", 0)
def boot_prompts(v):
    means = np.array([v[prompt_of == q].mean() for q in qs]); i = rng.integers(0, len(qs), (N_BOOT, len(qs))); b = (means[i] * W[i]).sum(1) / W[i].sum(1)
    return float(v.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5)), float(2 * min((b <= 0).mean(), (b >= 0).mean()))
for k in sorted(adapters):
    dk = dstats(adapters[k], k[0], k[1])
    for tgt in ("AESTHETIC photographs", "CONTROL photographs"):
        m, lo, hi, p = boot_prompts(dk[tgt] - dB[tgt]); chg.append(dict(adapter=k[0], training_seed=k[1], target=tgt, mean_change_vs_BASE=m, ci_low=lo, ci_high=hi, p_boot=p))
        log(f"[desc distances] {k} → {tgt}: Δ {m:+.3f} ({lo:+.3f}/{hi:+.3f}) p {p}")
    own, oth = ("AESTHETIC photographs", "CONTROL photographs") if k[0] == "AESTHETIC" else ("CONTROL photographs", "AESTHETIC photographs")
    m, lo, hi, p = boot_prompts((dk[own] - dB[own]) - (dk[oth] - dB[oth])); chg.append(dict(adapter=k[0], training_seed=k[1], target="own minus other corpus", mean_change_vs_BASE=m, ci_low=lo, ci_high=hi, p_boot=p))
    log(f"[desc distances] {k}: own − other {m:+.3f} ({lo:+.3f}/{hi:+.3f})")
def centroid_change(X, cen):
    i = rng.integers(0, len(qs), (N_BOOT, len(qs))); idx = [np.where(prompt_of == q)[0] for q in qs]
    est = float(np.linalg.norm(X.mean(0) - cen) - np.linalg.norm(ZB.mean(0) - cen)); b = []
    for row in i:
        sel = np.concatenate([idx[j] for j in row]); b.append(np.linalg.norm(X[sel].mean(0) - cen) - np.linalg.norm(ZB[sel].mean(0) - cen))
    b = np.array(b); return est, float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5)), float(2 * min((b <= 0).mean(), (b >= 0).mean()))
cchg = []
for k in sorted(adapters):
    for tgt, cen in (("AESTHETIC photographs", pA), ("CONTROL photographs", pC)):
        m, lo, hi, p = centroid_change(adapters[k], cen); cchg.append(dict(adapter=k[0], training_seed=k[1], target=tgt, metric="centroid_to_centroid", change_vs_BASE=m, ci_low=lo, ci_high=hi, p_boot=p))
        log(f"[desc centroid distances] {k} → {tgt}: Δ {m:+.3f} ({lo:+.3f}/{hi:+.3f}) p {p}")
pd.DataFrame(dist_rows).to_csv(os.path.join(OUT, "descriptors_distances.csv"), index=False)
pd.DataFrame(chg).to_csv(os.path.join(OUT, "descriptors_distance_changes.csv"), index=False)
pd.DataFrame(cchg).to_csv(os.path.join(OUT, "descriptors_centroid_distance_changes.csv"), index=False)
# redundancy among descriptors
Cm = np.corrcoef(Zp.to_numpy().T); off = Cm[np.triu_indices(31, 1)]
ev = np.linalg.eigvalsh(Cm)[::-1]; n_eff = (ev.sum() ** 2) / (ev ** 2).sum()
rep("redundancy", "descriptor correlations on the 600 photographs: mean |r| / max |r| / effective number of descriptors", None, f"{np.abs(off).mean():.2f} / {np.abs(off).max():.2f} / {n_eff:.1f}", note="effective number = (Σλ)²/Σλ²; the 31 descriptors are not independent, the profile r treats them as 31 equally weighted points")
pd.DataFrame(rows).to_csv(os.path.join(OUT, "descriptors_reproduction.csv"), index=False)

L = ["# The 31 descriptors — reproduction, covariance decomposition, strata, distances (audit rev12)", "",
     "Standardisation: every descriptor (CLIP attributes as logits) centred and scaled on the 600 photographs. x = mean(A photos) − mean(C photos); a, c = per-cell differences of the generated images from BASE (same prompt and seed), mean of the three paired training seeds, mean over the 192 cells.", "",
     "## Reproduction and definitions", "", "| section | quantity | reported | recomputed | 95% CI | note |", "|---|---|---|---|---|---|"]
for r in rows:
    ci = "" if r["ci_low"] is None else f"{r['ci_low']} / {r['ci_high']}"
    L.append(f"| {r['section']} | {r['quantity']} | {'' if r['reported'] is None else r['reported']} | {r['recomputed']} | {ci} | {r['note']} |")
L += ["", "## Photograph contrasts by CONTROL stratum (no pairs exist: stratum-weighted contrasts)", "",
      "| stratum | n CONTROL | n AESTHETIC involved | construction | r(x_stratum, x_full) | r with a−c | r with a | r with c | same sign with a−c |", "|---|---|---|---|---|---|---|---|---|"]
for st, grp in ST.groupby("stratum", sort=False):
    g_ = grp.set_index("output_contrast")
    L.append(f"| {st} | {g_.n_control.iloc[0]} | {g_.n_aesthetic.iloc[0]} | {g_.how.iloc[0]} | {g_.r_x_stratum_vs_x_full.iloc[0]:+.3f} | {g_.loc['a−c', 'r_with_x_stratum']:+.3f} | {g_.loc['a', 'r_with_x_stratum']:+.3f} | {g_.loc['c', 'r_with_x_stratum']:+.3f} | {g_.loc['a−c', 'same_sign']} |")
L += ["", "Per-descriptor values in `descriptors_profile.csv`. The random-fill contrast has no counterpart set and is reported as 'all AESTHETIC vs the 28 random CONTROL'. None of these contrasts estimates what adapters trained on the sub-groups would do.", "",
      "## Distances to the photograph profiles (descriptor space, 31 standardised dimensions)", "", "| adapter | seed | target | centroid→centroid | mean image→centroid |", "|---|---|---|---|---|"]
for r in dist_rows:
    L.append(f"| {r['adapter']} | {r['training_seed']} | {r['target']} | {r['centroid_to_centroid']:.3f} | {r['mean_image_to_centroid']:.3f} |")
L += ["", "| adapter | seed | target | Δ mean image→centroid vs BASE | 95% CI (prompts) | p |", "|---|---|---|---|---|---|"]
for r in chg:
    L.append(f"| {r['adapter']} | {r['training_seed']} | {r['target']} | {r['mean_change_vs_BASE']:+.3f} | {r['ci_low']:+.3f} / {r['ci_high']:+.3f} | {r['p_boot']:.4f} |")
L += ["", "| adapter | seed | target | Δ centroid→centroid vs BASE | 95% CI (prompts) | p |", "|---|---|---|---|---|---|"]
for r in cchg:
    L.append(f"| {r['adapter']} | {r['training_seed']} | {r['target']} | {r['change_vs_BASE']:+.3f} | {r['ci_low']:+.3f} / {r['ci_high']:+.3f} | {r['p_boot']:.4f} |")
L += ["", "Negative = closer than BASE. Two metrics, two questions: the mean position of the adapter's images (centroid→centroid) can move toward a profile while the mean distance of the individual images does not change (spread). Report both; the correlation r(x,a) ≈ 0 is neither test.", ""]
write_md("report_descriptors.md", L)
log("done")
