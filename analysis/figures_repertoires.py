"""
Figure: the two training repertoires (AESTHETIC vs CONTROL), two panels of six photographs each.

    python figures_repertoires.py <export.zip | folder> [--out figures]

Selection rule (deterministic, declared in the caption): within each of three period bands (1919–1969, 1970–2009, 2010+)
the two photographs of the set with the most extreme projection on the frozen source direction u — largest for AESTHETIC,
smallest (most CONTROL-like) for CONTROL — skipping a photograph whose building type is already shown in the panel.
Under each image: architect | style | period. Credits (photographer, licence) in figures/fig_repertoires_credits.csv.
"""
import argparse
import os
import tempfile
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BANDS = [("1919–1969", {"1919-1945", "1946-1969", "pre-1919"}), ("1970–2009", {"1970-1989", "1990-2009"}), ("2010+", {"2010-today"})]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("export"); ap.add_argument("--out", default=os.path.join(HERE, "figures")); ap.add_argument("--per-band", type=int, default=2)
    a = ap.parse_args(); folder = a.export
    if zipfile.is_zipfile(folder):
        folder = tempfile.mkdtemp(); zipfile.ZipFile(a.export).extractall(folder)
    rd = lambda f: pd.read_csv(os.path.join(folder, f))
    M = rd("image_metadata.csv").set_index("image_code")
    runs = rd("training_runs.csv").set_index("code"); A = rd("aesthetic_dataset.csv"); C = rd("control_dataset.csv")
    sets = {"AESTHETIC": list(A[A.dataset_code == runs.training_dataset["RUN-AESTHETIC-4"]].image_code), "CONTROL": list(C[C.dataset_code == runs.training_dataset["RUN-CONTROL-4"]].image_code)}
    z = np.load(os.path.join(HERE, "metrics", "embeddings_dinov2_vitb14.npz"), allow_pickle=False); D = np.load(os.path.join(HERE, "baseline", "direction_dinov2.npz"), allow_pickle=False)
    E = {i: v / np.linalg.norm(v) for i, k, v in zip(z["id"], z["kind"], z["cls"].astype(np.float64)) if k == "source"}
    u = D["cls_v"]
    chosen, rows = {}, []
    for name, codes in sets.items():
        proj = pd.Series({c: float(E[c] @ u) for c in codes}).sort_values(ascending=(name == "CONTROL"))
        picked, types = [], set()
        for band, periods in BANDS:
            n = 0
            for c in proj.index:
                if M.loc[c, "period"] in periods and M.loc[c, "building_type"] not in types:
                    picked.append((c, band)); types.add(M.loc[c, "building_type"]); n += 1
                    if n == a.per_band: break
        chosen[name] = picked
        for c, band in picked:
            m = M.loc[c]; rows.append(dict(panel=name, image_code=c, band=band, building=m.building_name, architect=m.architect, style=m.architectural_style, period=m.period, building_type=m.building_type, city=m.city, country=m.country,
                                           projection_on_u=round(float(E[c] @ u), 4), photographer=m.photographer, license=m.license, wikimedia_page=m.wikimedia_page_url))
    os.makedirs(a.out, exist_ok=True); pd.DataFrame(rows).to_csv(os.path.join(a.out, "fig_repertoires_credits.csv"), index=False)
    # ---- figure: two panels stacked, each 2 rows x 3 columns (one column per band)
    def short(t, n):
        t = str(t); return t if len(t) <= n else t[:n - 1].rstrip(" ,") + "…"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7})
    fig = plt.figure(figsize=(7.2, 6.3), dpi=300)
    gs = fig.add_gridspec(2, 1, hspace=0.30, top=0.885, bottom=0.005, left=0.01, right=0.99)
    for pi, (name, picked) in enumerate(chosen.items()):
        sub = gs[pi].subgridspec(2, 3, wspace=0.04, hspace=0.42)
        axes0 = []
        for bi, (band, _) in enumerate(BANDS):
            items = [p for p in picked if p[1] == band]
            for ri in range(2):
                ax = fig.add_subplot(sub[ri, bi]); ax.axis("off")
                if ri == 0: axes0.append(ax)
                if ri >= len(items): continue
                c = items[ri][0]; m = M.loc[c]
                img = Image.open(os.path.join(HERE, "images", "source", f"{c}.jpg")).convert("RGB")
                w, h = img.size; tw, th = 4, 3; s_ = min(w / tw, h / th); cw, ch = int(s_ * tw), int(s_ * th)
                img = img.crop(((w - cw) // 2, (h - ch) // 2, (w - cw) // 2 + cw, (h - ch) // 2 + ch)).resize((480, 360), Image.LANCZOS)
                ax.imshow(img)
                arch = str(m.architect) if isinstance(m.architect, str) else (str(m.architecture_firm) if isinstance(m.architecture_firm, str) else "—")
                ax.set_title(short(arch, 40) + chr(10) + f"{short(m.architectural_style, 34)} | {m.period}", fontsize=6.0, pad=2.0)
        y = axes0[0].get_position().y1
        for bi, ax in enumerate(axes0):
            p = ax.get_position(); fig.text((p.x0 + p.x1) / 2, y + 0.052, BANDS[bi][0], ha="center", va="bottom", fontsize=7.5, color="#444")
        fig.text(0.01, y + 0.075, f"{'A' if pi == 0 else 'B'}  {name}  ({len(sets[name])} photographs)", fontsize=9.5, weight="bold", va="bottom")
    fig.savefig(os.path.join(a.out, "fig_repertoires.png")); fig.savefig(os.path.join(a.out, "fig_repertoires.pdf"))
    print(pd.DataFrame(rows)[["panel", "band", "image_code", "architect", "style", "period", "building_type", "projection_on_u"]].to_string())


if __name__ == "__main__":
    main()
