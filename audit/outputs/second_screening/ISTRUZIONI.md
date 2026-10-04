# Second blind screening — instructions for the independent screener

Status: retrospective verification requested by the reviewer. It does not change the images shown to the participants in 2026; it measures the agreement of an independent screener with the original screening.

## What you receive

- `images/S001.jpg … S576.jpg`: the 576 generated images at full size (1216 × 832), in random order, with neutral codes. Nothing in the file name or the image reveals the model condition, the prompt or the seed.
- `defect_sheet.csv`: one row per image with empty columns.

## What you must not have

- the key (condition / prompt / seed per code) — it is kept by the audit in a separate file and opened only after your sheet is returned;
- the original screening decisions.

## Task

Look at every image once, in the given order, and mark with `1` each defect category that is clearly present (leave empty otherwise). Categories are those of the original review rule v1 (`generated_images.review_defects`):
- **Perspective**: implausible or broken perspective, inconsistent vanishing lines, leaning or warped building volumes.
- **Deformation**: deformed structural elements (windows, columns, roofs, stairs), melted or duplicated parts, impossible geometry.
- **WrongSubject**: the image does not show a building/architecture as the main subject.
- **Artefacts**: rendering artefacts (noise, smearing, text/logo fragments, split images).
- **Other**: any other defect that in your judgement would exclude the image from a human aesthetic evaluation (describe it in `note`).
Mark defects, not taste: 'ugly' is not a defect. Spend about the same time on every image; do not go back to compare images.

## What will be computed afterwards

- Agreement with the original screening (48 flagged images: {'Perspective': 23, 'Deformation': 21, 'Artefacts': 3, 'WrongSubject': 2}) per image and per category: Cohen's κ, prevalence of flags per condition in your sheet (the original had BASE 21, AESTHETIC 14, CONTROL 13).
- Whether the triplet-exclusion rule applied to your flags would have excluded a different set of triplets, and the human contrasts recomputed on the triplets that survive BOTH screenings (sensitivity, not a replacement of the original analysis).

The original screening was done by one researcher who knew the study; you do not know the conditions. The comparison is therefore an agreement study between a blind and an informed-but-condition-masked rater, declared as retrospective.
