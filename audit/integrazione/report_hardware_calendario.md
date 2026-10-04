# Hardware, LoRA inference scale, 599/600, closure of phase 2 — from the records

## Hardware and software actually used (per-job `environmentJson` recorded by `aar_worker.py` at job end)

34 of 37 finished cloud jobs (all trainings and generations with a recorded environment; the 3 without environment are the two early jobs that failed on the provider's user-data check and one cancelled job): **GPU NVIDIA L4 (Scaleway L4-1-24G), Python 3.10.12, Linux 5.15.0-173 x86_64, torch 2.4.1+cu121 (CUDA 12.1), diffusers 0.30.3, transformers 4.44.2, peft 0.12.0, accelerate 0.34.2, safetensors 0.4.5**, base model stabilityai/stable-diffusion-xl-base-1.0 @ 462165984030d82259a11f4367a4eed129e94a7b. Worker hash `266541cf…` for RUN-*-4, all final generations and the replications. Bit-identical results across GPU models are not guaranteed (worker docstring); the determinism re-run (same seed, same hardware class) gives a per-cell embedding distance of 0.32 between two trainings.

## LoRA scale at inference (worker code, not library defaults)

`aar_worker.py` loads the adapter with `pipe.load_lora_weights(..., adapter_name="condition")` and calls `pipe.set_adapters(["condition"], adapter_weights=[lora_scale])` **only if** `lora_scale` is present in the plan configuration. Every one of the 1,536 generation records has `"lora_scale": null` → `set_adapters` was not called → adapter weight 1.0 (diffusers/peft default weight when an adapter is loaded without an explicit weight). With rank 16 and alpha 16 the peft scaling factor alpha/rank = 1.0, so the effective LoRA contribution is ΔW·1.0. Statement for the paper: "LoRA applied at inference with weight 1.0 (no external scale); alpha/rank = 1". This is read from the recorded configuration and the worker code; the generation parameters JSON of every image carries the hash of the weights used.

## 599 / 600

Coverage of a rater group, not removal of a photograph: architects (role `Architect`) rated 599 of the 600 photographs; non-experts (`NonExpert`) all 600; the Spearman correlation between the two group means is therefore computed on 599 photographs. High (4–5) vs low (1–2) self-assessed expertise both cover 600. The full corpus is 600 in every analysis.

## Last phase-2 answers and administrative closure

| event | time UTC | source |
|---|---|---|
| last phase-2 rating (included and overall) | 2026-10-01 11:55:54 | `posttraining_ratings.created_at` |
| last pairwise comparison answered | 2026-10-01 11:52:17 | `pairwise_trials.answered_at` |
| last phase-2 session started | 2026-10-01 11:52:17 | `posttraining_sessions.started_at` |
| experiment status PostTrainingCollection → Analysis (participant interface closed) | 2026-10-01 12:52:27 | `audit_log` `experiment.status_changed` |
| full export used by the manuscript | 2026-10-01 13:46 | export file name / audit `export` |

A last timestamp does not by itself show the questionnaire was closed; the status change 56 minutes after the last answer is the administrative closure. Sessions: 325 Completed, 15 Active (never finished), 3 Abandoned.
