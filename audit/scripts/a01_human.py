"""
Audit step 1 — human statistics (prompt sections 2 and 7).

Part A (reproduction): sample perimeters 166/164/161/159 and 599/600; participant-level contrasts; Bradley–Terry on decisive
choices (cluster-robust by participant); Davidson model with ties (independent implementation, cluster-robust and bootstrap);
half-point share; ICC; leave-one-rater-out reselection; linked vs unlinked; sensitivities to filters.
Part B (new, post-review): crossed random effects (participant + prompt×seed cell + image) for the ratings; two-way
(participant × prompt) pigeonhole bootstrap for the Davidson odds ratio; phase-1 statistics on the complete 166 sample.

Writes outputs/human_reproduction.csv, outputs/human_sensitivities.csv, outputs/report_human.md.
"""
import json
import math
import os
import time

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from scipy.optimize import minimize

from common import OUT, PREVIOUS_REPLY, SEED, Export, Log, as_bool, write_md

log = Log("a01_human")
E = Export()
rng = np.random.default_rng(SEED)
N_BOOT = 2000

# ------------------------------------------------------------------ data
R_all = E.csv("posttraining_ratings.csv")
T_all = E.csv("pairwise_trials.csv")
P = E.csv("participants.csv")
PR_all = E.csv("pretraining_ratings.csv")
PS = E.csv("posttraining_sessions.csv")
SI = E.csv("source_images.csv")
R = R_all[~as_bool(R_all.excluded_from_analysis)].copy()
T = T_all[~as_bool(T_all.excluded_from_analysis) & T_all.answered_at.notna()].copy()
PR = PR_all[~as_bool(PR_all.excluded_from_analysis)].copy()
for d in (R, T):
    d["trip"] = d.prompt_code + "_" + d.seed.astype(str)
D = T[T.selected_side != "Tie"].copy()
runs = E.csv("training_runs.csv").set_index("code")
A_ds = E.csv("aesthetic_dataset.csv"); C_ds = E.csv("control_dataset.csv")
AES = set(A_ds[A_ds.dataset_code == runs.training_dataset["RUN-AESTHETIC-4"]].image_code)
CTL = set(C_ds[C_ds.dataset_code == runs.training_dataset["RUN-CONTROL-4"]].image_code)
roles = P.set_index("participant_id").professional_role

rows, sens = [], []


def rep(section, quantity, reported, value, lo=None, hi=None, p=None, n=None, unit="", source="manuscript rev12", note=""):
    try:
        diff = None if reported is None or value is None else round(float(value) - float(reported), 6)
    except (TypeError, ValueError):
        diff = "see text"
    rows.append(dict(section=section, quantity=quantity, reported=reported, recomputed=value, difference=diff, ci_low=lo, ci_high=hi, p=p, n=n, unit=unit, reported_in=source, note=note))
    log(f"[{section}] {quantity}: reported {reported} | recomputed {value} | CI {lo} {hi} | p {p} | n {n} {note}")


def t1(x, mu=0.0):
    x = np.asarray(x, float); n = len(x); m = x.mean(); se = x.std(ddof=1) / math.sqrt(n); q = stats.t.ppf(.975, n - 1)
    return m, m - q * se, m + q * se, stats.ttest_1samp(x, mu).pvalue, n, se


# ------------------------------------------------------------------ A1 perimeters
rep("perimeters", "phase 1 participants (all recorded ratings)", 166, PR_all.participant_id.nunique(), n=len(PR_all), note="before the export filter")
rep("perimeters", "phase 1 ratings (all recorded)", 23012, len(PR_all))
rep("perimeters", "phase 1 participants after the export filter", 164, PR.participant_id.nunique())
rep("perimeters", "phase 1 ratings after the export filter", 22712, len(PR))
excl = PR_all[as_bool(PR_all.excluded_from_analysis)]
rep("perimeters", "phase 1 ratings removed by the filter", 300, len(excl), note=f"participants {excl.participant_id.nunique()}; reasons {P.set_index('participant_id').exclusion_reason.reindex(excl.participant_id.unique()).tolist()}")
n10 = (PR.groupby("participant_id").size() >= 10).sum()
rep("perimeters", "phase 1 participants with >= 10 ratings (consensus agreement n)", 161, int(n10))
per3 = [pid for pid, g in PR.groupby("participant_id") if (g.image_code.isin(AES).sum() >= 3) and (g.image_code.isin(CTL).sum() >= 3)]
rep("perimeters", "phase 1 participants with >= 3 ratings in each frozen set (LOO n)", 159, len(per3))
arch = set(roles[roles == "Architect"].index); non = set(roles[roles == "NonExpert"].index)
cov_role = PR[PR.participant_id.isin(arch)].image_code.nunique(), PR[PR.participant_id.isin(non)].image_code.nunique()
both = len(set(PR[PR.participant_id.isin(arch)].image_code) & set(PR[PR.participant_id.isin(non)].image_code))
rep("perimeters", "photographs rated by both architects and non-experts", 599, both, note=f"architects cover {cov_role[0]}, non-experts {cov_role[1]}")
exp_ = P.set_index("participant_id").architecture_expertise
hiX, loX = set(exp_[exp_ >= 4].index), set(exp_[exp_ <= 2].index)
rep("perimeters", "photographs rated by both high (4-5) and low (1-2) expertise", 600, len(set(PR[PR.participant_id.isin(hiX)].image_code) & set(PR[PR.participant_id.isin(loX)].image_code)))
rep("perimeters", "phase 2 participants (ratings, included)", 158, R.participant_id.nunique())
rep("perimeters", "phase 2 ratings (included)", 9413, len(R))
rep("perimeters", "phase 2 comparisons answered (included)", 4736, len(T)); rep("perimeters", "ties", 726, int((T.selected_side == "Tie").sum())); rep("perimeters", "decisive choices", 4010, len(D))
rep("perimeters", "ratings per image: min / max / mean", "15-22 / 19.7", f"{R.groupby('generated_image_id').size().min()}-{R.groupby('generated_image_id').size().max()} / {R.groupby('generated_image_id').size().mean():.1f}")
linked = set(P[as_bool(P.has_pre_training_session)].participant_id) & set(R.participant_id)
rep("perimeters", "phase 2 participants linked to phase 1 by id", 32, len(linked))
decl = P[P.participant_id.isin(set(R.participant_id) - linked)].prior_participation_self_report.fillna("blank").value_counts().to_dict()
rep("perimeters", "unlinked: declared Yes / No / NotSure", "16 / 99 / 11", f"{decl.get('Yes', 0)} / {decl.get('No', 0)} / {decl.get('NotSure', 0)}", note=f"all values {decl}")
# phase-1 selection rule: binding criterion
g1 = PR_all.groupby("image_code").score.agg(["count", "mean"])  # complete sample, as at the selection
sel = g1[(g1["count"] >= 10) & (g1["mean"] >= 5)]
rep("selection", "photographs with n>=10 and mean>=5 on the complete phase-1 sample", 89, len(sel), note=f"identical to frozen AESTHETIC: {set(sel.index) == AES}")
elig = g1[g1["count"] >= 10]["mean"]
for pct in (30, 33, 35, 40):
    cut = np.percentile(elig, 100 - pct)
    s_ = set(elig[(elig >= cut) & (elig >= 5)].index)
    rep("selection", f"rule with top {pct}%: cutoff mean / selected / equals frozen", "89", f"{cut:.3f} / {len(s_)} / {s_ == AES}", note="percentile cutoff below 5 → mean threshold binds" if cut < 5 else "PERCENTILE BINDS")
rep("selection", "share of the 600 selected by mean>=5 and n>=10", "14.8%", f"{100 * len(sel) / 600:.1f}%", source="review (g)")

# ------------------------------------------------------------------ A2 ratings
def pdiff(r, a, b, minn=3):
    c = r[r.condition_code.isin([a, b])].groupby(["participant_id", "condition_code"]).score.agg(["mean", "count"]).unstack()
    ok = (c["count"][a] >= minn) & (c["count"][b] >= minn)
    return (c["mean"][a] - c["mean"][b])[ok].dropna()


dac = pdiff(R, "AESTHETIC", "CONTROL")
m, lo, hi, p, n, se = t1(dac)
rep("ratings", "AESTHETIC − CONTROL per participant (points)", 0.104, round(m, 4), round(lo, 4), round(hi, 4), round(p, 5), n, note="one-sample t on participant mean differences; participants with >= 3 ratings in each condition")
dz = m / dac.std(ddof=1); q = stats.t.ppf(.975, n - 1)
rep("ratings", "d_z", 0.22, round(dz, 3), round(lo / dac.std(ddof=1), 3), round(hi / dac.std(ddof=1), 3))
for lab, (a, b), repv in (("BASE − CONTROL", ("BASE", "CONTROL"), 0.140), ("AESTHETIC − BASE", ("AESTHETIC", "BASE"), -0.036)):
    m_, lo_, hi_, p_, n_, _ = t1(pdiff(R, a, b)); rep("ratings", f"{lab} per participant", repv, round(m_, 4), round(lo_, 4), round(hi_, 4), round(p_, 6), n_)
R["c"] = R.score - R.groupby("participant_id").score.transform("mean")
tt = R[R.condition_code.isin(["AESTHETIC", "CONTROL"])].groupby(["trip", "condition_code"]).c.mean().unstack().dropna()
m_, lo_, hi_, p_, n_, _ = t1(tt.AESTHETIC - tt.CONTROL); rep("ratings", "AESTHETIC − CONTROL per triplet (participant-centred scores)", 0.105, round(m_, 4), round(lo_, 4), round(hi_, 4), round(p_, 5), n_)
# role / expertise
for lab, s_, repv in (("architects", arch, 0.102), ("non-experts", non, 0.056)):
    x = dac[dac.index.isin(s_)]; m_, lo_, hi_, p_, n_, _ = t1(x); rep("ratings", f"A−C in {lab}", repv, round(m_, 4), round(lo_, 4), round(hi_, 4), round(p_, 4), n_)
w = stats.ttest_ind(dac[dac.index.isin(arch)], dac[dac.index.isin(non)], equal_var=False)
rep("ratings", "architects − non-experts difference (p)", 0.623, round(float(w.pvalue), 3), note=f"difference {dac[dac.index.isin(arch)].mean() - dac[dac.index.isin(non)].mean():+.3f}")
w = stats.ttest_ind(dac[dac.index.isin(hiX)], dac[dac.index.isin(loX)], equal_var=False); rep("ratings", "high − low expertise (p)", 0.717, round(float(w.pvalue), 3))
only2 = set(R.participant_id) - linked - set(P[P.prior_participation_self_report == "Yes"].participant_id)
w = stats.ttest_ind(dac[dac.index.isin(linked)], dac[dac.index.isin(only2)], equal_var=False); ci = w.confidence_interval(.95)
rep("ratings", "linked − unlinked (No + NotSure) A−C", -0.116, round(dac[dac.index.isin(linked)].mean() - dac[dac.index.isin(only2)].mean(), 4), round(ci.low, 4), round(ci.high, 4), round(float(w.pvalue), 3), f"{dac.index.isin(linked).sum()}+{dac.index.isin(only2).sum()}",
    note="Welch; the interval spans −0.29/+0.06: not a demonstration of equivalence (MDE for this comparison ≈ ±0.25 points)")

# ------------------------------------------------------------------ A3 pairwise
def pair(df, a, b): return df[df.left_condition.isin([a, b]) & df.right_condition.isin([a, b])]


x = pair(D, "AESTHETIC", "CONTROL")
rep("pairs", "AESTHETIC chosen in decisive A–C comparisons (share, n)", "51.3% of 1320", f"{100 * (x.winner_condition == 'AESTHETIC').mean():.1f}% of {len(x)}")
xt = pair(T, "AESTHETIC", "CONTROL"); half = xt.winner_condition.map({"AESTHETIC": 1.0, "CONTROL": 0.0}).fillna(0.5).groupby(xt.participant_id).mean()
m_, lo_, hi_, p_, n_, _ = t1(half, .5); rep("pairs", "half-point share A vs C per participant", None, round(m_, 4), round(lo_, 4), round(hi_, 4), round(p_, 3), n_, source="previous reply 8", note="t interval over participants; previous reply gave a participant bootstrap 48.69–53.52")


def bt(df, ref, groups):
    others = [c for c in ["AESTHETIC", "CONTROL", "BASE"] if c != ref]
    X = pd.DataFrame({"const": 1.0, **{c: (df.left_condition == c).astype(float) - (df.right_condition == c).astype(float) for c in others}})
    r = sm.GLM((df.selected_side == "Left").astype(float), X, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": groups})
    g = len(np.unique(groups)); q = stats.t.ppf(.975, g - 1)
    return {c: (math.exp(r.params[c]), math.exp(r.params[c] - q * r.bse[c]), math.exp(r.params[c] + q * r.bse[c]), 2 * stats.t.sf(abs(r.params[c] / r.bse[c]), g - 1)) for c in X.columns}


b = bt(D, "CONTROL", D.participant_id.values)
rep("pairs", "Bradley–Terry OR A vs C (cluster participant)", 1.090, *[round(v, 4) for v in b["AESTHETIC"]], n=len(D), note="logistic regression on 'left wins', intercept = position bias; ties excluded")
rep("pairs", "Bradley–Terry OR BASE vs C", 1.133, *[round(v, 4) for v in b["BASE"]])
rep("pairs", "Bradley–Terry OR A vs BASE", 0.962, *[round(v, 4) for v in bt(D, "BASE", D.participant_id.values)["AESTHETIC"]])
rep("pairs", "position bias OR (left)", None, *[round(v, 4) for v in b["const"]], note="not in the manuscript")
bp = bt(D, "CONTROL", D.prompt_code.values)
rep("pairs", "Bradley–Terry OR A vs C, clustered by PROMPT (48 clusters)", None, *[round(v, 4) for v in bp["AESTHETIC"]], note="sensitivity: inference about prompts rather than participants")


# Davidson model: P(i beats j) ∝ e^θi, P(j beats i) ∝ e^θj, P(tie) ∝ ν e^{(θi+θj)/2}; here parametrised with left/right and position bias
def davidson_fit(df, ref="CONTROL", weights=None):
    others = [c for c in ["AESTHETIC", "CONTROL", "BASE"] if c != ref]
    X = np.column_stack([np.ones(len(df))] + [(df.left_condition == c).astype(float).values - (df.right_condition == c).astype(float).values for c in others])
    y = df.selected_side.map({"Left": 1, "Right": 0, "Tie": 2}).values
    wts = np.ones(len(df)) if weights is None else np.asarray(weights, float)
    idx = np.arange(len(df))

    def ll_i(th):
        eta = X @ th[:-1]
        W = np.column_stack([np.zeros(len(df)), eta, th[-1] + eta / 2])
        mx = W.max(1, keepdims=True)
        return W[idx, y] - (mx[:, 0] + np.log(np.exp(W - mx).sum(1)))

    def grad(th):
        eta = X @ th[:-1]
        W = np.column_stack([np.zeros(len(df)), eta, th[-1] + eta / 2]); W -= W.max(1, keepdims=True)
        Pm = np.exp(W); Pm /= Pm.sum(1, keepdims=True)
        # d ll / d eta = 1[y=left] + 0.5·1[y=tie] − P(left) − 0.5 P(tie); d ll / d nu = 1[y=tie] − P(tie)
        de = (y == 1) + 0.5 * (y == 2) - Pm[:, 1] - 0.5 * Pm[:, 2]
        dn = (y == 2) - Pm[:, 2]
        return -np.concatenate([X.T @ (wts * de), [np.sum(wts * dn)]])

    r = minimize(lambda th: -np.sum(wts * ll_i(th)), np.zeros(X.shape[1] + 1), jac=grad, method="BFGS", options={"gtol": 1e-7, "maxiter": 2000})
    names = ["position"] + others + ["log_nu"]
    return dict(zip(names, r.x)), r, ll_i, X, y


def davidson_cluster_ci(df, groups):
    th, r, ll_i, X, y = davidson_fit(df)
    thv = np.array(list(th.values())); m = len(thv); h = 1e-5
    S = np.column_stack([(ll_i(thv + h * np.eye(m)[j]) - ll_i(thv - h * np.eye(m)[j])) / (2 * h) for j in range(m)])
    H = np.zeros((m, m))
    for j in range(m):
        for k in range(m):
            e1, e2 = 1e-4 * np.eye(m)[j], 1e-4 * np.eye(m)[k]
            H[j, k] = -(ll_i(thv + e1 + e2).sum() - ll_i(thv + e1 - e2).sum() - ll_i(thv - e1 + e2).sum() + ll_i(thv - e1 - e2).sum()) / (4 * 1e-8)
    Sg = pd.DataFrame(S).groupby(np.asarray(groups)).sum().values; G, n = len(Sg), len(df)
    V = np.linalg.inv(H) @ (Sg.T @ Sg) @ np.linalg.inv(H) * G / (G - 1) * (n - 1) / (n - m)
    se = np.sqrt(np.diag(V)); q = stats.t.ppf(.975, G - 1)
    return {k: (v, v - q * s, v + q * s, 2 * stats.t.sf(abs(v / s), G - 1)) for (k, v), s in zip(th.items(), se)}, r


dv, r_fit = davidson_cluster_ci(T, T.participant_id.values)
prev = pd.read_csv(os.path.join(PREVIOUS_REPLY, "14_pairwise_new_sensitivity.csv"))
rep("pairs", "Davidson OR A vs C (all 4736 answers incl. ties)", round(float(prev.odds_ratio.iloc[0]), 4), round(math.exp(dv["AESTHETIC"][0]), 4), round(math.exp(dv["AESTHETIC"][1]), 4), round(math.exp(dv["AESTHETIC"][2]), 4), round(dv["AESTHETIC"][3], 4), len(T), source="previous reply (Davidson, point estimate)",
    note=f"independent MLE (analytic gradient, BFGS, converged={r_fit.success}, logLik={-r_fit.fun:.3f}); interval here cluster-robust by participant with t(157); previous reply: participant bootstrap {prev.ci_low.iloc[0]:.3f}-{prev.ci_high.iloc[0]:.3f}")
rep("pairs", "Davidson OR BASE vs C", round(float(prev.odds_ratio.iloc[2]), 4), round(math.exp(dv["BASE"][0]), 4), round(math.exp(dv["BASE"][1]), 4), round(math.exp(dv["BASE"][2]), 4), round(dv["BASE"][3], 4), source="previous reply")
rep("pairs", "Davidson OR A vs BASE", round(float(prev.odds_ratio.iloc[1]), 4), round(math.exp(dv["AESTHETIC"][0] - dv["BASE"][0]), 4), source="previous reply", note="derived from the two parameters (BASE reference)")
rep("pairs", "Davidson tie parameter nu", round(float(prev.nu.iloc[0]), 4), round(math.exp(dv["log_nu"][0]), 4), note=f"tie probability at parity nu/(2+nu) = {math.exp(dv['log_nu'][0]) / (2 + math.exp(dv['log_nu'][0])):.3f}; observed tie share {(T.selected_side == 'Tie').mean():.3f}")

# ------------------------------------------------------------------ A4 ICC and LOO
def icc(df, item, rater, score):
    """One-way random-effects ANOVA ICC on participant-centred scores, unbalanced design (k0 = mean effective group size).
    ICC(1) = (MSB − MSW)/(MSB + (k0 − 1) MSW); ICC(k) = (MSB − MSW)/MSB. Degrees of freedom of MSW reduced by the centring."""
    g = df.groupby(item)[score].agg(["mean", "count", "var"]); g = g[g["count"] >= 2]; x = df[df[item].isin(g.index)]
    a, N, grand = len(g), g["count"].sum(), x[score].mean()
    msb = (g["count"] * (g["mean"] - grand) ** 2).sum() / (a - 1)
    msw = (g["var"] * (g["count"] - 1)).sum() / (N - a - (df[rater].nunique() - 1))
    k0 = (N - (g["count"] ** 2).sum() / N) / (a - 1)
    return (msb - msw) / (msb + (k0 - 1) * msw), (msb - msw) / msb, a, k0


i1, ik, a_, k0 = icc(R, "generated_image_id", "participant_id", "c")
rep("reliability", "phase 2 ICC(1) single rating", 0.239, round(i1, 3), n=a_, note=f"one-way ANOVA on participant-centred scores; k0={k0:.2f}; ICC(k)={ik:.3f}")
rep("reliability", "phase 2 ICC(k) image mean", 0.861, round(ik, 3))
PR["c"] = PR.score - PR.groupby("participant_id").score.transform("mean")
i1, ik, a_, k0 = icc(PR, "image_asset_id", "participant_id", "c")
rep("reliability", "phase 1 ICC(1) (export filter, 164)", 0.138, round(i1, 3), n=a_, note=f"k0={k0:.2f}")
rep("reliability", "phase 1 ICC(k) (export filter)", 0.858, round(ik, 3))
PR_all["c"] = PR_all.score - PR_all.groupby("participant_id").score.transform("mean")
i1c, ikc, a_, k0 = icc(PR_all, "image_asset_id", "participant_id", "c")
sens.append(dict(analysis="phase 1 ICC on the COMPLETE sample (166, 23012)", estimate=round(i1c, 3), note=f"ICC(k)={ikc:.3f}; export-filter values 0.138/0.858"))
tot = PR.groupby("image_code").score.agg(["sum", "count"])
x = PR.join(tot, on="image_code"); x = x[x["count"] > 1].assign(loo=lambda z: (z["sum"] - z.score) / (z["count"] - 1))
rs = [g.score.corr(g.loo) for _, g in x.groupby("participant_id") if len(g) >= 10]; rs = [v for v in rs if not math.isnan(v)]
m_, lo_, hi_, _, n_, _ = t1(rs); rep("reliability", "mean correlation with the aggregate of the others", 0.351, round(m_, 3), round(lo_, 3), round(hi_, 3), n=n_)


def loo_signal(PRx, min_each=3):
    """Leave-one-rater-out reselection: drop the rater, reselect the top-|AES| photographs by the others' means (active photographs,
    ties broken by asset id), evaluate with the rater's own scores: mean(own on reselected top) − mean(own on CONTROL \\ top)."""
    totx = PRx.groupby("image_code").score.agg(["sum", "count"])
    active = set(SI[as_bool(SI.is_active)].image_code); ids = SI.set_index("image_code").image_asset_id
    out, checks = [], dict(top_size_ok=0, control_overlap=[])
    for _, g in PRx.groupby("participant_id"):
        own = g.set_index("image_code").score
        t_ = totx[totx.index.isin(active)].copy(); mean = t_["sum"] / t_["count"]
        idx = own.index.intersection(t_.index)
        mean.loc[idx] = np.where(t_.loc[idx, "count"] > 1, (t_.loc[idx, "sum"] - own.loc[idx]) / (t_.loc[idx, "count"] - 1).replace(0, np.nan), np.nan)
        order = pd.DataFrame({"m": mean.dropna()}); order["id"] = ids.reindex(order.index).values
        top = set(order.sort_values(["m", "id"], ascending=[False, True]).index[:len(AES)])
        checks["top_size_ok"] += len(top) == len(AES); checks["control_overlap"].append(len(top & CTL))
        a_, c_ = own[own.index.isin(top)], own[own.index.isin(CTL - top)]
        if len(a_) >= min_each and len(c_) >= min_each: out.append(a_.mean() - c_.mean())
    return out, checks


loo, chk_ = loo_signal(PR)
m_, lo_, hi_, _, n_, _ = t1(loo)
rep("reliability", "leave-one-rater-out reselection signal (points)", 0.915, round(m_, 3), round(lo_, 3), round(hi_, 3), n=n_,
    note=f"inside each reselection: top set always 89 ({chk_['top_size_ok']} of {PR.participant_id.nunique()}), CONTROL photographs entering the reselected top: mean {np.mean(chk_['control_overlap']):.1f} (removed from the comparison set). NOTE the reselection uses the top-89 by mean, not the frozen rule (n>=10, mean>=5)")
loo_c, _ = loo_signal(PR_all); m_, lo_, hi_, _, n_, _ = t1(loo_c)
sens.append(dict(analysis="LOO reselection signal on the COMPLETE phase-1 sample (166)", estimate=round(m_, 3), ci_low=round(lo_, 3), ci_high=round(hi_, 3), n=n_, note="separate sensitivity; the manuscript value 0.915 uses the export filter"))
# dataset means on the complete sample
g_all = PR_all.groupby("image_code").score.agg(["mean", "std"])
rep("phase1", "AESTHETIC photographs mean of means (complete sample)", 5.295, round(g_all.loc[list(AES), "mean"].mean(), 3)); rep("phase1", "CONTROL photographs mean of means", 4.211, round(g_all.loc[list(CTL), "mean"].mean(), 3))
rep("phase1", "mean within-photo SD AESTHETIC / CONTROL", "1.444 / 1.556", f"{g_all.loc[list(AES), 'std'].mean():.3f} / {g_all.loc[list(CTL), 'std'].mean():.3f}")
ra = PR[PR.participant_id.isin(arch)].groupby("image_code").score.mean(); rn = PR[PR.participant_id.isin(non)].groupby("image_code").score.mean(); j = ra.index.intersection(rn.index)
rep("phase1", "Spearman architects vs non-experts (photograph means)", 0.425, round(stats.spearmanr(ra[j], rn[j]).statistic, 3), n=len(j), note="export-filter sample")
rh = PR[PR.participant_id.isin(hiX)].groupby("image_code").score.mean(); rl = PR[PR.participant_id.isin(loX)].groupby("image_code").score.mean(); j = rh.index.intersection(rl.index)
rep("phase1", "Spearman high vs low expertise", 0.496, round(stats.spearmanr(rh[j], rl[j]).statistic, 3), n=len(j))
rep("phase1", "role counts NonExpert/Architect/Student/Engineer/other", "63/58/8/8/29", str(roles.reindex(PR_all.participant_id.unique()).value_counts().to_dict()))

# ------------------------------------------------------------------ A5 filters (phase 2)
R_noex = R_all[R_all.participant_id.isin(P.participant_id)].copy()
for lab, df_, minn in (("without global participant exclusions, >=3 per condition", R_noex, 3), ("without global exclusions, >=1 per condition", R_noex, 1), ("included sample, >=1 per condition", R, 1)):
    x = pdiff(df_, "AESTHETIC", "CONTROL", minn); m_, lo_, hi_, p_, n_, _ = t1(x)
    sens.append(dict(analysis=f"A−C ratings: {lab}", estimate=round(m_, 4), ci_low=round(lo_, 4), ci_high=round(hi_, 4), p=round(p_, 4), n=n_))
fast = R[R.response_time_ms >= 500]; x = pdiff(fast, "AESTHETIC", "CONTROL"); m_, lo_, hi_, p_, n_, _ = t1(x)
sens.append(dict(analysis="A−C ratings: responses < 500 ms removed", estimate=round(m_, 4), ci_low=round(lo_, 4), ci_high=round(hi_, 4), p=round(p_, 4), n=n_, note=f"{int((R.response_time_ms < 500).sum())} ratings removed"))
fast = R[R.response_time_ms >= 1000]; x = pdiff(fast, "AESTHETIC", "CONTROL"); m_, lo_, hi_, p_, n_, _ = t1(x)
sens.append(dict(analysis="A−C ratings: responses < 1000 ms removed", estimate=round(m_, 4), ci_low=round(lo_, 4), ci_high=round(hi_, 4), p=round(p_, 4), n=n_, note=f"{int((R.response_time_ms < 1000).sum())} ratings removed"))
excluded_p = P[as_bool(P.excluded_from_analysis)]
sens.append(dict(analysis="phase 2 participants globally excluded", estimate=len(excluded_p), note=f"reasons: {excluded_p.exclusion_reason.value_counts().to_dict()}; with phase-2 answers: {int(excluded_p.participant_id.isin(R_all.participant_id).sum())}"))
cmp_sessions = PS.groupby("participant_id").agg(n_sessions=("session_id", "size"), completed=("status", lambda s: (s == "Completed").sum()))
sens.append(dict(analysis="phase 2 included participants with both sessions Completed", estimate=int((cmp_sessions.reindex(R.participant_id.unique()).completed == 2).sum()), n=R.participant_id.nunique()))

# ------------------------------------------------------------------ B1 crossed random effects for the ratings
t0 = time.time()
Rm = R[R.condition_code.isin(["AESTHETIC", "CONTROL", "BASE"])].copy()
Rm["cond"] = pd.Categorical(Rm.condition_code, ["CONTROL", "AESTHETIC", "BASE"])
Rm["one"] = 1
md = sm.MixedLM.from_formula("score ~ C(cond)", groups="one", re_formula="0", vc_formula={"participant": "0 + C(participant_id)", "cell": "0 + C(trip)", "image": "0 + C(generated_image_id)"}, data=Rm)
try:
    mf = md.fit(reml=True, method="lbfgs", maxiter=500)
    ok = mf.converged
except Exception as ex:  # noqa
    mf, ok = None, False
    log("MixedLM failed", ex)
if mf is not None:
    ca = mf.params["C(cond)[T.AESTHETIC]"]; sa = mf.bse["C(cond)[T.AESTHETIC]"]
    cb = mf.params["C(cond)[T.BASE]"]; sb = mf.bse["C(cond)[T.BASE]"]
    sens.append(dict(analysis="A−C ratings: linear mixed model with crossed random intercepts participant + prompt×seed cell + image (REML)", estimate=round(ca, 4), ci_low=round(ca - 1.96 * sa, 4), ci_high=round(ca + 1.96 * sa, 4),
                     p=round(2 * stats.norm.sf(abs(ca / sa)), 4), n=len(Rm), note=f"converged={ok}; variance components {json.dumps({k: round(float(v), 4) for k, v in zip(mf.model.exog_vc.names, mf.vcomp)})} (labels from the model, corrected 2026-10-03 second pass); residual {mf.scale:.4f}; fit {time.time() - t0:.0f}s"))
    sens.append(dict(analysis="BASE−C ratings: same crossed model", estimate=round(cb, 4), ci_low=round(cb - 1.96 * sb, 4), ci_high=round(cb + 1.96 * sb, 4), p=round(2 * stats.norm.sf(abs(cb / sb)), 4)))
    sens.append(dict(analysis="A−BASE ratings: same crossed model", estimate=round(ca - cb, 4), note="difference of the two fixed effects; SE not reported here"))
    log(mf.summary())

# ------------------------------------------------------------------ B2 bootstraps for the Davidson OR: participant, prompt, two-way pigeonhole
pid = T.participant_id.values; prm = T.prompt_code.values
up, uq = np.unique(pid), np.unique(prm)
ip, iq = np.searchsorted(up, pid), np.searchsorted(uq, prm)


def boot(kind, B=N_BOOT):
    out = []
    for _ in range(B):
        wp = rng.multinomial(len(up), np.ones(len(up)) / len(up)) if kind in ("participant", "two-way") else np.ones(len(up))
        wq = rng.multinomial(len(uq), np.ones(len(uq)) / len(uq)) if kind in ("prompt", "two-way") else np.ones(len(uq))
        w = wp[ip] * wq[iq]
        if w.sum() == 0: continue
        th, r, *_ = davidson_fit(T, weights=w)
        out.append([th["AESTHETIC"], th["BASE"], th["AESTHETIC"] - th["BASE"]])
    return np.array(out)


est = dv["AESTHETIC"][0], dv["BASE"][0], dv["AESTHETIC"][0] - dv["BASE"][0]
for kind in ("participant", "prompt", "two-way"):
    t0 = time.time(); bb = boot(kind)
    for j, lab in enumerate(["A vs C", "BASE vs C", "A vs BASE"]):
        lo_, hi_ = np.percentile(bb[:, j], [2.5, 97.5])
        sens.append(dict(analysis=f"Davidson OR {lab}: {kind} bootstrap ({len(bb)} resamples)", estimate=round(math.exp(est[j]), 4), ci_low=round(math.exp(lo_), 4), ci_high=round(math.exp(hi_), 4),
                         n=f"{len(up)} participants × {len(uq)} prompts", note="pigeonhole (two-way cluster) bootstrap: participants and prompts resampled independently, observation weight = product of multiplicities (Owen 2007; Owen & Eckles 2012)" if kind == "two-way" else f"cluster bootstrap over {kind}s, percentile interval"))
    log(kind, "bootstrap", f"{time.time() - t0:.0f}s")
# two-way for the ratings contrast too (participant × prompt), statistic = mean of participant mean differences weighted
dd = R[R.condition_code.isin(["AESTHETIC", "CONTROL"])]
pid2, prm2 = dd.participant_id.values, dd.prompt_code.values
up2, uq2 = np.unique(pid2), np.unique(prm2); ip2, iq2 = np.searchsorted(up2, pid2), np.searchsorted(uq2, prm2)
isA = (dd.condition_code == "AESTHETIC").values.astype(float); sc = dd.score.values
bs, bs_wrong, dropped = [], [], []
for _ in range(N_BOOT):
    wp2 = rng.multinomial(len(up2), np.ones(len(up2)) / len(up2)); wq2 = rng.multinomial(len(uq2), np.ones(len(uq2)) / len(uq2))
    w = wp2[ip2] * wq2[iq2]
    df_ = pd.DataFrame({"p": pid2, "a": isA, "s": sc, "w": w}); df_ = df_[df_.w > 0]
    # within a participant the participant multiplicity is constant and cancels in the weighted mean: only the prompt weights act here
    ma = df_[df_.a == 1].groupby("p").apply(lambda g: np.average(g.s, weights=g.w), include_groups=False); mc = df_[df_.a == 0].groupby("p").apply(lambda g: np.average(g.s, weights=g.w), include_groups=False)
    d_ = (ma - mc).dropna()
    if len(d_):
        mult = wp2[np.searchsorted(up2, d_.index.to_numpy())]           # participant multiplicities of the ids present
        bs.append(float(np.average(d_.to_numpy(), weights=mult)))         # CORRECTED (2026-10-03, second pass): outer mean keeps the drawn multiplicities
        bs_wrong.append(float(d_.mean()))                                 # first-pass estimator (every drawn id counted once) kept for the record
        dropped.append(int(len(set(up2[wp2 > 0])) - len(d_)))            # drawn participants without both A and C observations in the resample
lo_, hi_ = np.percentile(bs, [2.5, 97.5]); lo_w, hi_w = np.percentile(bs_wrong, [2.5, 97.5])
sens.append(dict(analysis="A−C ratings per participant: two-way (participant × prompt) pigeonhole bootstrap (corrected: outer mean weighted by participant multiplicity)", estimate=round(m, 4), ci_low=round(lo_, 4), ci_high=round(hi_, 4), n=len(bs),
                 note=f"participants and prompts resampled independently; within-participant means weighted by prompt multiplicity; outer mean weighted by participant multiplicity; drawn participants lacking A or C after resampling are dropped (mean {np.mean(dropped):.2f} per resample). First-pass estimator (ids counted once, superseded): {lo_w:+.4f} / {hi_w:+.4f}. Compare with the t interval +0.029/+0.178"))

# ------------------------------------------------------------------ write
pd.DataFrame(rows).to_csv(os.path.join(OUT, "human_reproduction.csv"), index=False)
pd.DataFrame(sens).to_csv(os.path.join(OUT, "human_sensitivities.csv"), index=False)
L = ["# Human statistics — reproduction and sensitivities (audit rev12)", "",
     "Independent recomputation from the export (SHA256 ea0bdbf6…). Reported values come from the manuscript revision 12 unless stated. "
     "Inference unit: participants, unless the row says prompt or two-way. The human data concern ONLY the two original adapters (training seeds 1254/9865); no model of repeated judgements creates training replications.", "",
     "## Reproduction", "", "| section | quantity | reported | recomputed | 95% CI | p | n | note |", "|---|---|---|---|---|---|---|---|"]
for r_ in rows:
    ci = "" if r_["ci_low"] is None else f"{r_['ci_low']} / {r_['ci_high']}"
    L.append(f"| {r_['section']} | {r_['quantity']} | {r_['reported']} | {r_['recomputed']} | {ci} | {'' if r_['p'] is None else r_['p']} | {'' if r_['n'] is None else r_['n']} | {r_['note']} |")
L += ["", "## Sensitivities (post-review, exploratory)", "", "| analysis | estimate | 95% CI | p | n | note |", "|---|---|---|---|---|---|"]
for s_ in sens:
    ci = "" if s_.get("ci_low") is None else f"{s_['ci_low']} / {s_['ci_high']}"
    L.append(f"| {s_['analysis']} | {s_['estimate']} | {ci} | {s_.get('p', '')} | {s_.get('n', '')} | {s_.get('note', '')} |")
L += ["", "## Definitions", "",
      "- Participant-level contrast: mean of a participant's ratings of condition A minus mean of condition B, participants with at least 3 ratings in each; one-sample t with t(n−1) interval.",
      "- Bradley–Terry: logistic regression of 'left image wins' on condition indicators (left − right), intercept = left-position bias; decisive choices only; cluster-robust SE by participant, t(G−1).",
      "- Davidson (1970): outcomes left/right/tie with weights e^{η}, 1, ν·e^{η/2} where η = position bias + θ_left − θ_right; θ_CONTROL = 0; MLE with analytic gradient. Cluster-robust interval by participant and three bootstraps (participant, prompt, two-way pigeonhole).",
      "- ICC: one-way random-effects ANOVA on participant-centred scores with the unbalanced-design mean group size k0; degrees of freedom of the within term reduced by the number of centring constants. The design is incomplete (each rater sees a subset); this estimator treats raters as a nuisance removed by centring, not as a crossed factor.",
      "- Leave-one-rater-out: see `loo_signal` — the reselection is the top-89 by the others' means (not the frozen rule with n ≥ 10 and mean ≥ 5), evaluated with the rater's own scores on the reselected top versus the frozen CONTROL photographs not in that top.",
      "- Crossed mixed model: score ~ condition + (1|participant) + (1|prompt×seed cell) + (1|image), REML, statsmodels MixedLM with variance components on a single group.", ""]
write_md("report_human.md", L)
log("done")
