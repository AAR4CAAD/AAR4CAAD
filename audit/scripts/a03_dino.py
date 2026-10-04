"""
Audit step 3 — DINOv2 measures (prompt sections 2, 4A and 6, embedding part).

Reproduction: d, u, P, S, R identities and their statistics on the 159 evaluated triplets and the 192 cells; shuffle null of
the gap; standardised distance; AUC; Spearman with ratings and choices; paired-seed replication; which measure Fig. 1 shows.
New (post-review): distances of BASE and of every adapter to the two photograph centroids (centroid distance and mean of
per-image distances, both reported); direction uncertainty by bootstrap of the photographs; direction adjusted for period,
area and both (specification fixed in outputs/SPEC_direzione_aggiustata.json before running).

Writes outputs/dino_reproduction.csv, outputs/dino_distances.csv, outputs/dino_adjusted_direction.csv, outputs/report_dino.md.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

from common import ANALYSIS, EXPORT_REP_ZIP, OUT, PREVIOUS_REPLY, REPLICATION_EXCLUDED, SEED, Export, Log, as_bool, write_md

log = Log("a03_dino")
rng = np.random.default_rng(SEED)
N_BOOT, N_DIR = 5000, 2000
E = Export(); ER = Export(EXPORT_REP_ZIP)


def unit(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


# ---------------------------------------------------------------- embeddings (L2-normalised CLS, as in freeze.py)
z = np.load(os.path.join(ANALYSIS, "metrics", "embeddings_dinov2_vitb14.npz"), allow_pickle=False)
zr = np.load(os.path.join(ANALYSIS, "metrics", "embeddings_replication_dinov2_vitb14.npz"), allow_pickle=False)
emb = {i: v for i, v in zip(np.concatenate([z["id"], zr["id"]]), unit(np.concatenate([z["cls"], zr["cls"]]).astype(np.float64)))}
D = np.load(os.path.join(ANALYSIS, "baseline", "direction_dinov2.npz"), allow_pickle=False)
aes, ctl = list(D["aesthetic_codes"]), list(D["control_codes"])
runs = E.csv("training_runs.csv").set_index("code")
A_ds = E.csv("aesthetic_dataset.csv"); C_ds = E.csv("control_dataset.csv")
assert set(aes) == set(A_ds[A_ds.dataset_code == runs.training_dataset["RUN-AESTHETIC-4"]].image_code) and set(ctl) == set(C_ds[C_ds.dataset_code == runs.training_dataset["RUN-CONTROL-4"]].image_code)
SI = E.csv("source_images.csv"); photos = list(SI.image_code)
XP = np.stack([emb[c] for c in photos]); XA = np.stack([emb[c] for c in aes]); XC = np.stack([emb[c] for c in ctl])
g = XA.mean(0) - XC.mean(0); d = float(np.linalg.norm(g)); u = g / d
rows = []


def rep(section, quantity, reported, value, lo=None, hi=None, p=None, n=None, source="manuscript rev12", note=""):
    try: diff = round(float(value) - float(reported), 6)
    except (TypeError, ValueError): diff = None
    rows.append(dict(section=section, quantity=quantity, reported=reported, recomputed=value, difference=diff, ci_low=lo, ci_high=hi, p=p, n=n, reported_in=source, note=note))
    log(f"[{section}] {quantity}: reported {reported} | recomputed {value} | CI {lo} {hi} | p {p} | n {n} {note}")


rep("direction", "gap between photograph centroids d", 0.235, round(d, 6), note=f"frozen file: {float(D['cls_gap']):.6f}; identical {abs(d - float(D['cls_gap'])) < 1e-9}; u·u_frozen = {float(u @ D['cls_v']):.9f}")
# shuffle null
lab = np.array([1] * 89 + [0] * 89); XAC = np.vstack([XA, XC]); null = []
for _ in range(2000):
    p_ = rng.permutation(lab); null.append(np.linalg.norm(XAC[p_ == 1].mean(0) - XAC[p_ == 0].mean(0)))
rep("direction", "gap under random relabelling (mean of null)", 0.138, round(float(np.mean(null)), 3), p=round(float((np.array(null) >= d).mean()), 4), note="2000 permutations of the 178 labels")
pooled = np.sqrt(((XA - XA.mean(0)) ** 2).sum(1).mean() / 2 + ((XC - XC.mean(0)) ** 2).sum(1).mean() / 2)
rep("direction", "standardised distance d / pooled multivariate dispersion", 0.26, round(d / pooled, 3), note=f"pooled dispersion {pooled:.4f} (root mean squared distance to the own centroid, averaged over the two sets); previous reply used {0.9131288332377052} with the same meaning → {d / 0.9131288332377052:.3f}")
# AUC of the LOO affinity
proj = []
for i in range(89):
    cA = (XA.sum(0) - XA[i]) / 88; proj.append(XA[i] @ (cA - XC.mean(0)))
for i in range(89):
    cC = (XC.sum(0) - XC[i]) / 88; proj.append(XC[i] @ (XA.mean(0) - cC))
auc = stats.mannwhitneyu(proj[:89], proj[89:]).statistic / (89 * 89)
rep("direction", "AUC AESTHETIC vs CONTROL photographs (leave-one-out affinity)", 0.78, round(float(auc), 3), note="AUC of the LOO relative affinity; the manuscript's 0.78 refers to the classifier of the historical report")
# association with external ratings (phase 1, export filter)
PR = E.csv("pretraining_ratings.csv"); PR = PR[~as_bool(PR.excluded_from_analysis)]
mean_r = PR.groupby("image_code").score.mean()
others = [c for c in photos if c not in set(aes) | set(ctl)]
aff_o = np.array([emb[c] @ g for c in others]); rr = stats.spearmanr(aff_o, mean_r.reindex(others))
rep("direction", "Spearman of the projection on the direction with the mean rating, 422 external photographs", 0.39, round(float(rr.statistic), 3), p=float(rr.pvalue), n=len(others))

# ---------------------------------------------------------------- outputs: original pair
G = E.csv("generated_images.csv"); G["o"] = G.opaque_id.str.replace("-", "").str.lower(); G["cell"] = G.prompt_code + "_" + G.seed.astype(str)
G = G[G.generation_plan_id.isin(G[G.training_run.isin(["RUN-AESTHETIC-4", "RUN-CONTROL-4"])].generation_plan_id)]  # the 576 images of the main plans only (the export may also list replication images)
cells = sorted(G.cell.unique()); shown = set(G[(G.condition_code == "BASE") & ~as_bool(G.excluded_by_review_rule)].cell)
prompt_of = np.array([c.rsplit("_", 1)[0] for c in cells])


def mat(cond, run=None, GG=G):
    s = GG[(GG.condition_code == cond)] if run is None else GG[GG.training_run == run]
    o = s.drop_duplicates("cell").set_index("cell").o.reindex(cells); assert o.notna().all()
    return np.stack([emb[i] for i in o])


EB, EA, EC = mat("BASE"), mat("AESTHETIC", "RUN-AESTHETIC-4"), mat("CONTROL", "RUN-CONTROL-4")
P = (EA - EC) @ u; S = (EA - EC) @ g; PA = (EA - EB) @ u; PC = (EC - EB) @ u
m159 = np.array([c in shown for c in cells])
rep("identities", "S = d·P max abs error (192 cells)", 0, float(np.abs(S - d * P).max()), note="S = difference of relative affinities (e·g), P = projection on the unit direction; exact up to rounding")
rep("identities", "R = P/d = S/d² max abs error", 0, float(np.abs(P / d - S / d ** 2).max()))
rep("identities", "sign and rank invariance S vs P (Spearman)", 1, float(stats.spearmanr(S, P).statistic), note="conversion by a positive constant")


def boot_prompts(x, mask=None):
    xm = x if mask is None else x[mask]; pm = prompt_of if mask is None else prompt_of[mask]
    qs = np.unique(pm); means = np.array([xm[pm == q].mean() for q in qs]); W = np.array([(pm == q).sum() for q in qs])
    i = rng.integers(0, len(qs), (N_BOOT, len(qs))); b = (means[i] * W[i]).sum(1) / W[i].sum(1)
    return float(xm.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5)), float(2 * min((b <= 0).mean(), (b >= 0).mean()))


prev = pd.read_csv(os.path.join(PREVIOUS_REPLY, "09_transfer_scale_check.csv")).set_index("measure")
for name, x, repv in (("P (unit-direction projection) A−C", P, 0.0429), ("P A−BASE", PA, 0.0443), ("P C−BASE", PC, 0.0014)):
    m, lo, hi, p = boot_prompts(x, m159); rep("159 triplets", f"mean {name}", repv, round(m, 4), round(lo, 4), round(hi, 4), p, int(m159.sum()), note="bootstrap over prompts (conditional on the frozen direction)")
m, lo, hi, p = boot_prompts(P / d, m159); rep("159 triplets", "transfer ratio R = mean P / d", 0.18, round(m, 4), round(lo, 4), round(hi, 4), p, note="manuscript CI 12–25%")
rep("159 triplets", "share of triplets with P > 0", 0.62, round(float((P[m159] > 0).mean()), 3), n=int(m159.sum()))
for nm, x in (("S", S), ("P", P)):
    xs = x[m159]
    rep("159 triplets", f"{nm}: min / median / mean / max / SD", prev.loc["affinity_difference_S" if nm == "S" else "unit_direction_projection_P", ["minimum", "median", "mean", "maximum", "sample_sd"]].round(4).tolist(),
        [round(float(v), 4) for v in (xs.min(), np.median(xs), xs.mean(), xs.max(), xs.std(ddof=1))], source="previous reply 09_transfer_scale_check", note="Fig. 1 of the manuscript labels −0.0289 / +0.0053 / +0.0995: these are S (affinity difference), while the text's +0.0429 is the mean of P")
# which cells are Fig. 1's
cs = np.array(cells)[m159]; xs = S[m159]
rep("159 triplets", "Fig. 1 cells (min, median, max of S)", "A07/6127; ?; A08/7", f"{cs[xs.argmin()]}; {cs[np.argsort(xs)[len(xs) // 2]]}; {cs[xs.argmax()]}", source="previous reply", note="median cell = the 80th of 159 ordered values")
# association with human judgements
R = E.csv("posttraining_ratings.csv"); R = R[~as_bool(R.excluded_from_analysis)].copy(); R["c"] = R.score - R.groupby("participant_id").score.transform("mean"); R["cell"] = R.prompt_code + "_" + R.seed.astype(str)
tt = R[R.condition_code.isin(["AESTHETIC", "CONTROL"])].groupby(["cell", "condition_code"]).c.mean().unstack(); dh = (tt.AESTHETIC - tt.CONTROL).reindex(cells)
T = E.csv("pairwise_trials.csv"); T = T[~as_bool(T.excluded_from_analysis) & T.answered_at.notna() & (T.selected_side != "Tie")].copy(); T["cell"] = T.prompt_code + "_" + T.seed.astype(str)
x = T[T.left_condition.isin(["AESTHETIC", "CONTROL"]) & T.right_condition.isin(["AESTHETIC", "CONTROL"])]; ch = (x.winner_condition == "AESTHETIC").groupby(x.cell).mean().reindex(cells)
ok = m159 & dh.notna().to_numpy(); r1 = stats.spearmanr(P[ok], dh[ok])
rep("159 triplets", "Spearman P vs human Δ rating A−C", 0.23, round(float(r1.statistic), 3), p=round(float(r1.pvalue), 4), n=int(ok.sum()))
ok2 = m159 & ch.notna().to_numpy(); r2 = stats.spearmanr(P[ok2], ch[ok2])
rep("159 triplets", "Spearman P vs share of A choices", 0.04, round(float(r2.statistic), 3), p=round(float(r2.pvalue), 3), n=int(ok2.sum()))
for name, x, repv in (("P A−C", P, None), ("P A−BASE", PA, None), ("P C−BASE", PC, None)):
    m, lo, hi, p = boot_prompts(x); rep("192 cells", f"mean {name} (original pair, all cells)", repv, round(m, 4), round(lo, 4), round(hi, 4), p, 192)
# amount vs direction
nA, nC = np.linalg.norm(EA - EB, axis=1), np.linalg.norm(EC - EB, axis=1)
rep("192 cells", "mean ‖Δ_A‖ / ‖Δ_C‖ (size of the shift from BASE), 159 / 192", "0.678 / 0.699 (159); 0.701 / 0.719 (192)", f"{nA[m159].mean():.3f} / {nC[m159].mean():.3f} (159); {nA.mean():.3f} / {nC.mean():.3f} (192)", source="historical report B5/B6")

# ---------------------------------------------------------------- replication adapters
GR = ER.csv("generated_images.csv"); GR["o"] = GR.opaque_id.str.replace("-", "").str.lower(); GR["cell"] = GR.prompt_code + "_" + GR.seed.astype(str)
runsR = ER.csv("training_runs.csv").set_index("code")
adapters = {("AESTHETIC", 1254): EA, ("CONTROL", 9865): EC}
for code in sorted(r for r in GR.training_run.dropna().unique() if r.startswith("REP-") and r not in REPLICATION_EXCLUDED):
    corpus = "AESTHETIC" if str(runsR.training_dataset[code]).startswith("AESTHETIC") else "CONTROL"
    adapters[(corpus, int(runsR.seed[code]))] = mat(corpus, code, GR)
seeds = sorted({s for _, s in adapters})
assert all((c, s) in adapters for c in ("AESTHETIC", "CONTROL") for s in seeds), adapters.keys()
for s, repv in zip(seeds, (0.0435, 0.0412, 0.0504)):
    m, lo, hi, p = boot_prompts((adapters[("AESTHETIC", s)] - adapters[("CONTROL", s)]) @ u)
    rep("replication", f"mean P A−C, paired training seed {s}", repv, round(m, 4), round(lo, 4), round(hi, 4), p, 192)
    for c in ("AESTHETIC", "CONTROL"):
        rep("replication", f"{c} seed {s}: along u / along the shared direction", None, f"{((adapters[(c, s)] - EB) @ u).mean():+.4f} / see fig_embedding_shifts", note="")
# shared direction as in figures_transfer.py: mean shift of all six adapters from BASE, made orthogonal to u
shared = np.mean([(adapters[k] - EB).mean(0) for k in adapters], 0); shared -= (shared @ u) * u; w = shared / np.linalg.norm(shared)
for k in sorted(adapters):
    rep("replication", f"{k[0]} seed {k[1]}: mean projection on u / on the shared orthogonal direction w", None, f"{((adapters[k] - EB) @ u).mean():+.4f} / {((adapters[k] - EB) @ w).mean():+.4f}", note="w = mean shift of the six adapters, orthogonalised to u (same construction as fig_embedding_shifts)")
det = [r for r in GR.training_run.dropna().unique() if r in REPLICATION_EXCLUDED]
if det:
    ED = mat("AESTHETIC", det[0], GR)
    rep("replication", "determinism: mean distance between the two runs of seed 1254 (AESTHETIC) / between seeds 1254 and 9865 / between AESTHETIC and CONTROL at seed 1254", "0.32 / 0.63 / 0.68",
        f"{np.linalg.norm(ED - EA, axis=1).mean():.2f} / {np.linalg.norm(adapters[('AESTHETIC', 9865)] - EA, axis=1).mean():.2f} / {np.linalg.norm(adapters[('CONTROL', 1254)] - EA, axis=1).mean():.2f}", source="replication report")

# ---------------------------------------------------------------- distances to the corpora (new)
cA, cC = XA.mean(0), XC.mean(0)
dist_rows = []


def dist_stats(X, name, seed):
    for tgt, cen, Xt in (("AESTHETIC photographs", cA, XA), ("CONTROL photographs", cC, XC)):
        cen_dist = float(np.linalg.norm(X.mean(0) - cen))
        per_img = np.linalg.norm(X - cen, axis=1)                       # distance of each image to the photograph centroid
        mean_pair = np.sqrt(((X[:, None, :] - Xt[None, :, :]) ** 2).sum(-1)).mean(1)   # mean distance to the individual photographs
        dist_rows.append(dict(adapter=name, training_seed=seed, target=tgt, centroid_to_centroid=cen_dist, mean_image_to_centroid=float(per_img.mean()), mean_image_to_photographs=float(mean_pair.mean())))
    return np.linalg.norm(X - cA, axis=1), np.linalg.norm(X - cC, axis=1)


dB = dist_stats(EB, "BASE", 0)
changes = []
for k in sorted(adapters):
    dA_, dC_ = dist_stats(adapters[k], k[0], k[1])
    for tgt, dd, db in (("AESTHETIC photographs", dA_, dB[0]), ("CONTROL photographs", dC_, dB[1])):
        m, lo, hi, p = boot_prompts(dd - db)
        changes.append(dict(adapter=k[0], training_seed=k[1], target=tgt, mean_change_of_image_to_centroid_distance=m, ci_low=lo, ci_high=hi, p_boot=p, own_corpus=(k[0] == tgt.split()[0])))
        log(f"[distances] {k} → {tgt}: Δ per-image distance to centroid {m:+.4f} ({lo:+.4f}/{hi:+.4f}) p {p}")
    # own vs other corpus: difference of changes
    own, oth = (dA_ - dB[0], dC_ - dB[1]) if k[0] == "AESTHETIC" else (dC_ - dB[1], dA_ - dB[0])
    m, lo, hi, p = boot_prompts(own - oth)
    changes.append(dict(adapter=k[0], training_seed=k[1], target="own minus other corpus (approach difference)", mean_change_of_image_to_centroid_distance=m, ci_low=lo, ci_high=hi, p_boot=p, own_corpus=None))
    log(f"[distances] {k}: approach to own minus approach to other {m:+.4f} ({lo:+.4f}/{hi:+.4f})")
# centroid-to-centroid metric: change vs BASE with prompt bootstrap (cells resampled by prompt; both centroids recomputed)
def centroid_change(X, cen):
    qs_ = np.unique(prompt_of); i = rng.integers(0, len(qs_), (N_BOOT, len(qs_)))
    idx = [np.where(prompt_of == q)[0] for q in qs_]
    est = float(np.linalg.norm(X.mean(0) - cen) - np.linalg.norm(EB.mean(0) - cen)); b = []
    for row in i:
        sel = np.concatenate([idx[j] for j in row]); b.append(np.linalg.norm(X[sel].mean(0) - cen) - np.linalg.norm(EB[sel].mean(0) - cen))
    b = np.array(b); return est, float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5)), float(2 * min((b <= 0).mean(), (b >= 0).mean()))
cchg = []
for k in sorted(adapters):
    r_ = {}
    for tgt, cen in (("AESTHETIC photographs", cA), ("CONTROL photographs", cC)):
        m, lo, hi, p = centroid_change(adapters[k], cen); r_[tgt] = m
        cchg.append(dict(adapter=k[0], training_seed=k[1], target=tgt, metric="centroid_to_centroid", change_vs_BASE=m, ci_low=lo, ci_high=hi, p_boot=p))
        log(f"[centroid distances] {k} → {tgt}: Δ centroid distance {m:+.4f} ({lo:+.4f}/{hi:+.4f}) p {p}")
pd.DataFrame(dist_rows).to_csv(os.path.join(OUT, "dino_distances.csv"), index=False)
pd.DataFrame(changes).to_csv(os.path.join(OUT, "dino_distance_changes.csv"), index=False)
pd.DataFrame(cchg).to_csv(os.path.join(OUT, "dino_centroid_distance_changes.csv"), index=False)

# ---------------------------------------------------------------- direction uncertainty (bootstrap of the photographs), original direction
bd, bm = [], []
diffAC = EA - EC
for _ in range(N_DIR):
    ia, ic = rng.integers(0, 89, 89), rng.integers(0, 89, 89)
    gb = XA[ia].mean(0) - XC[ic].mean(0); db_ = np.linalg.norm(gb); bd.append(db_); bm.append((diffAC[m159] @ (gb / db_)).mean())
bd, bm = np.array(bd), np.array(bm)
rep("direction uncertainty", "d: 95% interval from resampling the 89+89 photographs", None, round(d, 4), round(float(np.percentile(bd, 2.5)), 4), round(float(np.percentile(bd, 97.5)), 4), note="the bootstrap d is biased upwards (noise adds length): shown as a scale of uncertainty, not as a corrected estimate")
rep("direction uncertainty", "mean P (159) with the direction re-estimated on resampled photographs", None, round(float(P[m159].mean()), 4), round(float(np.percentile(bm, 2.5)), 4), round(float(np.percentile(bm, 97.5)), 4), note="outputs fixed; only the direction varies")
rep("direction uncertainty", "R with the direction re-estimated", None, round(float(P[m159].mean() / d), 4), round(float(np.percentile(bm / bd, 2.5)), 4), round(float(np.percentile(bm / bd, 97.5)), 4))

# ---------------------------------------------------------------- adjusted directions (specification: SPEC_direzione_aggiustata.json)
M = E.csv("image_metadata.csv").set_index("image_code").reindex(photos)
period = M.period.replace({"pre-1919": "1919-1945"}); area = M.continent
isA = np.array([c in set(aes) for c in photos]); isC = np.array([c in set(ctl) for c in photos])
adj_rows = []


def design(cols):
    X = pd.get_dummies(pd.DataFrame(cols), drop_first=True).astype(float); X.insert(0, "const", 1.0); return X.to_numpy()


def adjusted(name, Xd):
    if Xd is None:
        res, r2 = XP, 0.0
    else:
        beta, *_ = np.linalg.lstsq(Xd, XP, rcond=None); fit = Xd @ beta; res = XP - fit
        r2 = float(1 - ((res - res.mean(0)) ** 2).sum() / ((XP - XP.mean(0)) ** 2).sum())
    ga = res[isA].mean(0) - res[isC].mean(0); da = float(np.linalg.norm(ga)); ua = ga / da
    out = dict(direction=name, d_adj=da, d_ratio=da / d, cosine_with_original=float(ua @ u), mean_R2_covariate_model=r2)
    for s in seeds:
        for lab, Y in (("A_minus_C", adapters[("AESTHETIC", s)] - adapters[("CONTROL", s)]), ("A_minus_BASE", adapters[("AESTHETIC", s)] - EB), ("C_minus_BASE", adapters[("CONTROL", s)] - EB)):
            m, lo, hi, p = boot_prompts(Y @ ua); out[f"{lab}_seed{s}"] = m; out[f"{lab}_seed{s}_lo"] = lo; out[f"{lab}_seed{s}_hi"] = hi
    pooled_ac = np.mean([out[f"A_minus_C_seed{s}"] for s in seeds]); out["A_minus_C_pooled_mean_of_seeds"] = pooled_ac; out["R_pooled"] = pooled_ac / da
    m, lo, hi, p = boot_prompts((EA - EC) @ ua, m159); out["A_minus_C_original_pair_159"] = m; out["A_minus_C_original_pair_159_lo"] = lo; out["A_minus_C_original_pair_159_hi"] = hi; out["R_original_pair_159"] = m / da
    # direction uncertainty: resample the two sets, refit the covariate model on the resampled 600
    bd_, bm_ = [], []
    idxA, idxC, idxO = np.where(isA)[0], np.where(isC)[0], np.where(~isA & ~isC)[0]
    for _ in range(N_DIR // 4):
        sel = np.concatenate([idxA[rng.integers(0, 89, 89)], idxC[rng.integers(0, 89, 89)], idxO])
        Xb = XP[sel]
        if Xd is None: rb = Xb
        else:
            Xdb = Xd[sel]; bb, *_ = np.linalg.lstsq(Xdb, Xb, rcond=None); rb = Xb - Xdb @ bb
        gb = rb[:89].mean(0) - rb[89:178].mean(0); dbb = np.linalg.norm(gb); bd_.append(dbb); bm_.append(np.mean([((adapters[("AESTHETIC", s)] - adapters[("CONTROL", s)]) @ (gb / dbb)).mean() for s in seeds]))
    bd_, bm_ = np.array(bd_), np.array(bm_)
    out.update(d_adj_boot_lo=float(np.percentile(bd_, 2.5)), d_adj_boot_hi=float(np.percentile(bd_, 97.5)), A_minus_C_pooled_dirboot_lo=float(np.percentile(bm_, 2.5)), A_minus_C_pooled_dirboot_hi=float(np.percentile(bm_, 97.5)),
               R_pooled_dirboot_lo=float(np.percentile(bm_ / bd_, 2.5)), R_pooled_dirboot_hi=float(np.percentile(bm_ / bd_, 97.5)))
    adj_rows.append(out)
    log(f"[adjusted] {name}: d_adj {da:.4f} ({da / d:.0%} of d), cos {ua @ u:+.3f}, R2 {r2:.3f}; A−C pooled {pooled_ac:+.4f} → R {pooled_ac / da:.3f}; per seed " + ", ".join(f"{out[f'A_minus_C_seed{s}']:+.4f} [{out[f'A_minus_C_seed{s}_lo']:+.4f},{out[f'A_minus_C_seed{s}_hi']:+.4f}]" for s in seeds) + f"; dir-boot R {np.percentile(bm_ / bd_, 2.5):.3f}-{np.percentile(bm_ / bd_, 97.5):.3f}")
    return ua


u0 = adjusted("original (no adjustment)", None)
adjusted("adjusted for period", design({"period": period}))
adjusted("adjusted for area", design({"area": area}))
adjusted("adjusted for period and area (additive)", design({"period": period, "area": area}))
pd.DataFrame(adj_rows).to_csv(os.path.join(OUT, "dino_adjusted_direction.csv"), index=False)
# category counts
cat = pd.DataFrame({"period": period, "area": area, "set": np.where(isA, "AESTHETIC", np.where(isC, "CONTROL", "other"))})
ct_p = pd.crosstab(cat.period, cat.set); ct_a = pd.crosstab(cat.area, cat.set)
pd.DataFrame(rows).to_csv(os.path.join(OUT, "dino_reproduction.csv"), index=False)

# ---------------------------------------------------------------- report
def md_table(ct):
    L_ = ["| " + ct.index.name + " | " + " | ".join(map(str, ct.columns)) + " |", "|---" * (len(ct.columns) + 1) + "|"]
    for i, r in ct.iterrows(): L_.append("| " + str(i) + " | " + " | ".join(str(int(v)) for v in r) + " |")
    return chr(10).join(L_)


A = pd.DataFrame(adj_rows)
L = ["# DINOv2 measures — reproduction, distances to the corpora, adjusted directions (audit rev12)", "",
     "Space: DINOv2 CLS, L2-normalised. g = centroid(AESTHETIC photos) − centroid(CONTROL photos); d = ‖g‖; u = g/d. For a cell: P = (e_A − e_C)·u; S = (e_A − e_C)·g = d·P; R = P/d = S/d². "
     "Intervals: bootstrap over the 48 prompts unless stated (conditional on the direction). The 'direction uncertainty' rows resample the photographs.", "",
     "## Reproduction", "", "| section | quantity | reported | recomputed | 95% CI | p | n | note |", "|---|---|---|---|---|---|---|---|"]
for r in rows:
    ci = "" if r["ci_low"] is None else f"{r['ci_low']} / {r['ci_high']}"
    L.append(f"| {r['section']} | {r['quantity']} | {r['reported']} | {r['recomputed']} | {ci} | {'' if r['p'] is None else r['p']} | {'' if r['n'] is None else r['n']} | {r['note']} |")
L += ["", "**Which measure is in which figure/sentence.** Fig. 1 (min −0.0289, median +0.0053, max +0.0995) shows S; the text (+0.0429, 18%, Spearman +0.23, 62% positive) uses P and R. S and P differ by the constant d = 0.2352: identical signs, ranks and p-values. Fig. 3 plots P-type projections of cell means on u and on the shared orthogonal direction.", "",
      "## Distances to the two photograph corpora (new, post-review)", "",
      "Two metrics are reported and must not be confused: (i) distance between centroids (adapter mean image → photograph centroid); (ii) mean over images of the distance of each generated image to the photograph centroid. "
      "The *change* columns use (ii) per cell (adapter image minus the BASE image of the same cell), with prompt-bootstrap intervals.", "",
      "| adapter | seed | target | centroid→centroid | mean image→centroid | mean image→photographs |", "|---|---|---|---|---|---|"]
for r in dist_rows:
    L.append(f"| {r['adapter']} | {r['training_seed']} | {r['target']} | {r['centroid_to_centroid']:.4f} | {r['mean_image_to_centroid']:.4f} | {r['mean_image_to_photographs']:.4f} |")
L += ["", "| adapter | seed | target | Δ mean image→centroid distance vs BASE | 95% CI | p |", "|---|---|---|---|---|---|"]
for r in changes:
    L.append(f"| {r['adapter']} | {r['training_seed']} | {r['target']} | {r['mean_change_of_image_to_centroid_distance']:+.4f} | {r['ci_low']:+.4f} / {r['ci_high']:+.4f} | {r['p_boot']:.4f} |")
L += ["", "Negative Δ = the adapter's images are closer to that corpus than BASE's. 'own minus other' < 0 means the adapter approaches its own corpus more than the other one.", "",
      "Centroid-to-centroid metric (change vs BASE, prompt bootstrap, both centroids recomputed in each resample):", "", "| adapter | seed | target | Δ centroid→centroid | 95% CI | p |", "|---|---|---|---|---|---|"]
for r in cchg:
    L.append(f"| {r['adapter']} | {r['training_seed']} | {r['target']} | {r['change_vs_BASE']:+.4f} | {r['ci_low']:+.4f} / {r['ci_high']:+.4f} | {r['p_boot']:.4f} |")
L += ["", "The two metrics answer different questions (mean position vs spread of individual images) and are reported separately.", "",
      "## Direction adjusted for period and area (specification fixed before the run: `SPEC_direzione_aggiustata.json`)", "",
      "The adjustment residualises the 600 photograph embeddings on recorded period (pre-1919 merged with 1919–1945) and recorded area (8 labels, kept as recorded) by per-dimension OLS; the adjusted direction is the A−C difference of the mean residuals. "
      "Outputs are not residualised (they have no period/area): the numbers are projections of the original outputs on an adjusted source direction.", "",
      "| direction | d_adj | d_adj/d | cos with original | mean R² of the covariate model | A−C seed 1254 | seed 9865 | seed 42160 | pooled | R pooled | R, direction-bootstrap 95% | original pair 159: A−C | R |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for _, r in A.iterrows():
    L.append(f"| {r.direction} | {r.d_adj:.4f} | {r.d_ratio:.3f} | {r.cosine_with_original:+.3f} | {r.mean_R2_covariate_model:.3f} | " + " | ".join(f"{r[f'A_minus_C_seed{s}']:+.4f} [{r[f'A_minus_C_seed{s}_lo']:+.4f}, {r[f'A_minus_C_seed{s}_hi']:+.4f}]" for s in seeds) +
             f" | {r.A_minus_C_pooled_mean_of_seeds:+.4f} | {r.R_pooled:.3f} | {r.R_pooled_dirboot_lo:.3f} – {r.R_pooled_dirboot_hi:.3f} | {r.A_minus_C_original_pair_159:+.4f} [{r.A_minus_C_original_pair_159_lo:+.4f}, {r.A_minus_C_original_pair_159_hi:+.4f}] | {r.R_original_pair_159:.3f} |")
L += ["", "A−BASE and C−BASE on the adjusted directions are in `dino_adjusted_direction.csv`.", "",
      "Category counts (photographs): period × set", "", md_table(ct_p), "", "area × set", "", md_table(ct_a), "",
      "Limits: linear additive adjustment on two recorded variables only; small cells; the adjustment cannot turn the design into an experiment that isolates preference from composition.", ""]
write_md("report_dino.md", L)
json.dump(dict(d=d, pooled_dispersion=pooled, seeds=seeds), open(os.path.join(OUT, "dino_constants.json"), "w"), indent=1)
log("done")
