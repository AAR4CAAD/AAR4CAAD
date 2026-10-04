"""
Figure (manuscript Fig. 3): DINOv2, original geometry — change of the mean image-to-centroid distance with respect to BASE,
per adapter and training seed, towards the own and the other photograph corpus, with 95% prompt-bootstrap intervals.
Data: audit_rev12/outputs/dino_distance_changes.csv (produced by audit_rev12/scripts/a03_dino.py).

    python figures_distances.py [--out figures]
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(HERE, "figures")); ap.add_argument("--data", default=os.path.join(os.path.dirname(HERE), "audit", "outputs", "dino_distance_changes.csv"))
a = ap.parse_args()
D = pd.read_csv(a.data)
seeds = [1254, 9865, 42160]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), dpi=300, sharey=True)
for ax, adapter in zip(axes, ["AESTHETIC", "CONTROL"]):
    own_t = "AESTHETIC photographs" if adapter == "AESTHETIC" else "CONTROL photographs"; oth_t = "CONTROL photographs" if adapter == "AESTHETIC" else "AESTHETIC photographs"
    x = np.arange(len(seeds)); w = 0.27
    for k, (tgt, lab, col) in enumerate(((own_t, "own repertoire", "#2b5d8c"), (oth_t, "other repertoire", "#b8743a"), ("own minus other corpus (approach difference)", "own − other", "#555555"))):
        sub = D[(D.adapter == adapter) & (D.target == tgt)].set_index("training_seed").reindex(seeds)
        est = sub.mean_change_of_image_to_centroid_distance.to_numpy(); lo = sub.ci_low.to_numpy(); hi = sub.ci_high.to_numpy()
        ax.bar(x + (k - 1) * w, est, w, color=col, label=lab, yerr=[est - lo, hi - est], capsize=2, error_kw={"lw": 0.8})
    ax.axhline(0, color="black", lw=0.6); ax.set_xticks(x); ax.set_xticklabels([str(s) for s in seeds]); ax.set_xlabel("training seed")
    ax.set_title(f"{adapter} adapters", fontsize=9); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
axes[0].set_ylabel("ΔD vs BASE (mean image → photograph centroid)"); axes[0].legend(frameon=False, fontsize=7, loc="upper right", ncol=1)
fig.text(0.5, -0.02, "Negative = closer to that repertoire than BASE. 192 cells per adapter; bars = 95% bootstrap over the 48 prompts. DINOv2 CLS, L2-normalised, original geometry.", ha="center", fontsize=6.5, color="#444")
fig.tight_layout(); os.makedirs(a.out, exist_ok=True)
fig.savefig(os.path.join(a.out, "fig_dino_distance_changes.png"), bbox_inches="tight"); fig.savefig(os.path.join(a.out, "fig_dino_distance_changes.pdf"), bbox_inches="tight")
print("ok")
