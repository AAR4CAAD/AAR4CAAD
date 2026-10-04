"""
Integration step 1 — DINOv2 direction adjusted for period + area + building type + style (SPEC_dino_aggiustamento_completo.json).

Two geometries, never mixed:
  G1 — outputs (original embeddings) projected on the adjusted photograph direction (as in the audit's previous adjustment).
  G2 — common linear transformation T = I − Π (Π = projector on the row space of the covariate coefficient matrix), estimated on
       the photographs, applied identically to photographs and outputs: direction, projections, R and distances all in T-space.
Writes integrazione/dino_aggiustamento_completo.csv and integrazione/report_dino_aggiustamento_completo.md.
"""
import json
import os

import numpy as np
import pandas as pd

from common import ANALYSIS, AUDIT, EXPORT_REP_ZIP, REPLICATION_EXCLUDED, Export, Log, as_bool

OUTI = os.path.join(AUDIT, "integrazione"); os.makedirs(OUTI, exist_ok=True)
log = Log("b01_dino_adjust_full")
SEED, N_BOOT, N_DIR = 20261004, 5000, 1000
rng = np.random.default_rng(SEED)
E = Export(); ER = Export(EXPORT_REP_ZIP)
unit = lambda x: x / np.linalg.norm(x, axis=-1, keepdims=True)

z = np.load(os.path.join(ANALYSIS, "metrics", "embeddings_dinov2_vitb14.npz"), allow_pickle=False)
zr = np.load(os.path.join(ANALYSIS, "metrics", "embeddings_replication_dinov2_vitb14.npz"), allow_pickle=False)
emb = {i: v for i, v in zip(np.concatenate([z["id"], zr["id"]]), unit(np.concatenate([z["cls"], zr["cls"]]).astype(np.float64)))}
D = np.load(os.path.join(ANALYSIS, "baseline", "direction_dinov2.npz"), allow_pickle=False)
aes, ctl = list(D["aesthetic_codes"]), list(D["control_codes"])
SI = E.csv("source_images.csv"); photos = list(SI.image_code)
XP = np.stack([emb[c] for c in photos]); isA = np.array([c in set(aes) for c in photos]); isC = np.array([c in set(ctl) for c in photos])
M = E.csv("image_metadata.csv").set_index("image_code").reindex(photos)
norm = lambda s: s.fillna("∅").astype(str).str.strip().str.lower()
period = M.period.replace({"pre-1919": "1919-1945"}); area = M.continent
def pooled(col, name, min_n=3):
    v = norm(col); vc = v.value_counts(); keep = set(vc[vc >= min_n].index)
    out = v.where(v.isin(keep), f"rare {name}")
    log(f"{name}: {v.nunique()} distinct, {int((vc == 1).sum())} singletons, {len(keep)} categories with >= {min_n} ({int(vc[vc >= min_n].sum())} photographs), pooled {int((~v.isin(keep)).sum())}")
    return out
btype = pooled(M.building_type, "type"); style = pooled(M.architectural_style, "style")

G = E.csv("generated_images.csv"); G["o"] = G.opaque_id.str.replace("-", "").str.lower(); G["cell"] = G.prompt_code + "_" + G.seed.astype(str)
G = G[G.generation_plan_id.isin(G[G.training_run.isin(["RUN-AESTHETIC-4", "RUN-CONTROL-4"])].generation_plan_id)]
GR = ER.csv("generated_images.csv"); GR["o"] = GR.opaque_id.str.replace("-", "").str.lower(); GR["cell"] = GR.prompt_code + "_" + GR.seed.astype(str)
runsR = ER.csv("training_runs.csv").set_index("code")
cells = sorted(G.cell.unique()); prompt_of = np.array([c.rsplit("_", 1)[0] for c in cells]); qs = np.unique(prompt_of); W = np.array([(prompt_of == q).sum() for q in qs])
def mat(cond=None, run=None, GG=G):
    s = GG[GG.condition_code == cond] if run is None else GG[GG.training_run == run]
    o = s.drop_duplicates("cell").set_index("cell").o.reindex(cells); assert o.notna().all()
    return np.stack([emb[i] for i in o])
EB = mat("BASE"); AD = {("AESTHETIC", 1254): mat(run="RUN-AESTHETIC-4"), ("CONTROL", 9865): mat(run="RUN-CONTROL-4")}
for code in sorted(r for r in GR.training_run.dropna().unique() if r.startswith("REP-") and r not in REPLICATION_EXCLUDED):
    AD[("AESTHETIC" if str(runsR.training_dataset[code]).startswith("AESTHETIC") else "CONTROL", int(runsR.seed[code]))] = mat(run=code, GG=GR)
seeds = sorted({s for _, s in AD})

def boot(v):
    means = np.array([v[prompt_of == q].mean() for q in qs]); i = rng.integers(0, len(qs), (N_BOOT, len(qs))); b = (means[i] * W[i]).sum(1) / W[i].sum(1)
    return float(v.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
def design(cols):
    X = pd.get_dummies(pd.DataFrame(cols), drop_first=True).astype(float); X.insert(0, "const", 1.0); return X.to_numpy()

rows = []
def add(direction, geometry, seed, quantity, est, lo=None, hi=None, denominator=None, note=""):
    rows.append(dict(direction=direction, geometry=geometry, training_seed=seed, quantity=quantity, estimate=est, ci_low=lo, ci_high=hi, n_cells=192, denominator=denominator, note=note))

def analyse(name, Xd):
    # ---- fit
    if Xd is None:
        B = np.zeros((0, 768)); res = XP; rank = 0; k = 0
    else:
        B, *_ = np.linalg.lstsq(Xd, XP, rcond=None); res = XP - Xd @ B; rank = int(np.linalg.matrix_rank(Xd)); k = Xd.shape[1]
    r2 = 0.0 if Xd is None else float(1 - ((res - res.mean(0)) ** 2).sum() / ((XP - XP.mean(0)) ** 2).sum())
    # ---- G1: adjusted direction, original outputs projected
    g1 = res[isA].mean(0) - res[isC].mean(0); d1 = float(np.linalg.norm(g1)); u1 = g1 / d1
    cos1 = float(u1 @ D["cls_v"])
    add(name, "G1 projection on adjusted direction", "-", "d_adj (norm of the adjusted photograph contrast)", d1, note=f"rank(X)={rank} of {k} columns; mean R2 of covariate model {r2:.3f}")
    add(name, "G1 projection on adjusted direction", "-", "cosine(u_adj, u_original)", cos1)
    # ---- G2: common transformation
    if Xd is None:
        T = lambda e: e; dim_removed = 0; var_removed = 0.0
    else:
        Bc = B[1:]  # directions associated with the dummies (the intercept shifts nothing)
        Q, _ = np.linalg.qr(Bc.T); Q = Q[:, :np.linalg.matrix_rank(Bc)]
        T = lambda e: e - (e @ Q) @ Q.T; dim_removed = Q.shape[1]
        var_removed = float((((XP - XP.mean(0)) @ Q) ** 2).sum() / ((XP - XP.mean(0)) ** 2).sum())
    XT = T(XP); g2 = XT[isA].mean(0) - XT[isC].mean(0); d2 = float(np.linalg.norm(g2)); u2 = g2 / d2
    add(name, "G2 common transformation", "-", "d_T (norm of the photograph contrast after T)", d2, note=f"directions removed {dim_removed} of 768; share of photograph variance removed {var_removed:.3f}")
    add(name, "G2 common transformation", "-", "cosine(u_T, u_original)", float(u2 @ D["cls_v"]))
    EBT = T(EB); ADT = {k_: T(v) for k_, v in AD.items()}
    cA1, cC1 = XP[isA].mean(0), XP[isC].mean(0); cA2, cC2 = XT[isA].mean(0), XT[isC].mean(0)
    pooledP1, pooledP2 = [], []
    for s in seeds:
        A_, C_ = AD[("AESTHETIC", s)], AD[("CONTROL", s)]; AT_, CT_ = ADT[("AESTHETIC", s)], ADT[("CONTROL", s)]
        for geo, (a_, c_, b_, u_, d_) in (("G1 projection on adjusted direction", (A_, C_, EB, u1, d1)), ("G2 common transformation", (AT_, CT_, EBT, u2, d2))):
            for lab, Y in (("P A−C", a_ - c_), ("P A−BASE", a_ - b_), ("P C−BASE", c_ - b_)):
                m, lo, hi = boot(Y @ u_); add(name, geo, s, lab, m, lo, hi, denominator=d_, note="IC conditional on the estimated direction (prompt bootstrap)")
                if lab == "P A−C":
                    add(name, geo, s, "R = mean P(A−C) / d", m / d_, lo / d_, hi / d_, denominator=d_, note="denominator fixed within the bootstrap")
                    (pooledP1 if geo.startswith("G1") else pooledP2).append(Y @ u_)
        # ---- distances in G2 only
        dBA, dBC = np.linalg.norm(EBT - cA2, axis=1), np.linalg.norm(EBT - cC2, axis=1)
        for corpus, X_ in (("AESTHETIC", AT_), ("CONTROL", CT_)):
            dA_, dC_ = np.linalg.norm(X_ - cA2, axis=1), np.linalg.norm(X_ - cC2, axis=1)
            own, oth = (dA_ - dBA, dC_ - dBC) if corpus == "AESTHETIC" else (dC_ - dBC, dA_ - dBA)
            for lab, v in (("ΔD mean per-image distance to OWN corpus centroid (vs BASE)", own), ("ΔD mean per-image distance to OTHER corpus centroid (vs BASE)", oth), ("ΔD own − other (per-image)", own - oth)):
                m, lo, hi = boot(v); add(name, "G2 common transformation", s, f"{corpus}: {lab}", m, lo, hi, note="negative = closer than BASE")
            # centroid-to-centroid with prompt bootstrap
            for tgt, cen in (("OWN", cA2 if corpus == "AESTHETIC" else cC2), ("OTHER", cC2 if corpus == "AESTHETIC" else cA2)):
                est = float(np.linalg.norm(X_.mean(0) - cen) - np.linalg.norm(EBT.mean(0) - cen)); b = []
                idx = [np.where(prompt_of == q)[0] for q in qs]
                for row in rng.integers(0, len(qs), (N_BOOT, len(qs))):
                    sel = np.concatenate([idx[j] for j in row]); b.append(np.linalg.norm(X_[sel].mean(0) - cen) - np.linalg.norm(EBT[sel].mean(0) - cen))
                add(name, "G2 common transformation", s, f"{corpus}: ΔD centroid-to-centroid to {tgt} corpus (vs BASE)", est, float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5)))
    for geo, P_, d_ in (("G1 projection on adjusted direction", pooledP1, d1), ("G2 common transformation", pooledP2, d2)):
        pm = np.mean(P_, 0); m, lo, hi = boot(pm)
        add(name, geo, "mean of the three seeds (descriptive)", "P A−C", m, lo, hi, denominator=d_); add(name, geo, "mean of the three seeds (descriptive)", "R", m / d_, lo / d_, hi / d_, denominator=d_)
    # ---- denominator stability: resample the two photograph sets, refit, recompute d1 and d2
    iA, iC, iO = np.where(isA)[0], np.where(isC)[0], np.where(~isA & ~isC)[0]; bd1, bd2 = [], []
    for _ in range(N_DIR):
        sel = np.concatenate([iA[rng.integers(0, 89, 89)], iC[rng.integers(0, 89, 89)], iO]); Xb = XP[sel]
        if Xd is None:
            rb = Xb; Tb = lambda e: e
        else:
            Xdb = Xd[sel]; Bb, *_ = np.linalg.lstsq(Xdb, Xb, rcond=None); rb = Xb - Xdb @ Bb
            Qb, _ = np.linalg.qr(Bb[1:].T); Qb = Qb[:, :np.linalg.matrix_rank(Bb[1:])]; Tb = lambda e, Qb=Qb: e - (e @ Qb) @ Qb.T
        bd1.append(np.linalg.norm(rb[:89].mean(0) - rb[89:178].mean(0))); Xt = Tb(Xb); bd2.append(np.linalg.norm(Xt[:89].mean(0) - Xt[89:178].mean(0)))
    add(name, "G1 projection on adjusted direction", "-", "d_adj under resampling of the two photograph sets: 2.5% / 97.5%", float(np.percentile(bd1, 2.5)), float(np.percentile(bd1, 2.5)), float(np.percentile(bd1, 97.5)), note="stability check of the denominator only (norm biased upwards); not a CI of R")
    add(name, "G2 common transformation", "-", "d_T under resampling of the two photograph sets: 2.5% / 97.5%", float(np.percentile(bd2, 2.5)), float(np.percentile(bd2, 2.5)), float(np.percentile(bd2, 97.5)), note="same")
    log(f"[{name}] G1: d {d1:.4f} cos {cos1:+.3f} | G2: d_T {d2:.4f} removed {dim_removed} dims ({var_removed:.1%} var) | pooled R G1 {np.mean(pooledP1) / d1:.3f}, G2 {np.mean(pooledP2) / d2:.3f}")

analyse("(i) original", None)
analyse("(ii) period + area", design({"period": period, "area": area}))
analyse("(iii) period + area + type + style", design({"period": period, "area": area, "type": btype, "style": style}))
R = pd.DataFrame(rows); R.to_csv(os.path.join(OUTI, "dino_aggiustamento_completo.csv"), index=False)

# ---- report
def pick(direction, geo, seed, q):
    r = R[(R.direction == direction) & (R.geometry.str.startswith(geo)) & (R.training_seed.astype(str) == str(seed)) & (R.quantity == q)]
    return r.iloc[0] if len(r) else None
f = lambda r: "n/a" if r is None else (f"{r.estimate:+.4f}" + (f" [{r.ci_low:+.4f}, {r.ci_high:+.4f}]" if pd.notna(r.ci_low) else ""))
L = ["# DINOv2: direction adjusted for period, area, building type and style — two geometries", "",
     "Specification fixed before the run: `SPEC_dino_aggiustamento_completo.json`. G1 = original outputs projected on the adjusted photograph direction (as in the audit). G2 = common linear transformation T = I − Π estimated on the photographs and applied identically to photographs and outputs; only in G2 are distances comparable. P, R and distances of the two geometries are never mixed. Intervals: bootstrap over the 48 prompts, conditional on the estimated direction. The mean of the three seeds is a descriptive summary of these six adapters.", "",
     "## Directions", "", "| direction | geometry | d | cos with original | note |", "|---|---|---|---|---|"]
for dname in R.direction.unique():
    for geo, dq, cq in (("G1", "d_adj (norm of the adjusted photograph contrast)", "cosine(u_adj, u_original)"), ("G2", "d_T (norm of the photograph contrast after T)", "cosine(u_T, u_original)")):
        rd, rc = pick(dname, geo, "-", dq), pick(dname, geo, "-", cq)
        L.append(f"| {dname} | {geo} | {rd.estimate:.4f} | {rc.estimate:+.3f} | {rd.note} |")
L += ["", "## Projections and R per training seed", "", "| direction | geometry | seed | P A−C | P A−BASE | P C−BASE | R |", "|---|---|---|---|---|---|---|"]
for dname in R.direction.unique():
    for geo in ("G1", "G2"):
        for s in list(seeds) + ["mean of the three seeds (descriptive)"]:
            pr = pick(dname, geo, s, "P A−C"); pa = pick(dname, geo, s, "P A−BASE"); pc = pick(dname, geo, s, "P C−BASE"); rr = pick(dname, geo, s, "R = mean P(A−C) / d"); rr = pick(dname, geo, s, "R") if rr is None else rr
            L.append(f"| {dname} | {geo} | {s} | {f(pr)} | {f(pa)} | {f(pc)} | {f(rr)} |")
L += ["", "## Distances in G2 (ΔD vs BASE; negative = closer)", "", "| direction | seed | adapter | own, per-image | other, per-image | own − other | own, centroid | other, centroid |", "|---|---|---|---|---|---|---|---|"]
for dname in R.direction.unique():
    for s in seeds:
        for corpus in ("AESTHETIC", "CONTROL"):
            g = lambda q: pick(dname, "G2", s, f"{corpus}: {q}")
            L.append(f"| {dname} | {s} | {corpus} | {f(g('ΔD mean per-image distance to OWN corpus centroid (vs BASE)'))} | {f(g('ΔD mean per-image distance to OTHER corpus centroid (vs BASE)'))} | {f(g('ΔD own − other (per-image)'))} | {f(g('ΔD centroid-to-centroid to OWN corpus (vs BASE)'))} | {f(g('ΔD centroid-to-centroid to OTHER corpus (vs BASE)'))} |")
L += ["", "## Denominator stability (resampling of the two photograph sets; not a CI of R)", "", "| direction | geometry | 2.5% | 97.5% |", "|---|---|---|---|"]
for dname in R.direction.unique():
    for geo, q in (("G1", "d_adj under resampling of the two photograph sets: 2.5% / 97.5%"), ("G2", "d_T under resampling of the two photograph sets: 2.5% / 97.5%")):
        r = pick(dname, geo, "-", q); L.append(f"| {dname} | {geo} | {r.ci_low:.4f} | {r.ci_high:.4f} |")
L += ["", "## Reading", "", "- G1 answers: does the output contrast align with the part of the photograph contrast not explained by the recorded covariates? The denominator changes with the adjustment, so R changes even if P does not.",
      "- G2 removes from BOTH photographs and outputs the embedding directions along which the covariates shift the photographs; the number of removed directions grows with the covariates (type + style add many dummies), and genuine corpus differences aligned with those directions are removed too: attenuation under (iii) is expected by construction and is not evidence against transfer. Only G2 supports distance comparisons.",
      "- Limits: linear additive adjustment on catalogue strings with pooled rare levels; no alias merging; A and C share few style categories (15) — the adjustment is partly a between-category contrast, not an identification of a preference effect.", ""]
open(os.path.join(OUTI, "report_dino_aggiustamento_completo.md"), "w", encoding="utf-8").write("\n".join(L))
log("done")
