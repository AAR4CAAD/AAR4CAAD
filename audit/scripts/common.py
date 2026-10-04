"""
Shared helpers of the revision-12 audit (analysis/audit_rev12). Post-review analyses, not preregistered.

Every script writes only inside analysis/audit_rev12/outputs and analysis/audit_rev12/logs. Historical results
(analysis/*_report, analysis/figures, analysis/metrics) are read, never modified.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import time
import zipfile

import numpy as np
import pandas as pd

AUDIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT = os.path.dirname(AUDIT)                 # repository root (audit/ sits at the root of the reviewer repository)
ANALYSIS = os.path.join(PROJECT, "analysis")
OUT = os.path.join(AUDIT, "outputs")
LOGS = os.path.join(AUDIT, "logs")
os.makedirs(OUT, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)

# the only export used by the audit (the one of the manuscript and of the previous reply)
EXPORT_ZIP = os.environ.get("ARCH300_EXPORT", os.path.join(PROJECT, "data", "export"))  # anonymised export folder of this repository (a zip path is also accepted)
EXPORT_SHA256_EXPECTED = "ea0bdbf6faa91396019e31db97f81784957bd80bd84342179670b5cdbc055d1c"
# the later export that also lists the paired-seed replication adapters and their 960 images (human tables must coincide)
EXPORT_REP_ZIP = os.environ.get("ARCH300_EXPORT_REP", os.path.join(PROJECT, "data", "export"))  # the anonymised export already lists the replication runs
# the package received for the audit (prompt, reviews, previous reply with attachments)
PACKAGE = os.environ.get("AAR_PACKAGE", os.path.join(AUDIT, "inputs", "package"))  # not redistributed (review texts and manuscript drafts)
PREVIOUS_REPLY = os.path.join(AUDIT, "inputs", "previous_reply")  # attachments of the previous technical reply (derived data, no personal information)

SEED = 20261003  # bootstrap seed of the audit (fixed before any result)

ORIGINAL = {"RUN-AESTHETIC-4": ("AESTHETIC", 1254), "RUN-CONTROL-4": ("CONTROL", 9865)}
REPLICATION_EXCLUDED = ["REP-AES-S1254-R"]  # determinism re-run of the original AESTHETIC seed, not a new realisation
PHOTO = ["brightness", "contrast", "saturation", "colorfulness", "warmth", "sharpness", "detail", "sky_brightness", "dark_share", "bright_share"]
FRAMING = ["whole_building", "low_angle", "sunny", "vintage_photo", "real_photo", "people", "cars", "greenery", "water", "urban", "interior"]
CONTENT = ["iconic_design", "complex_form", "curved_organic", "monumental", "contemporary", "glass", "concrete", "wood", "white", "colourful"]
DESCRIPTORS = PHOTO + FRAMING + CONTENT


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def export_folder(zip_path=EXPORT_ZIP):
    """Extracts an export once (into a cache folder named after the zip's hash) and returns the folder; a folder is used as is."""
    if os.path.isdir(zip_path):
        return zip_path
    digest = sha256(zip_path)
    if zip_path == EXPORT_ZIP and digest != EXPORT_SHA256_EXPECTED:
        print(f"WARNING: export sha256 {digest} differs from the expected {EXPORT_SHA256_EXPECTED}", file=sys.stderr)
    folder = os.path.join(tempfile.gettempdir(), f"arch300_export_{digest[:12]}")
    if not os.path.isdir(os.path.join(folder, "aggregates")):
        os.makedirs(folder, exist_ok=True)
        zipfile.ZipFile(zip_path).extractall(folder)
    return folder


class Export:
    def __init__(self, zip_path=EXPORT_ZIP):
        self.zip = zip_path
        self.folder = export_folder(zip_path)

    def csv(self, name, **kw):
        return pd.read_csv(os.path.join(self.folder, name), **kw)

    def json(self, name):
        with open(os.path.join(self.folder, name), encoding="utf-8") as f:
            return json.load(f)


def as_bool(s):
    return s.astype(str).str.lower().eq("true")


def logit(p, eps=1e-4):
    p = np.clip(np.asarray(p, float), eps, 1 - eps)
    return np.log(p / (1 - p))


def descriptor_matrix(cov, ids):
    """Raw descriptor matrix (31 columns + elegant) for the given ids, CLIP attributes as logits — the historical transform."""
    z = cov.loc[ids, DESCRIPTORS + ["elegant"]].astype(float).copy()
    for c in FRAMING + CONTENT + ["elegant"]:
        z[c] = logit(z[c])
    return z


class Log:
    """Appends to logs/<script>.log and echoes to stdout."""

    def __init__(self, name):
        self.path = os.path.join(LOGS, f"{name}.log")
        self.f = open(self.path, "a", encoding="utf-8")
        self(f"=== {name} started {time.strftime('%Y-%m-%dT%H:%M:%S%z')} python {sys.version.split()[0]} numpy {np.__version__} pandas {pd.__version__}")

    def __call__(self, *a):
        s = " ".join(str(x) for x in a)
        try:
            print(s)
        except UnicodeEncodeError:
            print(s.encode("ascii", "replace").decode())
        self.f.write(s + "\n")
        self.f.flush()


def write_md(name, lines):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return p


def fmt(x, nd=4):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:+.{nd}f}" if isinstance(x, (float, np.floating)) else str(x)
