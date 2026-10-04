# Human statistics — reproduction and sensitivities (audit rev12)

Independent recomputation from the export (SHA256 ea0bdbf6…). Reported values come from the manuscript revision 12 unless stated. Inference unit: participants, unless the row says prompt or two-way. The human data concern ONLY the two original adapters (training seeds 1254/9865); no model of repeated judgements creates training replications.

## Reproduction

| section | quantity | reported | recomputed | 95% CI | p | n | note |
|---|---|---|---|---|---|---|---|
| perimeters | phase 1 participants (all recorded ratings) | 166 | 166 |  |  | 23012 | before the export filter |
| perimeters | phase 1 ratings (all recorded) | 23012 | 23012 |  |  |  |  |
| perimeters | phase 1 participants after the export filter | 164 | 164 |  |  |  |  |
| perimeters | phase 1 ratings after the export filter | 22712 | 22712 |  |  |  |  |
| perimeters | phase 1 ratings removed by the filter | 300 | 300 |  |  |  | participants 2; reasons ['non finito', 'non finito'] |
| perimeters | phase 1 participants with >= 10 ratings (consensus agreement n) | 161 | 161 |  |  |  |  |
| perimeters | phase 1 participants with >= 3 ratings in each frozen set (LOO n) | 159 | 159 |  |  |  |  |
| perimeters | photographs rated by both architects and non-experts | 599 | 599 |  |  |  | architects cover 599, non-experts 600 |
| perimeters | photographs rated by both high (4-5) and low (1-2) expertise | 600 | 600 |  |  |  |  |
| perimeters | phase 2 participants (ratings, included) | 158 | 158 |  |  |  |  |
| perimeters | phase 2 ratings (included) | 9413 | 9413 |  |  |  |  |
| perimeters | phase 2 comparisons answered (included) | 4736 | 4736 |  |  |  |  |
| perimeters | ties | 726 | 726 |  |  |  |  |
| perimeters | decisive choices | 4010 | 4010 |  |  |  |  |
| perimeters | ratings per image: min / max / mean | 15-22 / 19.7 | 15-22 / 19.7 |  |  |  |  |
| perimeters | phase 2 participants linked to phase 1 by id | 32 | 32 |  |  |  |  |
| perimeters | unlinked: declared Yes / No / NotSure | 16 / 99 / 11 | 16 / 99 / 11 |  |  |  | all values {'No': 99, 'Yes': 16, 'NotSure': 11} |
| selection | photographs with n>=10 and mean>=5 on the complete phase-1 sample | 89 | 89 |  |  |  | identical to frozen AESTHETIC: True |
| selection | rule with top 30%: cutoff mean / selected / equals frozen | 89 | 4.650 / 89 / True |  |  |  | percentile cutoff below 5 → mean threshold binds |
| selection | rule with top 33%: cutoff mean / selected / equals frozen | 89 | 4.603 / 89 / True |  |  |  | percentile cutoff below 5 → mean threshold binds |
| selection | rule with top 35%: cutoff mean / selected / equals frozen | 89 | 4.562 / 89 / True |  |  |  | percentile cutoff below 5 → mean threshold binds |
| selection | rule with top 40%: cutoff mean / selected / equals frozen | 89 | 4.492 / 89 / True |  |  |  | percentile cutoff below 5 → mean threshold binds |
| selection | share of the 600 selected by mean>=5 and n>=10 | 14.8% | 14.8% |  |  |  |  |
| ratings | AESTHETIC − CONTROL per participant (points) | 0.104 | 0.1037 | 0.0291 / 0.1782 | 0.00673 | 158 | one-sample t on participant mean differences; participants with >= 3 ratings in each condition |
| ratings | d_z | 0.22 | 0.218 | 0.061 / 0.376 |  |  |  |
| ratings | BASE − CONTROL per participant | 0.14 | 0.1401 | 0.0684 / 0.2118 | 0.000167 | 158 |  |
| ratings | AESTHETIC − BASE per participant | -0.036 | -0.0364 | -0.1075 / 0.0347 | 0.31325 | 158 |  |
| ratings | AESTHETIC − CONTROL per triplet (participant-centred scores) | 0.105 | 0.1051 | 0.0279 / 0.1822 | 0.00791 | 159 |  |
| ratings | A−C in architects | 0.102 | 0.1021 | -0.0133 / 0.2175 | 0.0817 | 54 |  |
| ratings | A−C in non-experts | 0.056 | 0.0565 | -0.0892 / 0.2022 | 0.4401 | 53 |  |
| ratings | architects − non-experts difference (p) | 0.623 | 0.623 |  |  |  | difference +0.046 |
| ratings | high − low expertise (p) | 0.717 | 0.717 |  |  |  |  |
| ratings | linked − unlinked (No + NotSure) A−C | -0.116 | -0.1163 | -0.2891 / 0.0565 | 0.183 | 32+110 | Welch; the interval spans −0.29/+0.06: not a demonstration of equivalence (MDE for this comparison ≈ ±0.25 points) |
| pairs | AESTHETIC chosen in decisive A–C comparisons (share, n) | 51.3% of 1320 | 51.3% of 1320 |  |  |  |  |
| pairs | half-point share A vs C per participant | None | 0.5076 | 0.4811 / 0.5342 | 0.57 | 158 | t interval over participants; previous reply gave a participant bootstrap 48.69–53.52 |
| pairs | Bradley–Terry OR A vs C (cluster participant) | 1.09 | 1.0899 | 0.9848 / 1.2062 | 0.0957 | 4010 | logistic regression on 'left wins', intercept = position bias; ties excluded |
| pairs | Bradley–Terry OR BASE vs C | 1.133 | 1.1334 | 1.0385 / 1.237 | 0.0053 |  |  |
| pairs | Bradley–Terry OR A vs BASE | 0.962 | 0.9616 | 0.8742 / 1.0576 | 0.4176 |  |  |
| pairs | position bias OR (left) | None | 0.9738 | 0.8933 / 1.0615 | 0.5434 |  | not in the manuscript |
| pairs | Bradley–Terry OR A vs C, clustered by PROMPT (48 clusters) | None | 1.0899 | 0.9503 / 1.2499 | 0.2127 |  | sensitivity: inference about prompts rather than participants |
| pairs | Davidson OR A vs C (all 4736 answers incl. ties) | 1.0893 | 1.0894 | 0.9849 / 1.2049 | 0.0955 | 4736 | independent MLE (analytic gradient, BFGS, converged=True, logLik=-4803.889); interval here cluster-robust by participant with t(157); previous reply: participant bootstrap 0.989-1.204 |
| pairs | Davidson OR BASE vs C | 1.133 | 1.1331 | 1.0382 / 1.2368 | 0.0054 |  |  |
| pairs | Davidson OR A vs BASE | 0.9614 | 0.9614 |  |  |  | derived from the two parameters (BASE reference) |
| pairs | Davidson tie parameter nu | 0.3625 | 0.3625 |  |  |  | tie probability at parity nu/(2+nu) = 0.153; observed tie share 0.153 |
| reliability | phase 2 ICC(1) single rating | 0.239 | 0.239 |  |  | 477 | one-way ANOVA on participant-centred scores; k0=19.73; ICC(k)=0.861 |
| reliability | phase 2 ICC(k) image mean | 0.861 | 0.861 |  |  |  |  |
| reliability | phase 1 ICC(1) (export filter, 164) | 0.138 | 0.138 |  |  | 600 | k0=37.83 |
| reliability | phase 1 ICC(k) (export filter) | 0.858 | 0.858 |  |  |  |  |
| reliability | mean correlation with the aggregate of the others | 0.351 | 0.351 | 0.322 / 0.38 |  | 161 |  |
| reliability | leave-one-rater-out reselection signal (points) | 0.915 | 0.915 | 0.811 / 1.019 |  | 159 | inside each reselection: top set always 89 (164 of 164), CONTROL photographs entering the reselected top: mean 0.1 (removed from the comparison set). NOTE the reselection uses the top-89 by mean, not the frozen rule (n>=10, mean>=5) |
| phase1 | AESTHETIC photographs mean of means (complete sample) | 5.295 | 5.295 |  |  |  |  |
| phase1 | CONTROL photographs mean of means | 4.211 | 4.211 |  |  |  |  |
| phase1 | mean within-photo SD AESTHETIC / CONTROL | 1.444 / 1.556 | 1.444 / 1.556 |  |  |  |  |
| phase1 | Spearman architects vs non-experts (photograph means) | 0.425 | 0.423 |  |  | 599 | export-filter sample |
| phase1 | Spearman high vs low expertise | 0.496 | 0.5 |  |  | 600 |  |
| phase1 | role counts NonExpert/Architect/Student/Engineer/other | 63/58/8/8/29 | {'NonExpert': 63, 'Architect': 58, 'Other': 29, 'ArchitectureStudent': 8, 'Engineer': 8} |  |  |  |  |

## Sensitivities (post-review, exploratory)

| analysis | estimate | 95% CI | p | n | note |
|---|---|---|---|---|---|
| phase 1 ICC on the COMPLETE sample (166, 23012) | 0.138 |  |  |  | ICC(k)=0.860; export-filter values 0.138/0.858 |
| LOO reselection signal on the COMPLETE phase-1 sample (166) | 0.944 | 0.842 / 1.045 |  | 161 | separate sensitivity; the manuscript value 0.915 uses the export filter |
| A−C ratings: without global participant exclusions, >=3 per condition | 0.1295 | 0.0482 / 0.2109 | 0.002 | 167 |  |
| A−C ratings: without global exclusions, >=1 per condition | 0.1258 | 0.0446 / 0.207 | 0.0026 | 168 |  |
| A−C ratings: included sample, >=1 per condition | 0.1037 | 0.0291 / 0.1782 | 0.0067 | 158 |  |
| A−C ratings: responses < 500 ms removed | 0.1037 | 0.0291 / 0.1782 | 0.0067 | 158 | 0 ratings removed |
| A−C ratings: responses < 1000 ms removed | 0.1199 | 0.0414 / 0.1985 | 0.003 | 158 | 571 ratings removed |
| phase 2 participants globally excluded | 18 |  |  |  | reasons: {'non finito': 8, 'non termitano': 1, 'Automatic rule: 64 of 90 answers (71%) excluded as faster than 501 ms, above the 20% limit': 1, 'non ha partecipato': 1, 'non completo': 1, 'q': 1, 'a': 1, 'Automatic rule: 19 of 90 answers (21%) excluded as faster than 501 ms, above the 20% limit': 1, 'Automatic rule: 26 of 90 answers (29%) excluded as faster than 501 ms, above the 20% limit': 1, 'Non completato': 1, 'non completato': 1}; with phase-2 answers: 11 |
| phase 2 included participants with both sessions Completed | 158 |  |  | 158 |  |
| A−C ratings: linear mixed model with crossed random intercepts participant + prompt×seed cell + image (REML) | 0.1011 | 0.016 / 0.1862 | 0.0199 | 9413 | converged=True; variance components {"cell": 0.4355, "image": 0.0704, "participant": 1.05} (labels from the model, corrected 2026-10-03 second pass); residual 1.5431; fit 35s |
| BASE−C ratings: same crossed model | 0.1344 | 0.0493 / 0.2194 | 0.002 |  |  |
| A−BASE ratings: same crossed model | -0.0333 |  |  |  | difference of the two fixed effects; SE not reported here |
| Davidson OR A vs C: participant bootstrap (2000 resamples) | 1.0894 | 0.9821 / 1.2049 |  | 158 participants × 48 prompts | cluster bootstrap over participants, percentile interval |
| Davidson OR BASE vs C: participant bootstrap (2000 resamples) | 1.1331 | 1.0404 / 1.2398 |  | 158 participants × 48 prompts | cluster bootstrap over participants, percentile interval |
| Davidson OR A vs BASE: participant bootstrap (2000 resamples) | 0.9614 | 0.8745 / 1.0561 |  | 158 participants × 48 prompts | cluster bootstrap over participants, percentile interval |
| Davidson OR A vs C: prompt bootstrap (2000 resamples) | 1.0894 | 0.9464 / 1.2394 |  | 158 participants × 48 prompts | cluster bootstrap over prompts, percentile interval |
| Davidson OR BASE vs C: prompt bootstrap (2000 resamples) | 1.1331 | 0.9852 / 1.2928 |  | 158 participants × 48 prompts | cluster bootstrap over prompts, percentile interval |
| Davidson OR A vs BASE: prompt bootstrap (2000 resamples) | 0.9614 | 0.8394 / 1.1012 |  | 158 participants × 48 prompts | cluster bootstrap over prompts, percentile interval |
| Davidson OR A vs C: two-way bootstrap (2000 resamples) | 1.0894 | 0.8991 / 1.3128 |  | 158 participants × 48 prompts | pigeonhole (two-way cluster) bootstrap: participants and prompts resampled independently, observation weight = product of multiplicities (Owen 2007; Owen & Eckles 2012) |
| Davidson OR BASE vs C: two-way bootstrap (2000 resamples) | 1.1331 | 0.949 / 1.351 |  | 158 participants × 48 prompts | pigeonhole (two-way cluster) bootstrap: participants and prompts resampled independently, observation weight = product of multiplicities (Owen 2007; Owen & Eckles 2012) |
| Davidson OR A vs BASE: two-way bootstrap (2000 resamples) | 0.9614 | 0.8023 / 1.1635 |  | 158 participants × 48 prompts | pigeonhole (two-way cluster) bootstrap: participants and prompts resampled independently, observation weight = product of multiplicities (Owen 2007; Owen & Eckles 2012) |
| A−C ratings per participant: two-way (participant × prompt) pigeonhole bootstrap (corrected: outer mean weighted by participant multiplicity) | 0.1037 | -0.024 / 0.2347 |  | 2000 | participants and prompts resampled independently; within-participant means weighted by prompt multiplicity; outer mean weighted by participant multiplicity; drawn participants lacking A or C after resampling are dropped (mean 0.00 per resample). First-pass estimator (ids counted once, superseded): -0.0096 / +0.2145. Compare with the t interval +0.029/+0.178 |

## Definitions

- Participant-level contrast: mean of a participant's ratings of condition A minus mean of condition B, participants with at least 3 ratings in each; one-sample t with t(n−1) interval.
- Bradley–Terry: logistic regression of 'left image wins' on condition indicators (left − right), intercept = left-position bias; decisive choices only; cluster-robust SE by participant, t(G−1).
- Davidson (1970): outcomes left/right/tie with weights e^{η}, 1, ν·e^{η/2} where η = position bias + θ_left − θ_right; θ_CONTROL = 0; MLE with analytic gradient. Cluster-robust interval by participant and three bootstraps (participant, prompt, two-way pigeonhole).
- ICC: one-way random-effects ANOVA on participant-centred scores with the unbalanced-design mean group size k0; degrees of freedom of the within term reduced by the number of centring constants. The design is incomplete (each rater sees a subset); this estimator treats raters as a nuisance removed by centring, not as a crossed factor.
- Leave-one-rater-out: see `loo_signal` — the reselection is the top-89 by the others' means (not the frozen rule with n ≥ 10 and mean ≥ 5), evaluated with the rater's own scores on the reselected top versus the frozen CONTROL photographs not in that top.
- Crossed mixed model: score ~ condition + (1|participant) + (1|prompt×seed cell) + (1|image), REML, statsmodels MixedLM with variance components on a single group.

