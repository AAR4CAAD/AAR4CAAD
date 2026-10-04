# Controlled-caption experiment — analysis (DRY RUN on existing adapters: numbers meaningless, code-path test only)

Direction frozen (d = 0.2352); P = (e_A − e_C)·u per cell; intervals: bootstrap over the 48 prompts. Three quantities kept separate: estimate in the neutral regime, its uncertainty, paired per-cell difference between the original and the neutral regime.

| seed | quantity | estimate | 95% CI | p | R |
|---|---|---|---|---|---|
| 1254 | neutral regime: P_s | +0.0435 | +0.0275 / +0.0615 | 0.0000 | 0.185 |
| 1254 | original regime: P_s | +0.0435 | +0.0279 / +0.0612 | 0.0000 | 0.185 |
| 1254 | paired difference original − neutral | +0.0000 | +0.0000 / +0.0000 | 2.0000 |  |
| 9865 | neutral regime: P_s | +0.0412 | +0.0261 / +0.0576 | 0.0000 | 0.175 |
| 9865 | original regime: P_s | +0.0412 | +0.0255 / +0.0579 | 0.0000 | 0.175 |
| 9865 | paired difference original − neutral | +0.0000 | +0.0000 / +0.0000 | 2.0000 |  |
| 42160 | neutral regime: P_s | +0.0504 | +0.0350 / +0.0681 | 0.0000 | 0.214 |
| 42160 | original regime: P_s | +0.0504 | +0.0357 / +0.0676 | 0.0000 | 0.214 |
| 42160 | paired difference original − neutral | +0.0000 | +0.0000 / +0.0000 | 2.0000 |  |
| pooled | neutral regime: mean of the three seeds | +0.0451 | +0.0318 / +0.0587 | 0.0000 | 0.192 |
| pooled | original regime: mean of the three seeds | +0.0451 | +0.0323 / +0.0595 | 0.0000 | 0.192 |
| pooled | paired difference, mean of the three seeds | +0.0000 | +0.0000 / +0.0000 | 2.0000 |  |

Category (protocol §4, revised): **maintained (neutral contrast > 0; difference between regimes not distinguishable from zero)**. Three seeds individually > 0: True.

Reading rules fixed in advance: a neutral-regime interval that includes zero is 'not distinguishable from zero', not 'lost'; the captions are called 'necessary' only if the paired difference between regimes is > 0 AND the neutral contrast is not distinguishable from zero; 'maintained' says that the corpora differ under common captions in this configuration, not that beauty is transferred.

| descriptors | estimate | 95% CI | original |
|---|---|---|---|
| r(x, a−c) under common captions | +0.707 | +0.563 / +0.824 | +0.707 |
