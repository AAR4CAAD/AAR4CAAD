"""
Integration step 5 — complete Table 3: every contrast (A−C, BASE−C, A−BASE) by every method already used in the audit v2.
  ratings:  participant-level t test; crossed mixed model (linear contrasts from the coefficient covariance matrix);
            two-way participant×prompt pigeonhole bootstrap (participant multiplicity preserved in the outer mean; all three
            contrasts from the SAME replicates; replicates without eligible data counted)
  pairs:    Bradley–Terry (decisive, cluster participant); Davidson with ties (cluster participant; two-way bootstrap, same
            replicates); exact binomial on decisive choices (marginal, i.i.d. assumption declared)
Also operational definitions of 'global filter' and 'incomplete phase 2' from the export fields.
Writes integrazione/tabella3_completa.csv and integrazione/report_tabella3.md.
"""
import math
import os
import time

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from scipy.optimize import minimize

from common import AUDIT, SEED, Export, Log, as_bool

OUTI = os.path.join(AUDIT, "integrazione"); log = Log("b05_tabella3"); E = Export(); rng = np.random.default_rng(SEED); N_BOOT = 2000
R_all = E.csv("posttraining_ratings.csv"); T_all = E.csv("pairwise_trials.csv"); P = E.csv("participants.csv"); PS = E.csv("posttraining_sessions.csv")
R = R_all[~as_bool(R_all.excluded_from_analysis)].copy(); T = T_all[~as_bool(T_all.excluded_from_analysis) & T_all.answered_at.notna()].copy()
for d in (R, T): d["trip"] = d.prompt_code + "_" + d.seed.astype(str)
D = T[T.selected_side != "Tie"].copy()
CONTR = {"A−C": ("AESTHETIC", "CONTROL"), "BASE−C": ("BASE", "CONTROL"), "A−BASE": ("AESTHETIC", "BASE")}
rows = []
def add(contrast, method, unit, n, est, lo=None, hi=None, p=None, note=""):
    rows.append(dict(contrast=contrast, method=method, unit=unit, n=n, estimate=est, ci_low=lo, ci_high=hi, p=p, note=note)); log(f"{contrast:7s} | {method}: {est:+.4f} [{'' if lo is None else f'{lo:+.4f}'}, {'' if hi is None else f'{hi:+.4f}'}] p={p} n={n}")

# ---------------------------------------------------------------- ratings: participant t
def pdiff(a, b, minn=3):
    c = R[R.condition_code.isin([a, b])].groupby(["participant_id", "condition_code"]).score.agg(["mean", "count"]).unstack(); ok = (c["count"][a] >= minn) & (c["count"][b] >= minn)
    return (c["mean"][a] - c["mean"][b])[ok].dropna()
for k, (a, b) in CONTR.items():
    x = pdiff(a, b); n = len(x); m = x.mean(); se = x.std(ddof=1) / math.sqrt(n); q = stats.t.ppf(.975, n - 1)
    add(k, "ratings: participant-level mean difference, one-sample t", "participants (≥3 ratings per condition)", n, m, m - q * se, m + q * se, stats.ttest_1samp(x, 0).pvalue, f"d_z {m / x.std(ddof=1):+.3f}")
# ---------------------------------------------------------------- ratings: crossed mixed model, linear contrasts
Rm = R.copy(); Rm["cond"] = pd.Categorical(Rm.condition_code, ["CONTROL", "AESTHETIC", "BASE"]); Rm["one"] = 1
t0 = time.time(); mf = sm.MixedLM.from_formula("score ~ C(cond)", groups="one", re_formula="0", vc_formula={"participant": "0 + C(participant_id)", "cell": "0 + C(trip)", "image": "0 + C(generated_image_id)"}, data=Rm).fit(reml=True, method="lbfgs", maxiter=500)
beta = mf.params[["C(cond)[T.AESTHETIC]", "C(cond)[T.BASE]"]].to_numpy(); V = mf.cov_params().loc[["C(cond)[T.AESTHETIC]", "C(cond)[T.BASE]"], ["C(cond)[T.AESTHETIC]", "C(cond)[T.BASE]"]].to_numpy()
L_ = {"A−C": np.array([1.0, 0.0]), "BASE−C": np.array([0.0, 1.0]), "A−BASE": np.array([1.0, -1.0])}
vc = dict(zip(mf.model.exog_vc.names, [float(v) for v in mf.vcomp]))
for k, l in L_.items():
    est = float(l @ beta); se = math.sqrt(float(l @ V @ l)); add(k, "ratings: linear mixed model, crossed random intercepts (participant + prompt×seed cell + image), linear contrast", "ratings (9,413)", len(Rm), est, est - 1.96 * se, est + 1.96 * se, 2 * stats.norm.sf(abs(est / se)), f"REML, converged {mf.converged}; variance components {vc}; residual {mf.scale:.4f}; contrast SE from the coefficient covariance matrix")
log(f"mixed model {time.time() - t0:.0f}s")
# ---------------------------------------------------------------- ratings: two-way bootstrap, same replicates for the three contrasts
pid, prm = R.participant_id.values, R.prompt_code.values; up, uq = np.unique(pid), np.unique(prm); ip, iq = np.searchsorted(up, pid), np.searchsorted(uq, prm)
cond = R.condition_code.values; sc = R.score.values
bs = {k: [] for k in CONTR}; empty = {k: 0 for k in CONTR}; dropped = {k: [] for k in CONTR}
for _ in range(N_BOOT):
    wp = rng.multinomial(len(up), np.ones(len(up)) / len(up)); wq = rng.multinomial(len(uq), np.ones(len(uq)) / len(uq)); w = wp[ip] * wq[iq]; keep = w > 0
    df_ = pd.DataFrame({"p": pid[keep], "c": cond[keep], "s": sc[keep], "w": w[keep]}); df_["ws"] = df_.s * df_.w
    agg = df_.groupby(["p", "c"]).agg(ws=("ws", "sum"), w=("w", "sum")); mean = (agg.ws / agg.w).unstack()
    for k, (a, b) in CONTR.items():
        if a not in mean.columns or b not in mean.columns: empty[k] += 1; continue
        d_ = (mean[a] - mean[b]).dropna()
        if len(d_) == 0: empty[k] += 1; continue
        mult = wp[np.searchsorted(up, d_.index.to_numpy())]; bs[k].append(float(np.average(d_.to_numpy(), weights=mult))); dropped[k].append(len(set(up[wp > 0])) - len(d_))
for k, (a, b) in CONTR.items():
    x = pdiff(a, b); add(k, "ratings: two-way (participant × prompt) pigeonhole bootstrap of the participant-level mean difference", "participants × prompts", f"{len(up)} × {len(uq)}", float(x.mean()), float(np.percentile(bs[k], 2.5)), float(np.percentile(bs[k], 97.5)), None,
                       f"{len(bs[k])} usable replicates of {N_BOOT}; replicates with no eligible participant: {empty[k]}; mean drawn participants dropped for lacking one condition: {np.mean(dropped[k]):.2f}; outer mean weighted by participant multiplicity; same replicates for the three contrasts")
# ---------------------------------------------------------------- pairs: Bradley–Terry (decisive) cluster participant
def bt(df, ref, groups):
    others = [c for c in ["AESTHETIC", "CONTROL", "BASE"] if c != ref]
    X = pd.DataFrame({"const": 1.0, **{c: (df.left_condition == c).astype(float) - (df.right_condition == c).astype(float) for c in others}})
    r = sm.GLM((df.selected_side == "Left").astype(float), X, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": groups}); g = len(np.unique(groups)); q = stats.t.ppf(.975, g - 1)
    return {c: (r.params[c], r.bse[c], q, g) for c in others}
b = bt(D, "CONTROL", D.participant_id.values); bb = bt(D, "BASE", D.participant_id.values)
for k, (coef, se, q, g) in (("A−C", b["AESTHETIC"]), ("BASE−C", b["BASE"]), ("A−BASE", bb["AESTHETIC"])):
    add(k, "pairs: Bradley–Terry odds ratio (decisive choices), cluster-robust by participant", "decisive comparisons", len(D), math.exp(coef), math.exp(coef - q * se), math.exp(coef + q * se), 2 * stats.t.sf(abs(coef / se), g - 1), "OR; ties excluded; left-position intercept")
# ---------------------------------------------------------------- pairs: Davidson (ties), cluster CI and two-way bootstrap
def dav_fit(df, weights=None):
    others = ["AESTHETIC", "BASE"]; X = np.column_stack([np.ones(len(df))] + [(df.left_condition == c).astype(float).values - (df.right_condition == c).astype(float).values for c in others]); y = df.selected_side.map({"Left": 1, "Right": 0, "Tie": 2}).values
    wts = np.ones(len(df)) if weights is None else weights; idx = np.arange(len(df))
    def ll_i(th):
        eta = X @ th[:-1]; W = np.column_stack([np.zeros(len(df)), eta, th[-1] + eta / 2]); mx = W.max(1, keepdims=True); return W[idx, y] - (mx[:, 0] + np.log(np.exp(W - mx).sum(1)))
    def grad(th):
        eta = X @ th[:-1]; W = np.column_stack([np.zeros(len(df)), eta, th[-1] + eta / 2]); W -= W.max(1, keepdims=True); Pm = np.exp(W); Pm /= Pm.sum(1, keepdims=True)
        de = (y == 1) + 0.5 * (y == 2) - Pm[:, 1] - 0.5 * Pm[:, 2]; dn = (y == 2) - Pm[:, 2]; return -np.concatenate([X.T @ (wts * de), [np.sum(wts * dn)]])
    r = minimize(lambda th: -np.sum(wts * ll_i(th)), np.zeros(X.shape[1] + 1), jac=grad, method="BFGS", options={"gtol": 1e-7, "maxiter": 2000}); return r.x, ll_i, X
th, ll_i, X = dav_fit(T); m_ = len(th); h = 1e-5
S = np.column_stack([(ll_i(th + h * np.eye(m_)[j]) - ll_i(th - h * np.eye(m_)[j])) / (2 * h) for j in range(m_)]); H = np.zeros((m_, m_))
for j in range(m_):
    for k2 in range(m_):
        e1, e2 = 1e-4 * np.eye(m_)[j], 1e-4 * np.eye(m_)[k2]; H[j, k2] = -(ll_i(th + e1 + e2).sum() - ll_i(th + e1 - e2).sum() - ll_i(th - e1 + e2).sum() + ll_i(th - e1 - e2).sum()) / (4e-8)
Sg = pd.DataFrame(S).groupby(T.participant_id.values).sum().values; G_, n_ = len(Sg), len(T); Vd = np.linalg.inv(H) @ (Sg.T @ Sg) @ np.linalg.inv(H) * G_ / (G_ - 1) * (n_ - 1) / (n_ - m_); q = stats.t.ppf(.975, G_ - 1)
Ld = {"A−C": np.array([0, 1, 0, 0.0]), "BASE−C": np.array([0, 0, 1, 0.0]), "A−BASE": np.array([0, 1, -1, 0.0])}
for k, l in Ld.items():
    est = float(l @ th); se = math.sqrt(float(l @ Vd @ l)); add(k, "pairs: Davidson model with ties, cluster-robust by participant", "answered comparisons (incl. ties)", len(T), math.exp(est), math.exp(est - q * se), math.exp(est + q * se), 2 * stats.t.sf(abs(est / se), G_ - 1), f"OR; tie parameter ν = {math.exp(th[-1]):.3f}; contrasts from the coefficient covariance")
pidT, prmT = T.participant_id.values, T.prompt_code.values; upT, uqT = np.unique(pidT), np.unique(prmT); ipT, iqT = np.searchsorted(upT, pidT), np.searchsorted(uqT, prmT); bd = []
for _ in range(N_BOOT):
    w = rng.multinomial(len(upT), np.ones(len(upT)) / len(upT))[ipT] * rng.multinomial(len(uqT), np.ones(len(uqT)) / len(uqT))[iqT]
    if w.sum() == 0: continue
    thb, *_ = dav_fit(T, w); bd.append([thb[1], thb[2], thb[1] - thb[2]])
bd = np.array(bd)
for j, k in enumerate(["A−C", "BASE−C", "A−BASE"]):
    add(k, "pairs: Davidson odds ratio, two-way (participant × prompt) pigeonhole bootstrap", "participants × prompts", f"{len(upT)} × {len(uqT)}", math.exp(float(Ld[k] @ th)), math.exp(float(np.percentile(bd[:, j], 2.5))), math.exp(float(np.percentile(bd[:, j], 97.5))), None, f"{len(bd)} replicates; weights in the likelihood; same replicates for the three contrasts")
# ---------------------------------------------------------------- pairs: exact binomial (marginal)
for k, (a, b) in CONTR.items():
    x = D[D.left_condition.isin([a, b]) & D.right_condition.isin([a, b])]; wins = int((x.winner_condition == a).sum()); n = len(x); bt_ = stats.binomtest(wins, n, 0.5); ci = bt_.proportion_ci(0.95, method="exact")
    add(k, "pairs: exact binomial on decisive choices (marginal)", "decisive comparisons of the pair", n, wins / n, ci.low, ci.high, bt_.pvalue, f"{wins}/{n} first condition chosen; Clopper–Pearson; assumes independent comparisons: does NOT account for repeated participants/prompts and does not replace the clustered inference")
TAB = pd.DataFrame(rows); TAB.to_csv(os.path.join(OUTI, "tabella3_completa.csv"), index=False)

# ---------------------------------------------------------------- operational definitions of the filters
excl_p = P[as_bool(P.excluded_from_analysis)]
sess = PS.groupby("participant_id").agg(modes=("mode", lambda s: ",".join(sorted(set(s)))), completed=("status", lambda s: int((s == "Completed").sum())), sessions=("session_id", "size"), answered=("answered_items", "sum"), items=("item_count", "sum"))
inc = sess.reindex(R.participant_id.unique())
defs = ["# Table 3 complete — operational definitions", "",
        "| term | definition from the export | count |", "|---|---|---|",
        f"| included phase-2 participant | has ≥ 1 rating with `excluded_from_analysis = false` (ratings) — same 158 ids have ≥ 1 answered comparison | {R.participant_id.nunique()} |",
        f"| global filter (export flag) | `participants.excluded_from_analysis = true`: every answer of the participant carries `excluded_from_analysis = true` in all tables (phase 1 included) | {len(excl_p)} participants; reasons: {excl_p.exclusion_reason.fillna('').value_counts().to_dict()} |",
        f"| 'incomplete phase 2' (manual reason) | reasons 'non finito' / 'non completo' / 'Non completato' / 'non termitano' typed by the researcher when excluding; the sessions table shows for those ids `status` ≠ Completed or `answered_items` < `item_count` in at least one phase-2 session | {int(excl_p.exclusion_reason.fillna('').str.lower().str.contains('fini|complet|termi').sum())} |",
        f"| automatic rule (platform) | reason 'Automatic rule: … faster than 501 ms, above the 20% limit' | {int(excl_p.exclusion_reason.fillna('').str.contains('Automatic').sum())} |",
        f"| analysis rule (this table) | participant-level contrasts require ≥ 3 ratings in each of the two conditions; no other exclusion added | 158 for every contrast |",
        f"| included participants with both phase-2 sessions Completed | from `posttraining_sessions.status` | {int((inc.completed >= 2).sum())} of {len(inc)} |", "",
        "Phase 1 is not re-filtered by these definitions: the phase-1 statistics of the manuscript use the 166/23,012 complete sample for selection and the 164/22,712 export-filtered perimeter for the secondary estimates (both reported in the audit).", "",
        "## Table", "", "| contrast | method | unit | n | estimate | 95% CI | p | note |", "|---|---|---|---|---|---|---|---|"]
for _, r in TAB.iterrows():
    f = lambda v: "" if v is None or (isinstance(v, float) and np.isnan(v)) else (f"{v:.4f}" if abs(v) < 10 else f"{v:.0f}")
    defs.append(f"| {r.contrast} | {r.method} | {r.unit} | {r.n} | {f(r.estimate)} | {f(r.ci_low)} / {f(r.ci_high)} | {'' if r.p is None or (isinstance(r.p, float) and np.isnan(r.p)) else f'{r.p:.4f}'} | {r.note} |")
open(os.path.join(OUTI, "report_tabella3.md"), "w", encoding="utf-8").write("\n".join(defs) + "\n"); log("done")
