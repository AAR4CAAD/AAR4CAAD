"""
Analysis of the controlled-caption experiment (PROTOCOLLO_CAPTION_CONTROLLATE.md §4). Written and tested BEFORE any neutral
adapter exists; the test uses `--dry-run`, which feeds the existing paired-seed adapters as if they were the neutral regime so
that every code path runs (its numbers are meaningless and are written to outputs/caption_control_DRYRUN_*.csv only).

    python a10_caption_control_analysis.py <export.zip with the NEU-* runs> [--dry-run]

Inputs when real: the export containing the six NEU-* runs and their 1152 generated images; their DINOv2 embeddings in
metrics/embeddings_neutral_dinov2_vitb14.npz (same pipeline as the replication file) and their descriptors appended to
metrics/covariates_images.csv by image_scripts/covariates.py. Frozen direction: baseline/direction_dinov2.npz.
Outputs: caption_control_results.csv (per seed and pooled, three quantities kept separate: estimate in the neutral regime,
its uncertainty, paired per-cell difference between regimes), caption_control_descriptors.csv, report_caption_control.md.
Decision categories (fixed in the protocol): maintained / reduced / not distinguishable from zero / inconclusive — never
"lost" or "necessary captions" from a non-significant result alone.
"""
import argparse
import os

import numpy as np
import pandas as pd

from common import ANALYSIS, DESCRIPTORS, EXPORT_REP_ZIP, OUT, REPLICATION_EXCLUDED, SEED, Export, Log, descriptor_matrix, write_md

ap = argparse.ArgumentParser(); ap.add_argument("export", nargs="?", default=EXPORT_REP_ZIP); ap.add_argument("--dry-run", action="store_true"); args = ap.parse_args()
log = Log("a10_caption_control_analysis"); rng = np.random.default_rng(SEED); N_BOOT = 5000
E = Export(args.export); tag = "DRYRUN_" if args.dry_run else ""


def unit(x): return x / np.linalg.norm(x, axis=-1, keepdims=True)


D = np.load(os.path.join(ANALYSIS, "baseline", "direction_dinov2.npz"), allow_pickle=False); u = D["cls_v"]; d = float(D["cls_gap"])
files = [os.path.join(ANALYSIS, "metrics", "embeddings_dinov2_vitb14.npz"), os.path.join(ANALYSIS, "metrics", "embeddings_replication_dinov2_vitb14.npz")]
neu_file = os.path.join(ANALYSIS, "metrics", "embeddings_neutral_dinov2_vitb14.npz")
if os.path.exists(neu_file): files.append(neu_file)
elif not args.dry_run: raise SystemExit("neutral embeddings missing: run the extraction pipeline first (see protocol §5)")
emb = {}
for f in files:
    z = np.load(f, allow_pickle=False); emb.update({i: v for i, v in zip(z["id"], unit(z["cls"].astype(np.float64)))})
G = E.csv("generated_images.csv"); G["o"] = G.opaque_id.str.replace("-", "").str.lower(); G["cell"] = G.prompt_code + "_" + G.seed.astype(str)
runs = E.csv("training_runs.csv").set_index("code")
cells = sorted(G[G.condition_code == "BASE"].cell.unique()); prompt_of = np.array([c.rsplit("_", 1)[0] for c in cells]); qs = np.unique(prompt_of); W = np.array([(prompt_of == q).sum() for q in qs])


def mat(run=None, cond=None):
    s = G[G.training_run == run] if run else G[(G.condition_code == cond) & (G.generation_plan_id.isin(G[G.training_run.isin(["RUN-AESTHETIC-4", "RUN-CONTROL-4"])].generation_plan_id))]
    o = s.drop_duplicates("cell").set_index("cell").o.reindex(cells); assert o.notna().all(), run
    return np.stack([emb[i] for i in o])


def regime(prefix_a, prefix_c, originals=None):
    out = {}
    for code in runs.index:
        if originals and code in originals: out[originals[code]] = mat(code); continue
        if code.startswith(prefix_a) and code not in REPLICATION_EXCLUDED: out[("AESTHETIC", int(runs.seed[code]))] = mat(code)
        if code.startswith(prefix_c): out[("CONTROL", int(runs.seed[code]))] = mat(code)
    return out


orig = regime("REP-AES", "REP-CTL", {"RUN-AESTHETIC-4": ("AESTHETIC", 1254), "RUN-CONTROL-4": ("CONTROL", 9865)})
neu = regime("REP-AES", "REP-CTL", {"RUN-AESTHETIC-4": ("AESTHETIC", 1254), "RUN-CONTROL-4": ("CONTROL", 9865)}) if args.dry_run else regime("NEU-AES", "NEU-CTL")
seeds = sorted({s for _, s in orig}); assert all((c, s) in neu for c in ("AESTHETIC", "CONTROL") for s in seeds), "neutral regime incomplete"


def boot(v):
    means = np.array([v[prompt_of == q].mean() for q in qs]); i = rng.integers(0, len(qs), (N_BOOT, len(qs))); b = (means[i] * W[i]).sum(1) / W[i].sum(1)
    return float(v.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5)), float(2 * min((b <= 0).mean(), (b >= 0).mean()))


rows = []
Pn, Po = {}, {}
for s in seeds:
    Pn[s] = (neu[("AESTHETIC", s)] - neu[("CONTROL", s)]) @ u; Po[s] = (orig[("AESTHETIC", s)] - orig[("CONTROL", s)]) @ u
    for lab, v in (("neutral regime: P_s", Pn[s]), ("original regime: P_s", Po[s]), ("paired difference original − neutral", Po[s] - Pn[s])):
        m, lo, hi, p = boot(v); rows.append(dict(seed=s, quantity=lab, estimate=m, ci_low=lo, ci_high=hi, p_boot=p, R=m / d if "P_s" in lab else None))
pooled_n = np.mean([Pn[s] for s in seeds], 0); pooled_o = np.mean([Po[s] for s in seeds], 0)
for lab, v in (("neutral regime: mean of the three seeds", pooled_n), ("original regime: mean of the three seeds", pooled_o), ("paired difference, mean of the three seeds", pooled_o - pooled_n)):
    m, lo, hi, p = boot(v); rows.append(dict(seed="pooled", quantity=lab, estimate=m, ci_low=lo, ci_high=hi, p_boot=p, R=m / d if "regime" in lab else None))
Rz = pd.DataFrame(rows); Rz.to_csv(os.path.join(OUT, f"caption_control_{tag}results.csv"), index=False)
# categories (protocol §4, revised): based on the neutral estimate AND its interval AND the paired difference
pn = Rz[(Rz.seed == "pooled") & (Rz.quantity.str.startswith("neutral"))].iloc[0]; pdiff = Rz[(Rz.seed == "pooled") & (Rz.quantity.str.startswith("paired"))].iloc[0]
all_pos = all(Rz[(Rz.seed == s) & (Rz.quantity.str.startswith("neutral"))].ci_low.iloc[0] > 0 for s in seeds)
if pn.ci_low > 0 and pdiff.ci_low <= 0 <= pdiff.ci_high: cat = "maintained (neutral contrast > 0; difference between regimes not distinguishable from zero)"
elif pn.ci_low > 0 and pdiff.ci_low > 0: cat = "reduced (neutral contrast > 0 but smaller than the original, difference > 0)"
elif pn.ci_low <= 0 <= pn.ci_high and pdiff.ci_low > 0: cat = "not distinguishable from zero under common captions, and smaller than the original (difference > 0)"
elif pn.ci_low <= 0 <= pn.ci_high: cat = "inconclusive (neutral contrast not distinguishable from zero; difference between regimes not distinguishable either)"
else: cat = "reversed (neutral contrast < 0)"
# descriptors (if available)
desc_rows = []
cov = pd.read_csv(os.path.join(ANALYSIS, "metrics", "covariates_images.csv")).set_index("id")
have = all(i in cov.index for k in neu for i in G[G.training_run.isin([c for c in runs.index if c.startswith("NEU")])].o) if not args.dry_run else True
if have:
    photos = list(E.csv("source_images.csv").image_code); Zraw = descriptor_matrix(cov, photos); mu, sd = Zraw.mean(), Zraw.std().replace(0, 1)
    A_ds = E.csv("aesthetic_dataset.csv"); C_ds = E.csv("control_dataset.csv")
    aes = list(A_ds[A_ds.dataset_code == runs.training_dataset["RUN-AESTHETIC-4"]].image_code); ctl = list(C_ds[C_ds.dataset_code == runs.training_dataset["RUN-CONTROL-4"]].image_code)
    Zp = ((Zraw - mu) / sd)[DESCRIPTORS]; Zp.index = photos; x = (Zp.loc[aes].mean() - Zp.loc[ctl].mean()).to_numpy()
    def Zm(run): o = G[G.training_run == run].drop_duplicates("cell").set_index("cell").o.reindex(cells); return ((descriptor_matrix(cov, o.to_numpy()) - mu) / sd)[DESCRIPTORS].to_numpy()
    codes_n = {("AESTHETIC" if str(runs.training_dataset[c]).startswith("AESTHETIC") else "CONTROL", int(runs.seed[c])): c for c in runs.index if (c.startswith("NEU") or (args.dry_run and c.startswith("REP") and c not in REPLICATION_EXCLUDED))}
    if args.dry_run: codes_n.update({("AESTHETIC", 1254): "RUN-AESTHETIC-4", ("CONTROL", 9865): "RUN-CONTROL-4"})
    ac = np.mean([Zm(codes_n[("AESTHETIC", s)]) - Zm(codes_n[("CONTROL", s)]) for s in seeds], 0).mean(0)
    r = np.corrcoef(x, ac)[0, 1]; b = [np.corrcoef(x[i], ac[i])[0, 1] for i in rng.integers(0, 31, (N_BOOT, 31))]
    desc_rows.append(dict(quantity="r(x, a−c) under common captions", estimate=r, ci_low=float(np.nanpercentile(b, 2.5)), ci_high=float(np.nanpercentile(b, 97.5)), reference_original=0.707))
    pd.DataFrame(desc_rows).to_csv(os.path.join(OUT, f"caption_control_{tag}descriptors.csv"), index=False)
L = [f"# Controlled-caption experiment — analysis {'(DRY RUN on existing adapters: numbers meaningless, code-path test only)' if args.dry_run else ''}", "",
     f"Direction frozen (d = {d:.4f}); P = (e_A − e_C)·u per cell; intervals: bootstrap over the 48 prompts. Three quantities kept separate: estimate in the neutral regime, its uncertainty, paired per-cell difference between the original and the neutral regime.", "",
     "| seed | quantity | estimate | 95% CI | p | R |", "|---|---|---|---|---|---|"]
for _, r in Rz.iterrows():
    L.append(f"| {r.seed} | {r.quantity} | {r.estimate:+.4f} | {r.ci_low:+.4f} / {r.ci_high:+.4f} | {r.p_boot:.4f} | {'' if r.R is None or pd.isna(r.R) else f'{r.R:.3f}'} |")
L += ["", f"Category (protocol §4, revised): **{cat}**. Three seeds individually > 0: {all_pos}.", "",
      "Reading rules fixed in advance: a neutral-regime interval that includes zero is 'not distinguishable from zero', not 'lost'; the captions are called 'necessary' only if the paired difference between regimes is > 0 AND the neutral contrast is not distinguishable from zero; 'maintained' says that the corpora differ under common captions in this configuration, not that beauty is transferred.", ""]
if desc_rows: L += ["| descriptors | estimate | 95% CI | original |", "|---|---|---|---|"] + [f"| {r['quantity']} | {r['estimate']:+.3f} | {r['ci_low']:+.3f} / {r['ci_high']:+.3f} | {r['reference_original']:+.3f} |" for r in desc_rows]
write_md(f"report_caption_control{'_DRYRUN' if args.dry_run else ''}.md", L)
log("category:", cat); log("done")
