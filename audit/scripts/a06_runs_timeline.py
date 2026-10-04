"""
Audit step 6 — RUN-AESTHETIC-4 / RUN-CONTROL-4 and the chronology (prompt section 3).

Reads training_runs.csv, generated_images.csv, generation_plan.csv, prompt_sets.csv and audit_log.csv (every recorded event with
its creator) and reconstructs: all training runs with dataset/captions/seed/config/weights/status/notes; every cloud job
(training and generation) with its worker hash; which generation plans existed before the final ones (exposure to outputs);
prompt-set versions; the screening records; the sequence of experiment states; symmetry of the changes between the two corpora.
Every timestamp is labelled with its source and meaning (record creation, job start/end, decision save).

Writes outputs/runs_all.csv, outputs/timeline_full.csv, outputs/report_runs_timeline.md.
"""
import json
import os

import numpy as np
import pandas as pd

from common import OUT, Export, Log, as_bool, write_md

log = Log("a06_runs_timeline")
E = Export()
if not os.path.exists(os.path.join(E.folder, "audit_log.csv")):
    raise SystemExit("This step needs the complete platform audit log (not redistributed: it contains participant-level events). Its outputs, produced on the full export on 2026-10-03, are in outputs/ (report_runs_timeline.md, timeline_full.csv, runs_all.csv, cloud_jobs.csv, report_documentation.md).")
A = E.csv("audit_log.csv"); A["t"] = pd.to_datetime(A.created_at, utc=True)
runs = E.csv("training_runs.csv").sort_values("started_at")
G = E.csv("generated_images.csv"); G["t"] = pd.to_datetime(G.created_at, utc=True)
GP = E.csv("generation_plan.csv"); PS = E.csv("prompt_sets.csv")
R = E.csv("posttraining_ratings.csv"); PR = E.csv("pretraining_ratings.csv")
events = []


def ev(t, event, source, meaning, detail=""):
    events.append(dict(time_utc=t, event=event, source=source, meaning=meaning, detail=str(detail)[:300]))


def aj(s):
    try: return json.loads(s) if isinstance(s, str) else {}
    except Exception: return {}


# ---------------------------------------------------------------- training runs
jobs = A[A.action.isin(["cloud_job.started", "cloud_job.finished", "cloud_job.cancelled"])].copy()
jobs["j"] = jobs.after_json.apply(aj)
job_rows = []
for _, r in jobs.iterrows():
    j = r.j; job_rows.append(dict(time=r.created_at, action=r.action, job_id=r.entity_id, kind=j.get("kind"), training_run_id=j.get("trainingRunId"), plan_id=j.get("generationPlanId"), worker_sha256=j.get("workerSha256"), status=j.get("status"), note=j.get("message") or j.get("error") or r.reason))
J = pd.DataFrame(job_rows); J.to_csv(os.path.join(OUT, "cloud_jobs.csv"), index=False)
worker_hashes = J.worker_sha256.dropna().unique().tolist()
run_rows = []
for _, r in runs.iterrows():
    cfg = aj(r.configuration_json)
    gen = G[G.training_run == r.code]
    lora_sha = sorted({aj(x).get("lora_sha256") for x in gen.generation_parameters_json}) if len(gen) else []
    tj = J[(J.training_run_id == r.training_run_id) & (J.action == "cloud_job.started")]
    run_rows.append(dict(code=r.code, name=r["name"], dataset=r.training_dataset, base_model=r.base_model, base_revision=r.base_model_revision[:12], seed=r.seed, steps=r.steps, lr=r.learning_rate, rank=r.lora_rank, alpha=r.lora_alpha, resolution=r.resolution,
                         noise_offset=cfg.get("noise_offset", "default(worker: 0.0357 for SDXL)" if r.model_family == "SDXL" else ""), timestep_min=cfg.get("timestep_min", 0), other_config={k: v for k, v in cfg.items() if k not in ("noise_offset", "timestep_min")},
                         started=r.started_at, completed=r.completed_at, status=r.status, artifact=os.path.basename(str(r.artifact_uri)), weights_sha256_used_for_images=";".join(x for x in lora_sha if x) or "(no generated image in the export)",
                         n_generated_images_in_export=len(gen), evaluated_by_humans=(r.code in ("RUN-AESTHETIC-4", "RUN-CONTROL-4")), worker_sha256=";".join(tj.worker_sha256.dropna().unique()), notes=r.notes))
    ev(r.started_at, f"training started {r.code}", "training_runs.started_at", "job start recorded by the platform", f"dataset {r.training_dataset}, seed {r.seed}, config {cfg}")
    ev(r.completed_at, f"training completed {r.code}", "training_runs.completed_at", "weights uploaded; record updated", r.notes)
RUNS = pd.DataFrame(run_rows); RUNS.to_csv(os.path.join(OUT, "runs_all.csv"), index=False)
log(RUNS[["code", "dataset", "seed", "noise_offset", "timestep_min", "started", "status", "n_generated_images_in_export", "notes"]].to_string())
# the two evaluated adapters: weights hash consistency
for code in ("RUN-AESTHETIC-4", "RUN-CONTROL-4"):
    shas = {aj(x).get("lora_sha256") for x in G[G.training_run == code].generation_parameters_json}
    log(f"{code}: lora_sha256 in the 192 generation records: {shas}")
# training-run.updated events (what changed after creation?)
upd = A[A.action == "training_run.updated"]
upd_summary = upd.groupby("entity_id").size().to_dict()
log("training_run.updated events per run id:", upd_summary)
for _, r in upd.iterrows():
    b, a_ = aj(r.before_json), aj(r.after_json)
    diff = {k: (b.get(k), a_.get(k)) for k in set(b) | set(a_) if b.get(k) != a_.get(k) and k not in ("updatedAt",)}
    ev(r.created_at, f"training run {r.entity_id} updated", "audit_log training_run.updated", "record edit (status/notes/artifact) saved by the platform or the user", json.dumps(diff, default=str)[:300])

# ---------------------------------------------------------------- generation plans and prompt sets (exposure to outputs)
plans = A[A.action.isin(["generation_plan.frozen", "generation_plan.deleted", "generation_plan.changed"])]
for _, r in plans.iterrows():
    j = aj(r.after_json) or aj(r.before_json)
    ev(r.created_at, f"{r.action} plan {r.entity_id}", "audit_log", "plan frozen = generation requested; deleted = plan removed (test plans)", json.dumps({k: j.get(k) for k in ("name", "promptSetId", "conditions", "seeds") if k in j}))
imports = A[A.action == "generation.imported"]; imports_t = pd.to_datetime(imports.created_at, utc=True)
pf = A[A.action == "prompt_set.frozen"]
for _, r in pf.iterrows():
    ev(r.created_at, f"prompt set {r.entity_id} frozen", "audit_log prompt_set.frozen", "prompt set version frozen", aj(r.after_json))
pc = A[A.action == "prompt.changed"]; log("prompt.changed events:", len(pc), pc.created_at.min(), "→", pc.created_at.max())
final_ps = GP[GP.generation_plan_id.isin([22, 23])].prompt_set_id.unique().tolist()
final_frozen = pf[pf.entity_id.astype(str).isin([str(x) for x in final_ps])].created_at.tolist()
# generated images in the export: only the final 576 (test generations were deleted with their plans)
log("generation plans in export:", GP[["generation_plan_id", "name", "prompt_set_id", "frozen_at"]].to_dict("records"))
log("generation.imported events:", len(imports), "first", imports.created_at.min(), "last", imports.created_at.max(), "| before the final prompt freeze:", int((imports_t < pd.Timestamp(min(final_frozen)) if final_frozen else False).sum()))
# which runs produced images before the final prompt-set freeze? (generation plans deleted → use cloud jobs of kind Generation)
genjobs = J[(J.kind == "Generation") & (J.action == "cloud_job.started")]
log("generation cloud jobs:", len(genjobs), genjobs[["time", "job_id", "plan_id"]].to_string())

# ---------------------------------------------------------------- statuses, screening, phases
for _, r in A[A.action.isin(["experiment.status_changed", "experiment.protocol_changed", "experiment.protocol_frozen", "experiment.updated", "selection_rule.created", "selection_rule.frozen", "dataset.generated", "dataset.frozen", "corpus.extended"])].iterrows():
    j = aj(r.after_json)
    ev(r.created_at, f"{r.action} ({r.entity_type} {r.entity_id})", "audit_log", "decision saved by the user" if r.action not in ("dataset.generated",) else "dataset generated by the platform", json.dumps({k: j.get(k) for k in ("status", "code", "name", "items", "ruleJson", "postTrainingTargetParticipants", "researchQuestion") if k in j})[:300] + (f" reason: {r.reason}" if isinstance(r.reason, str) else ""))
qd = A[A.action == "quality.decision"]; mc = A[A.action == "manual_correction"]
ev(PR.created_at.min(), "first phase-1 rating", "pretraining_ratings.created_at", "answer saved"); ev(PR.created_at.max(), "last phase-1 rating", "pretraining_ratings.created_at", "answer saved")
ev(G.created_at.min(), "first final generated image imported", "generated_images.created_at", "import of the generated file (generation itself ran minutes earlier on the GPU)")
ev(G.created_at.max(), "last final generated image imported", "generated_images.created_at", "import")
ev(mc.created_at.min(), "first manual correction on generated images", "audit_log manual_correction", "defect flag / activation saved", mc.reason.iloc[0])
rev = G.reviewed_at.dropna(); ev(rev.min(), "first screening record (reviewed_at)", "generated_images.reviewed_at", "blind review decision saved (bulk save possible: NOT a measure of reviewing time)"); ev(rev.max(), "last screening record", "generated_images.reviewed_at", "same")
ev(R.created_at.min(), "first phase-2 rating", "posttraining_ratings.created_at", "answer saved"); ev(R.created_at.max(), "last phase-2 rating", "posttraining_ratings.created_at", "answer saved")
TL = pd.DataFrame(events); TL["t"] = pd.to_datetime(TL.time_utc, utc=True, errors="coerce"); TL = TL.sort_values("t").drop(columns="t"); TL.to_csv(os.path.join(OUT, "timeline_full.csv"), index=False)
# screening facts
flagged = G[G.review_defects.notna() & (G.review_defects != "None")]
log("screening: images with defects", len(flagged), flagged.groupby("condition_code").size().to_dict(), "| defect types:", flagged.review_defects.value_counts().head(10).to_dict())
log("reviewed_at span:", rev.min(), "→", rev.max(), "| distinct reviewed_at values:", rev.nunique(), "| manual_correction events:", len(mc), mc.created_at.min(), "→", mc.created_at.max(), "| users:", mc.user.value_counts().to_dict())
# phase-1 ratings during phase 2?
log("phase-1 ratings after the first phase-2 rating:", int((pd.to_datetime(PR.created_at, utc=True) > pd.to_datetime(R.created_at.min(), utc=True)).sum()))
# symmetry: caption changes per corpus
cc = A[A.action == "caption.changed"]; cc_t = pd.to_datetime(cc.created_at, utc=True)
A_ds = E.csv("aesthetic_dataset.csv"); C_ds = E.csv("control_dataset.csv")
aes = set(A_ds[A_ds.dataset_code == "AESTHETIC-v2"].image_code); ctl = set(C_ds[C_ds.dataset_code == "CONTROL-v2"].image_code)
CAP = E.csv("captions.csv"); cap_img = CAP.set_index("caption_id").image_code
cc_img = cc.entity_id.astype(str).where(cc.entity_id.astype(str).str.startswith("ARCH"), cc.entity_id.astype(str).map(lambda v: cap_img.get(int(v)) if v.isdigit() else v))
log("caption.changed by corpus:", {"AESTHETIC": int(cc_img.isin(aes).sum()), "CONTROL": int(cc_img.isin(ctl).sum()), "other": int((~cc_img.isin(aes | ctl)).sum())})

# ---------------------------------------------------------------- report
users = A.user.value_counts().to_dict()
L = ["# Training runs and chronology (audit rev12)", "",
     f"Sources: `training_runs.csv`, `generated_images.csv`, `generation_plan.csv`, `prompt_sets.csv`, `audit_log.csv` ({len(A)} events, users {users}). Times UTC. "
     "Each timestamp is the moment a record was saved by the platform; durations of human activities are not measured by these records.", "",
     "## 1. All recorded training runs", "", "| code | dataset | seed | noise offset | timestep min | started | completed | status | images in export | note |", "|---|---|---|---|---|---|---|---|---|---|"]
for _, r in RUNS.iterrows():
    L.append(f"| {r.code} | {r.dataset} | {r.seed} | {r.noise_offset} | {r.timestep_min} | {str(r.started)[:16]} | {str(r.completed)[:16]} | {r.status} | {r.n_generated_images_in_export} | {r.notes if isinstance(r.notes, str) else ''} |")
L += ["", "What distinguishes RUN-1/2/3/4 (from the records, not inferred from the suffix):",
      "- RUN-AESTHETIC / RUN-CONTROL (v1 captions, default settings), 27 Sep 22:19–22:43: first complete pair.",
      "- TEST-AES-S500 / TEST-AES-LR3E5 (AESTHETIC only, 28 Sep 00:18–00:54): 'green-cast investigation' — technical tests on one corpus, no CONTROL counterpart.",
      "- RUN-*-2 (v2 captions, 01:29–01:53): same settings, captions rewritten/harmonised; the only change is the text.",
      "- RUN-*-3 (+ noise offset 0.0357, 04:46–05:10): configuration fix for washed-out, low-contrast output (worker note).",
      "- RUN-*-4 (+ timesteps ≥ 250, 05:55–06:19): configuration fix so the LoRA does not learn fine photographic texture (JPEG noise, lettering). **These are the adapters evaluated by the participants.**",
      "- RUN-*-RV (RealVisXL base, 06:45–07:08): photorealism test on a different base model; not used.",
      "The sequence is a chain of configuration changes applied to BOTH corpora at each step (symmetric), with two extra single-corpus tests. Which outputs were inspected between steps is not recorded as data: the notes name the defect observed (colour cast, washed-out contrast, texture), which implies that trial generations of the intermediate runs were viewed before each change. Those trial generation plans were deleted (19 `generation_plan.deleted` events) and their images are not in the export. "
      "No record documents a comparison of the human-relevant outcome (ratings) across runs before choosing RUN-4: the choice is documented as a technical-quality decision. The seeds 1254/9865 are constant across all runs of each corpus, so the realisation evaluated is the 4th configuration, not the best of four seeds.", "",
      f"Trainer: `aar_worker.py` (hash recorded per job: {len(worker_hashes)} distinct worker versions over the jobs: {[h[:12] for h in worker_hashes]}); LoRA on the UNet attention projections (to_q, to_k, to_v, to_out.0), rank 16, alpha 16, gaussian init; text encoders frozen (captions pre-encoded, no text-encoder LoRA); AdamW lr 1e-4, batch 1, 1500 steps, fp16; noise offset and minimum timestep per table. "
      f"Weights used for the 576 evaluated images: lora_sha256 recorded in each generation record and checked against the artifact (one hash per adapter: {RUNS.set_index('code').loc['RUN-AESTHETIC-4', 'weights_sha256_used_for_images'][:12]}…, {RUNS.set_index('code').loc['RUN-CONTROL-4', 'weights_sha256_used_for_images'][:12]}…). The .safetensors of RUN-*-4 are on the platform's storage (artifact_uri), not in this repository.", "",
      "## 2. Timeline (facts recorded; meaning of each timestamp in the column)", "", "| time UTC | event | source | meaning | detail |", "|---|---|---|---|---|"]
for _, r in TL.iterrows():
    L.append(f"| {str(r.time_utc)[:19]} | {r.event} | {r.source} | {r.meaning} | {r.detail.replace('|', '/')} |")
L += ["", "## 3. Facts relevant to the review", "",
      f"- Phase-1 ratings after the first phase-2 rating: {int((pd.to_datetime(PR.created_at, utc=True) > pd.to_datetime(R.created_at.min(), utc=True)).sum())} (phase 1 did not continue during phase 2). The status log shows a 79-second re-opening of phase 1 on 27 Sep 20:45–20:46 with no rating saved.",
      "- The selection rule at 35% was created 17 s before the last phase-1 rating and frozen 85 s after it; the preliminary 33% rule was created 46 min earlier while collection was open. 'Definita dopo la raccolta' is imprecise: 'defined in the last minutes of the collection and frozen immediately after it closed, before any dataset or training'.",
      f"- Captions: {len(cc)} `caption.changed` events between 27 Sep 13:48 and 28 Sep 01:28 (two user accounts), AESTHETIC {int(cc_img.isin(aes).sum())} vs CONTROL {int(cc_img.isin(ctl).sum())}; all 89 AESTHETIC captions differ between v1 and v2, 62 of 89 CONTROL captions. The harmonisation was not symmetric in extent (declared by the audit events 1238/1480 as 'rewritten' vs 'harmonised').",
      f"- Prompts: {len(pc)} `prompt.changed` events, {len(pf)} prompt-set freezes; the final set (id {final_ps}) frozen at {min(final_frozen) if final_frozen else 'n/a'}; generation plans 22/23 frozen 13:09; generation 13:14–14:28. Earlier plans (19 deleted; {len(genjobs)} generation jobs in total, {int((imports_t < pd.Timestamp(min(final_frozen))).sum())} trial images imported before the final prompt freeze) show that prompts were revised while trial outputs of the intermediate runs existed: 'frozen before the final generation', not 'before seeing any output'.",
      f"- Screening: {len(flagged)} images flagged ({flagged.groupby('condition_code').size().to_dict()}), reviewed_at spans {str(rev.min())[11:19]}–{str(rev.max())[11:19]} UTC with {rev.nunique()} distinct timestamps; the `manual_correction` events run from {str(mc.created_at.min())[11:19]} to {str(mc.created_at.max())[11:19]}: the two-minute span of `reviewed_at` is the bulk save of the rule, not the duration of the review (the first defect flags were saved from 13:25, during the import).",
      "- Phase 2 opened at 15:31:59, 28 s after the last screening save.", "",
      "## 4. Separate conclusions", "",
      "**Different seeds.** The two evaluated adapters differ in corpus AND in training seed (1254 vs 9865). The records show the seeds fixed from the first run (27 Sep) and never changed; nothing in the records shows seed selection. But the human contrast remains a comparison of two realisations: the paired-seed replication (3 seeds × 2 corpora) shows the DINOv2 contrast is stable across seeds (+0.044/+0.041/+0.050), while the VLM contrasts are not reproduced and the original CONTROL adapter scores lower than the other CONTROL adapters on representation quality (`report_replication_vlm.md`). The human endpoint has no replication: the limit stands, declared or not.",
      "**Selection of realisations.** Four successive configurations were trained on both corpora; RUN-4 was chosen for technical quality (texture, contrast) according to the notes, before any human rating of outputs existed (phase 2 opened after RUN-4's images were screened). There is no evidence of choosing among realisations on the outcome; there is also no record proving the intermediate outputs were not compared on preference. The honest statement: 'configuration chosen after inspecting trial outputs for technical defects; no outcome data existed at that time; seeds never varied'.", ""]
write_md("report_runs_timeline.md", L)
log("done")
