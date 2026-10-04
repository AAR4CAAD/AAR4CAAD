"""
Integration step 2 (and 4) — independent reproduction of the author's local verifications (AAR_integrazione_mirata) and the
out-of-training check with intra-corpus dispersion.

- per-photograph phase-1 statistics on the complete sample (166 / 23,012): n, distinct raters, mean, sample SD, SE; compared with 02/03 files
- selection rule re-run against the historical code (SelectionService.Evaluate: eligible = active & n >= 10; percentile cutoff with linear
  interpolation on the ELIGIBLE means; mean >= cutoff AND mean >= 5) -> exactly the 89 AESTHETIC?
- rater bootstrap (3000, raters resampled with replacement, all their answers kept, multiplicity preserved) with BOTH conventions for the
  percentile population (author's: all active images; historical: eligible n >= 10) -> cardinality, recovery, Jaccard, inclusion frequency
- historical ICC estimator on complete and filtered samples (formula, k0, n)
- batch counts (corpus_batch, import dates)
- exact binomial 677/1320 with Clopper–Pearson
- out-of-training check: Spearman between projection on u (from the matrices) and mean rating of the 422 external photographs, complete
  and filtered; intra-corpus dispersion (RMS distance to own centroid AND mean pairwise distance, both reported) for A and C with bootstrap
Writes integrazione/verifica_tabelle_locali.csv, integrazione/stabilita_bootstrap_riprodotta.csv, integrazione/report_verifiche_locali.md.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

from common import ANALYSIS, AUDIT, Export, Log, as_bool

OUTI = os.path.join(AUDIT, "integrazione"); PK = os.path.join(AUDIT, "inputs", "integrazione_mirata")
log = Log("b02_verifiche_locali"); E = Export(); rng = np.random.default_rng(20261004)
PR_all = E.csv("pretraining_ratings.csv"); PR = PR_all[~as_bool(PR_all.excluded_from_analysis)]
SI = E.csv("source_images.csv"); active = set(SI[as_bool(SI.is_active)].image_code)
runs = E.csv("training_runs.csv").set_index("code"); A_ds = E.csv("aesthetic_dataset.csv"); C_ds = E.csv("control_dataset.csv")
aes = set(A_ds[A_ds.dataset_code == runs.training_dataset["RUN-AESTHETIC-4"]].image_code); ctl = set(C_ds[C_ds.dataset_code == runs.training_dataset["RUN-CONTROL-4"]].image_code)
rule = pd.read_json(os.path.join(E.folder, "selection_rules.json")).iloc[-1]["rule"]; MIN_N, MEAN, TOP = int(rule["minimumRatings"]), float(rule["meanThreshold"]), float(rule["topPercentile"])
rows = []
def chk(section, quantity, package_value, recomputed, note=""):
    ok = None
    try: ok = abs(float(package_value) - float(recomputed)) < 1e-6
    except (TypeError, ValueError): ok = str(package_value) == str(recomputed)
    rows.append(dict(section=section, quantity=quantity, package_value=package_value, recomputed=recomputed, agree=ok, note=note)); log(f"[{section}] {quantity}: package {package_value} | recomputed {recomputed} | agree {ok} {note}")

# ---------------------------------------------------------------- per-photo statistics (complete sample)
dup = int(PR_all.duplicated(["participant_id", "image_code"]).sum()); chk("fase1", "duplicate participant-photo pairs", 0, dup)
g = PR_all.groupby("image_code").score.agg(n="size", mean="mean", sd=lambda s: s.std(ddof=1)); g["raters"] = PR_all.groupby("image_code").participant_id.nunique(); g["se"] = g.sd / np.sqrt(g.n)
P600 = pd.read_csv(os.path.join(PK, "02_fase1_per_600_foto.csv")).set_index("image_code")
for col_pk, col_me in (("n_giudizi", "n"), ("n_valutatori_distinti", "raters"), ("media", "mean"), ("sd_campionaria", "sd"), ("errore_standard_media", "se")):
    diff = float((P600[col_pk] - g[col_me].reindex(P600.index)).abs().max()); chk("fase1", f"per-photo {col_pk}: max abs difference over 600", 0, round(diff, 10))
ga = g.loc[sorted(aes)]; chk("fase1", "89 AESTHETIC: n range", "14-64", f"{int(ga.n.min())}-{int(ga.n.max())}"); chk("fase1", "89 AESTHETIC: SE range", "0.1533-0.4871", f"{ga.se.min():.4f}-{ga.se.max():.4f}")

# ---------------------------------------------------------------- selection rule vs historical code
def select(ratings, population="eligible"):
    s = ratings[ratings.image_code.isin(active)].groupby("image_code").score.agg(["size", "mean"])
    elig = s[s["size"] >= MIN_N]
    pop = elig["mean"] if population == "eligible" else s["mean"]
    cut = float(np.percentile(pop, 100 - TOP)) if len(pop) else -np.inf        # numpy default = linear interpolation = Statistics.Percentile
    return set(elig[(elig["mean"] >= cut) & (elig["mean"] >= MEAN)].index), cut
sel, cut = select(PR_all); chk("regola", "historical rule on the complete sample reproduces the 89 AESTHETIC (eligible-population percentile)", True, sel == aes, f"cutoff P65 = {cut:.3f} (platform recorded 4.563)")
sel2, cut2 = select(PR_all, "all"); chk("regola", "author's convention (percentile over all active images) gives the same 89", True, sel2 == aes, f"cutoff {cut2:.3f}; both non-binding because < 5")

# ---------------------------------------------------------------- rater bootstrap
raters = PR_all.participant_id.unique(); by_r = {p: d for p, d in PR_all.groupby("participant_id")}
def rater_bootstrap(B, population):
    out = []; incl = pd.Series(0.0, index=sorted(active))
    for b in range(B):
        draw = rng.choice(raters, len(raters), replace=True)                 # multiplicity preserved: duplicated raters contribute their answers twice
        R_ = pd.concat([by_r[p] for p in draw]); s_, cut_ = select(R_, population)
        incl[list(s_ & set(incl.index))] += 1
        out.append(dict(replica=b + 1, n_selected=len(s_), n_original_recovered=len(s_ & aes), recovery=len(s_ & aes) / 89, jaccard=len(s_ & aes) / len(s_ | aes), cutoff=cut_))
    return pd.DataFrame(out), incl / B
B = 3000
bs_e, inc_e = rater_bootstrap(B, "eligible"); bs_a, inc_a = rater_bootstrap(B, "all")
pk = json.load(open(os.path.join(PK, "RISULTATI_LOCALI.json"), encoding="utf-8"))
for lab, bs in (("historical convention (eligible)", bs_e), ("author's convention (all active)", bs_a)):
    chk("stabilita", f"{lab}: mean cardinality", round(pk["cardinality_mean"], 3), round(float(bs.n_selected.mean()), 3), "different seed and convention: compare distributions, not digits")
    chk("stabilita", f"{lab}: cardinality quantiles 2.5/50/97.5", [round(v, 1) for v in pk["cardinality_quantiles_025_50_975"]], [round(float(v), 1) for v in np.percentile(bs.n_selected, [2.5, 50, 97.5])])
    chk("stabilita", f"{lab}: mean recovery of the 89", round(pk["recovery_mean"], 4), round(float(bs.recovery.mean()), 4))
    chk("stabilita", f"{lab}: mean Jaccard", round(pk["jaccard_mean"], 4), round(float(bs.jaccard.mean()), 4))
inc_pk = pd.read_csv(os.path.join(PK, "02_fase1_per_600_foto.csv")).set_index("image_code").probabilita_inclusione_bootstrap
chk("stabilita", "inclusion probability of the 89: min / median / max (historical convention)", [round(v, 3) for v in pk["original_inclusion_probability_min_median_max"]], [round(float(v), 3) for v in (inc_e[sorted(aes)].min(), inc_e[sorted(aes)].median(), inc_e[sorted(aes)].max())])
chk("stabilita", "correlation of per-image inclusion probabilities with the package's (600 images)", 1, round(float(np.corrcoef(inc_e.reindex(inc_pk.index).fillna(0), inc_pk.fillna(0))[0, 1]), 4))
bs_e.assign(convention="eligible").to_csv(os.path.join(OUTI, "stabilita_bootstrap_riprodotta.csv"), index=False)
pd.DataFrame({"inclusion_probability_eligible_convention": inc_e, "inclusion_probability_all_active_convention": inc_a, "in_frozen_AESTHETIC": inc_e.index.isin(aes), "in_CONTROL": inc_e.index.isin(ctl)}).to_csv(os.path.join(OUTI, "stabilita_inclusione_per_foto.csv"))

# ---------------------------------------------------------------- ICC historical estimator
def icc(df):
    df = df.copy(); df["c"] = df.score - df.groupby("participant_id").score.transform("mean")
    g_ = df.groupby("image_code").c.agg(["mean", "count", "var"]); g_ = g_[g_["count"] >= 2]; x = df[df.image_code.isin(g_.index)]
    a, N, grand = len(g_), g_["count"].sum(), x.c.mean(); msb = (g_["count"] * (g_["mean"] - grand) ** 2).sum() / (a - 1)
    dfw = N - a - (df.participant_id.nunique() - 1); msw = (g_["var"] * (g_["count"] - 1)).sum() / dfw; k0 = (N - (g_["count"] ** 2).sum() / N) / (a - 1)
    return dict(MS_between=msb, MS_within=msw, df_within=dfw, k0=k0, ICC1=(msb - msw) / (msb + (k0 - 1) * msw), ICCk=(msb - msw) / msb, n_part=df.participant_id.nunique(), n=len(df))
for lab, df_, pkrow in (("complete", PR_all, pk["icc"][0]), ("filtered", PR, pk["icc"][1])):
    r = icc(df_)
    for k_, pkk in (("ICC1", "ICC1_storico"), ("ICCk", "ICCk_storico"), ("k0", "k0"), ("MS_between", "MS_between"), ("MS_within", "MS_within"), ("df_within", "df_within")):
        chk("icc", f"{lab}: {k_}", round(pkrow[pkk], 6), round(float(r[k_]), 6), "one-way ANOVA on rater-centred scores, df_within reduced by (raters − 1); NOT a crossed model" if k_ == "ICC1" else "")

# ---------------------------------------------------------------- batches
B4 = pd.read_csv(os.path.join(PK, "04_conteggi_per_lotto.csv"))
SIb = SI.set_index("image_code"); PR_all["batch"] = PR_all.image_code.map(SIb.corpus_batch)
for _, r in B4[B4.dataset == "all"].iterrows():
    sub = PR_all[PR_all.batch == r.batch]; chk("lotti", f"batch {r.batch}: photographs / ratings / raters", f"{r.n_fotografie}/{r.n_giudizi}/{r.n_valutatori_con_almeno_un_giudizio}", f"{int((SIb.corpus_batch == r.batch).sum())}/{len(sub)}/{sub.participant_id.nunique()}", "import dates from source_images.imported_at")
for ds, S_ in (("AESTHETIC", aes), ("CONTROL", ctl)):
    for b in (1, 2):
        r = B4[(B4.dataset == ds) & (B4.batch == b)].iloc[0]; chk("lotti", f"batch {b} {ds}: photographs", int(r.n_fotografie), int(sum(SIb.corpus_batch[c] == b for c in S_)))

# ---------------------------------------------------------------- binomial
T = E.csv("pairwise_trials.csv"); T = T[~as_bool(T.excluded_from_analysis) & T.answered_at.notna() & (T.selected_side != "Tie")]
x = T[T.left_condition.isin(["AESTHETIC", "CONTROL"]) & T.right_condition.isin(["AESTHETIC", "CONTROL"])]; wins = int((x.winner_condition == "AESTHETIC").sum()); n = len(x)
bt = stats.binomtest(wins, n, 0.5); ci = bt.proportion_ci(0.95, method="exact")
chk("binomiale", "wins / n", "677/1320", f"{wins}/{n}"); chk("binomiale", "two-sided exact p", round(pk["binomiale"]["p_bilaterale_esatto"], 10), round(float(bt.pvalue), 10))
chk("binomiale", "Clopper–Pearson 95% low / high", f"{pk['binomiale']['ci95_cp_low']:.6f}/{pk['binomiale']['ci95_cp_high']:.6f}", f"{ci.low:.6f}/{ci.high:.6f}", "marginal summary assuming independent comparisons; does not replace the clustered inference")

# ---------------------------------------------------------------- out-of-training check on the matrices + dispersion
z = np.load(os.path.join(ANALYSIS, "metrics", "embeddings_dinov2_vitb14.npz"), allow_pickle=False); emb = {i: v / np.linalg.norm(v) for i, v in zip(z["id"], z["cls"].astype(np.float64))}
D = np.load(os.path.join(ANALYSIS, "baseline", "direction_dinov2.npz"), allow_pickle=False); u = D["cls_v"]
others = [c for c in SI.image_code if c not in aes | ctl]; proj = np.array([emb[c] @ u for c in others])
m_all = PR_all.groupby("image_code").score.mean(); m_f = PR.groupby("image_code").score.mean()
r1 = stats.spearmanr(proj, m_all.reindex(others)); r2 = stats.spearmanr(proj, m_f.reindex(others))
chk("fuori_training", "n external photographs", 422, len(others)); chk("fuori_training", "Spearman projection-on-u vs mean rating, complete sample", round(pk["heldout"][0]["spearman_rho"], 6), round(float(r1.statistic), 6), "projection on u from the matrices (affinity = d·projection: same ranks)")
chk("fuori_training", "Spearman, filtered sample", round(pk["heldout"][1]["spearman_rho"], 6), round(float(r2.statistic), 6))
aff = pd.read_csv(os.path.join(ANALYSIS, "embedding_report", "source_affinity_dino.csv")).set_index("image_code").relative_source_set_affinity
chk("fuori_training", "Spearman(saved affinity, projection on u) over the 422", 1, round(float(stats.spearmanr(aff.reindex(others), proj).statistic), 6), "the saved affinity is a positive affine transform of the projection for non-members")
XA = np.stack([emb[c] for c in sorted(aes)]); XC = np.stack([emb[c] for c in sorted(ctl)])
def disp(X):
    cen = X.mean(0); rms = float(np.sqrt(((X - cen) ** 2).sum(1).mean())); mean_to_cen = float(np.linalg.norm(X - cen, axis=1).mean())
    pw = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(-1)); iu = np.triu_indices(len(X), 1); return rms, mean_to_cen, float(pw[iu].mean())
dA, dC = disp(XA), disp(XC); bA, bC = [], []
for _ in range(2000):
    bA.append(disp(XA[rng.integers(0, 89, 89)])); bC.append(disp(XC[rng.integers(0, 89, 89)]))
bA, bC = np.array(bA), np.array(bC)
for j, lab in enumerate(["RMS distance to own centroid", "mean distance to own centroid", "mean pairwise distance"]):
    rows.append(dict(section="dispersione", quantity=f"AESTHETIC: {lab}", package_value="", recomputed=round(dA[j], 4), agree=None, note=f"bootstrap of photographs 95% {np.percentile(bA[:, j], 2.5):.4f}–{np.percentile(bA[:, j], 97.5):.4f} (biased downward by resampling duplicates)"))
    rows.append(dict(section="dispersione", quantity=f"CONTROL: {lab}", package_value="", recomputed=round(dC[j], 4), agree=None, note=f"95% {np.percentile(bC[:, j], 2.5):.4f}–{np.percentile(bC[:, j], 97.5):.4f}"))
    rows.append(dict(section="dispersione", quantity=f"A − C: {lab}", package_value="", recomputed=round(dA[j] - dC[j], 4), agree=None, note=f"difference bootstrap 95% {np.percentile(bA[:, j] - bC[:, j], 2.5):+.4f}/{np.percentile(bA[:, j] - bC[:, j], 97.5):+.4f}"))
    log(f"[dispersione] {lab}: A {dA[j]:.4f} C {dC[j]:.4f} diff {dA[j] - dC[j]:+.4f}")
rows.append(dict(section="dispersione", quantity="pooled RMS dispersion used for the standardised distance 0.26", package_value="", recomputed=round(float(np.sqrt((dA[0] ** 2 + dC[0] ** 2) / 2)), 4), agree=None, note="d / pooled RMS = " + f"{0.2352287934639978 / np.sqrt((dA[0] ** 2 + dC[0] ** 2) / 2):.3f}"))
pd.DataFrame(rows).to_csv(os.path.join(OUTI, "verifica_tabelle_locali.csv"), index=False)
L = ["# Verification of the author's local tables (AAR_integrazione_mirata) and out-of-training check", "", "| section | quantity | package | recomputed | agree | note |", "|---|---|---|---|---|---|"]
for r in rows: L.append(f"| {r['section']} | {r['quantity']} | {r['package_value']} | {r['recomputed']} | {'' if r['agree'] is None else r['agree']} | {r['note']} |")
L += ["", "Notes. (1) The historical rule (`SelectionService.Evaluate`) computes the percentile cutoff on the ELIGIBLE images (active, n ≥ 10) with linear interpolation; the package's specification uses all active images. On the original data both give the 89 AESTHETIC because the cutoff is below 5 in both cases; in the rater bootstrap the two conventions are reported separately. (2) Bootstrap distributions are compared, not digits: different seed. (3) Inclusion frequencies measure internal stability of the selection under resampling of the raters, not generalisation. (4) The out-of-training correlation verifies that the photograph direction is associated with the ratings outside the LoRA sets; it says nothing about memorisation of training examples in the outputs, and 'held out' refers to the LoRA, not to the SDXL pretraining.", ""]
open(os.path.join(OUTI, "report_verifiche_locali.md"), "w", encoding="utf-8").write("\n".join(L)); log("done")
