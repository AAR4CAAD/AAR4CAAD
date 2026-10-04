"""
Audit step 0 — inventory of the inputs that exist in THIS environment (prompt section 1).

Writes outputs/INVENTARIO_INPUT.csv (path, sha256, size, matrix shape, row identifiers, role) and
outputs/inventario_controlli.md (cardinalities, duplicates, identifier matches, condition membership).
"""
import glob
import os
import zipfile

import numpy as np
import pandas as pd

from common import (ANALYSIS, DESCRIPTORS, EXPORT_REP_ZIP, EXPORT_ZIP, LOGS, ORIGINAL, OUT, PACKAGE, PREVIOUS_REPLY, PROJECT, REPLICATION_EXCLUDED, Export, Log, as_bool,
                    sha256, write_md)

log = Log("a00_inventory")
rows = []


def add(path, role, shape="", ids="", version=""):
    if not os.path.exists(path):
        rows.append(dict(path=os.path.relpath(path, PROJECT) if path.startswith(PROJECT) else path, exists=False, sha256="", size_bytes="", shape=shape, row_identifiers=ids, version=version, role=role))
        log("MISSING", path)
        return False
    if os.path.isdir(path):
        rows.append(dict(path=os.path.relpath(path, PROJECT) if path.startswith(PROJECT) else path, exists=True, sha256="(folder: see SHA256SUMS.txt of the repository)", size_bytes="", shape=shape, row_identifiers=ids, version=version, role=role)); return True
    rows.append(dict(path=os.path.relpath(path, PROJECT) if path.startswith(PROJECT) else path, exists=True, sha256=sha256(path), size_bytes=os.path.getsize(path), shape=shape,
                     row_identifiers=ids, version=version, role=role))
    return True


# ---------------------------------------------------------------- exports
add(EXPORT_ZIP, "original export of 2026-10-01 13:46 UTC: human data, frozen datasets, captions, training runs, generation, audit log (used by the manuscript and by the previous reply)")
add(EXPORT_REP_ZIP, "export of 2026-10-02 05:36 UTC: same experiment after the paired-seed replication trainings (adds REP-* runs and 960 generated images)")
E, R = Export(EXPORT_ZIP), Export(EXPORT_REP_ZIP)
same = []
for name in ["pretraining_ratings.csv", "posttraining_ratings.csv", "pairwise_trials.csv", "participants.csv", "aesthetic_dataset.csv", "control_dataset.csv", "captions.csv", "image_metadata.csv", "source_images.csv"]:
    a, b = sha256(os.path.join(E.folder, name)), sha256(os.path.join(R.folder, name))
    same.append((name, a == b, a[:12], b[:12]))
    if a != b:  # content equality beyond byte equality (export order / timestamps may differ)
        da, db = pd.read_csv(os.path.join(E.folder, name)), pd.read_csv(os.path.join(R.folder, name))
        same[-1] = (name, "same shape and same sorted content" if da.shape == db.shape and da.sort_values(list(da.columns)).reset_index(drop=True).equals(db.sort_values(list(db.columns)).reset_index(drop=True)) else f"DIFFERENT {da.shape} vs {db.shape}", a[:12], b[:12])
for name in sorted(os.listdir(E.folder)):
    p = os.path.join(E.folder, name)
    if os.path.isfile(p):
        shape = ""
        if name.endswith(".csv"):
            d = pd.read_csv(p, low_memory=False)
            shape = f"{d.shape[0]}x{d.shape[1]}"
        add(p, f"member of the original export", shape=shape)

# ---------------------------------------------------------------- matrices
emb = os.path.join(ANALYSIS, "metrics", "embeddings_dinov2_vitb14.npz")
z = np.load(emb, allow_pickle=False)
add(emb, "DINOv2 CLS and patch-mean embeddings: 600 photographs + 576 original generated images (keys kind,id,cls,patch_mean)", shape=f"cls {z['cls'].shape}", ids="id = ARCH_xxxx for photographs, opaque_id (32 hex) for generated images", version=f"model {z['model']}; preprocessing {z['preprocessing']}")
kinds = pd.Series(z["kind"]).value_counts().to_dict()
emb_ids = set(z["id"])
embr = os.path.join(ANALYSIS, "metrics", "embeddings_replication_dinov2_vitb14.npz")
zr = np.load(embr, allow_pickle=False)
add(embr, "DINOv2 embeddings of the 960 images of the five replication adapters", shape=f"cls {zr['cls'].shape}", ids="opaque_id", version=f"model {zr['model']}")
d = os.path.join(ANALYSIS, "baseline", "direction_dinov2.npz")
dz = np.load(d, allow_pickle=False)
add(d, "frozen source direction (tag baseline-v1): centroids of the 89+89 photographs, unit vector, gap", shape="cls_v (768,)", version=f"gap {float(dz['cls_gap']):.6f}; datasets {dz['datasets']}")
cov_p = os.path.join(ANALYSIS, "metrics", "covariates_images.csv")
cov = pd.read_csv(cov_p)
add(cov_p, "31 descriptors (+elegant): 10 pixel measures and 22 CLIP ViT-L/14 zero-shot attributes for all 2136 images (600 photographs, 576 original, 960 replication)", shape=f"{cov.shape[0]}x{cov.shape[1]}", ids="id (image_code or opaque_id)")
add(os.path.join(ANALYSIS, "image_scripts", "covariates.py"), "pipeline of the 31 descriptors (CLIP prompts and pixel measures)")
add(os.path.join(ANALYSIS, "images", "manifest.csv"), "mapping kind/image_code/opaque_id of the 1176 images used for the baseline embeddings")
add(os.path.join(ANALYSIS, "replication", "images", "manifest.csv"), "mapping of the 768 replication images downloaded for embeddings (+192 determinism run in images/det)")
add(os.path.join(ANALYSIS, "replication", "design.json"), "replication design: seeds, training order, criterion written before the trainings")
for p in sorted(glob.glob(os.path.join(ANALYSIS, "embedding_report", "*"))) + sorted(glob.glob(os.path.join(ANALYSIS, "replication_report", "*"))) + \
        sorted(glob.glob(os.path.join(ANALYSIS, "decomposition_report", "*"))) + sorted(glob.glob(os.path.join(ANALYSIS, "figures", "*.csv"))) + sorted(glob.glob(os.path.join(ANALYSIS, "figures", "*.md"))) + \
        sorted(glob.glob(os.path.join(ANALYSIS, "human_report", "*"))) + sorted(glob.glob(os.path.join(ANALYSIS, "vlm_report", "*"))):
    add(p, "historical report/result (read only; compared with the recomputed values)")
for p in ["embedding_analysis.py", "replication_analysis.py", "direction_decomposition.py", "caption_analysis.py", "figures_transfer.py", "arch300_analysis.py", "vlm_analysis.py", "replication_vlm_analysis.py", "baseline/freeze.py", "ANALYSIS_PLAN.md"]:
    add(os.path.join(ANALYSIS, p), "historical analysis code")
add(os.path.join(PROJECT, "training", "aar_worker.py"), "trainer and generator actually run on the cloud GPU (LoRA on the UNet attention projections; text encoders frozen)")
add(os.path.join(PROJECT, "training", "platform", "TrainingDatasetService.cs"), "selection rule and CONTROL sampling algorithm (SampleControl)")
add(os.path.join(PROJECT, "training", "platform", "DeterministicRandom.cs"), "xoshiro256** generator used by SampleControl")
for p in sorted(glob.glob(os.path.join(ANALYSIS, "vlm", "outputs", "*", "*.jsonl"))) + sorted(glob.glob(os.path.join(ANALYSIS, "vlm", "manifests", "*.csv"))):
    add(p, "VLM raw responses / blind manifests")
for p in sorted(glob.glob(os.path.join(os.path.expanduser("~"), "Downloads", "job*_lora.safetensors"))):
    add(p, "LoRA weights downloaded locally (jobs 3-6 = RUN-AESTHETIC/RUN-CONTROL v1 and tests; NOT the RUN-*-4 adapters used for the evaluated images)")
# package received
for p in sorted(glob.glob(os.path.join(PREVIOUS_REPLY, "*"))):
    add(p, "attachment of the previous reply (other assistant) — verified, not trusted")
for p in sorted(glob.glob(os.path.join(PACKAGE, "02_review", "*"))) + sorted(glob.glob(os.path.join(PACKAGE, "01_manuscritto", "*.docx"))):
    add(p, "review texts / manuscript revision 12 received in the package")

# ---------------------------------------------------------------- cardinality checks
G = E.csv("generated_images.csv")
G["o"] = G.opaque_id.str.replace("-", "").str.lower()
main_plans = set(G[G.training_run.isin(ORIGINAL)].generation_plan_id)
Gm = G[G.generation_plan_id.isin(main_plans)]
GR = R.csv("generated_images.csv")
GR["o"] = GR.opaque_id.str.replace("-", "").str.lower()
rep_runs = sorted(r for r in GR.training_run.dropna().unique() if str(r).startswith("REP-"))
shaf = lambda p: sha256(p) if os.path.isfile(p) else "(folder)"
checks = ["# Inventory checks", "", f"Export (original): `{os.path.basename(EXPORT_ZIP)}` sha256 `{shaf(EXPORT_ZIP)}`", f"Export (replication): `{os.path.basename(EXPORT_REP_ZIP)}` sha256 `{shaf(EXPORT_REP_ZIP)}`", "",
          "## Human tables identical in the two exports?", "", "| table | identical | sha(original) | sha(replication) |", "|---|---|---|---|"]
checks += [f"| {n} | {s} | {a} | {b} |" for n, s, a, b in same]
checks += ["", "## Generated images (original export)", "",
           f"- rows: {len(G)}; conditions: {G.condition_code.value_counts().to_dict()}",
           f"- main plans {sorted(main_plans)}: {len(Gm)} images = {Gm.groupby('condition_code').size().to_dict()}; prompts {Gm.prompt_code.nunique()}; seeds {sorted(Gm.seed.unique())}; cells {Gm.groupby(['prompt_code', 'seed']).ngroups}",
           f"- training runs of the main plans: {Gm.training_run.dropna().unique().tolist()} (BASE has none)",
           f"- duplicated opaque ids: {int(G.o.duplicated().sum())}; duplicated sha256: {int(G.sha256.duplicated().sum())}",
           f"- shown to participants (not excluded by the review rule): {int((~as_bool(Gm.excluded_by_review_rule)).sum())} images = {int((~as_bool(Gm.excluded_by_review_rule)).sum()) // 3} triplets",
           f"- other plans (tests, not evaluated): {len(G) - len(Gm)} images in plans {sorted(set(G.generation_plan_id) - main_plans)} with runs {G[~G.generation_plan_id.isin(main_plans)].training_run.dropna().unique().tolist()}",
           "", "## Embeddings", "",
           f"- baseline file: kinds {kinds}; all 600 photograph codes present: {set(E.csv('source_images.csv').image_code) <= emb_ids}; all 576 main-plan generated ids present: {set(Gm.o) <= emb_ids}",
           f"- replication file: {zr['cls'].shape[0]} ids; runs in the replication export: {rep_runs}; images per run: {GR[GR.training_run.isin(rep_runs)].groupby('training_run').size().to_dict()}",
           f"- replication ids covered by the replication embedding file: {int(GR[GR.training_run.isin(rep_runs)].o.isin(set(zr['id'])).sum())} of {int(GR.training_run.isin(rep_runs).sum())}",
           f"- excluded from the paired-seed analyses by design: {REPLICATION_EXCLUDED} (determinism re-run of seed 1254, same corpus as RUN-AESTHETIC-4)",
           "", "## Descriptor matrix", "",
           f"- rows {len(cov)}: kinds {cov.kind.value_counts().to_dict()}; duplicated ids {int(cov.id.duplicated().sum())}; missing values {int(cov[DESCRIPTORS].isna().sum().sum())}",
           f"- covers the 600 photographs: {set(E.csv('source_images.csv').image_code) <= set(cov.id)}; the 576 original images: {set(Gm.o) <= set(cov.id)}; the replication images: {int(GR[GR.training_run.isin(rep_runs)].o.isin(set(cov.id)).sum())} of {int(GR.training_run.isin(rep_runs).sum())}",
           "", "## Units of observation (to keep separate)", "",
           "- Human sample: 158 participants of phase 2 on 159 triplets of the two ORIGINAL adapters (RUN-AESTHETIC-4 seed 1254, RUN-CONTROL-4 seed 9865) + BASE.",
           "- Computational replication: 3 paired training seeds × 2 corpora = 6 adapters, 192 cells each; BASE images are the SAME 192 for every seed (one BASE image per cell, re-used in every contrast: not independent observations).",
           "- A 7th adapter (REP-AES-S1254-R) repeats seed 1254 on AESTHETIC-v2 to measure training non-determinism; it is not an additional realisation.", ""]
pd.DataFrame(rows).to_csv(os.path.join(OUT, "INVENTARIO_INPUT.csv"), index=False)
write_md("inventario_controlli.md", checks)
log("\n".join(checks))
log("inventory rows", len(rows), "missing", sum(not r["exists"] for r in rows))
