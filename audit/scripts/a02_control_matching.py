"""
Audit step 2 — how CONTROL was really built (prompt section 4, first part).

The platform code (src/.../Services/TrainingDatasetService.cs, SampleControl + Common/DeterministicRandom.cs) is ported here
line by line: xoshiro256** seeded with SplitMix64, Fisher–Yates shuffle of the pool ordered by image_asset_id, stratum-count
matching on BuildingType|Style, relaxation to BuildingType, random fill. The re-execution with the stored seed 345145722 is
compared with the frozen CONTROL-v1/v2 membership AND order. It also shows that the algorithm matches STRATUM COUNTS, not
photograph pairs: no 1:1 pair map ever existed.

Writes outputs/control_construction.csv (one row per CONTROL photograph with its stratum and the AESTHETIC photographs of the same
stratum), outputs/control_composition.csv, outputs/report_control.md.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

from common import OUT, Export, Log, as_bool, write_md

log = Log("a02_control_matching")
E = Export()
MASK = (1 << 64) - 1


class DeterministicRandom:
    def __init__(self, seed):
        x = seed & MASK
        self.s = []
        for _ in range(4):
            x = (x + 0x9E3779B97F4A7C15) & MASK
            z = x
            z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
            z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
            self.s.append(z ^ (z >> 31))

    @staticmethod
    def rotl(x, k):
        return ((x << k) | (x >> (64 - k))) & MASK

    def next_u64(self):
        s0, s1, s2, s3 = self.s
        result = (self.rotl((s1 * 5) & MASK, 7) * 9) & MASK
        t = (s1 << 17) & MASK
        s2 ^= s0; s3 ^= s1; s1 ^= s2; s0 ^= s3; s2 ^= t; s3 = self.rotl(s3, 45)
        self.s = [s0, s1, s2, s3]
        return result

    def next_int(self, max_exclusive):
        bound = max_exclusive
        threshold = ((1 << 64) - bound) % bound
        while True:
            r = self.next_u64()
            if r >= threshold:
                return r % bound

    def shuffle(self, lst):
        for i in range(len(lst) - 1, 0, -1):
            j = self.next_int(i + 1)
            lst[i], lst[j] = lst[j], lst[i]


def sample_control(pool, reference, variables, seed, key):
    """pool/reference: lists of dicts with 'id'; key(img, vars) -> stratum string. Returns [(img, reason)]."""
    rng = DeterministicRandom(seed)
    n = len(reference)
    available = sorted(pool, key=lambda i: i["id"])
    rng.shuffle(available)
    result, used = [], set()

    def take(cands, count, reason):
        for c in cands:
            if count <= 0: break
            if c["id"] not in used:
                used.add(c["id"]); result.append((c, reason)); count -= 1

    # targets: strata of the reference, ordered by key (ordinal)
    groups = {}
    for r in reference:
        groups.setdefault(key(r, variables), []).append(r)
    deficits = []
    for k in sorted(groups):
        need = len(groups[k])
        before = len(result)
        take([i for i in available if key(i, variables) == k], need, f"matched: {k}")
        got = len(result) - before
        if got < need: deficits.append((groups[k][0], need - got))
    for kk in range(len(variables) - 1, 0, -1):
        if not deficits: break
        subset = variables[:kk]
        nxt = []
        for ref_img, missing in deficits:
            k = key(ref_img, subset)
            before = len(result)
            take([i for i in available if key(i, subset) == k], missing, f"matched (relaxed to {','.join(subset)}): {k}")
            got = len(result) - before
            if got < missing: nxt.append((ref_img, missing - got))
        deficits = nxt
    take(available, n - len(result), "matched: random fill")
    return result


# ---------------------------------------------------------------- data as at 2026-09-27 13:39 UTC
SI = E.csv("source_images.csv"); M = E.csv("image_metadata.csv").set_index("image_code")
A_ds = E.csv("aesthetic_dataset.csv"); C_ds = E.csv("control_dataset.csv")
A1 = A_ds[A_ds.dataset_code == "AESTHETIC-v1"].sort_values("sort_order"); C1 = C_ds[C_ds.dataset_code == "CONTROL-v1"].sort_values("sort_order")
A2 = A_ds[A_ds.dataset_code == "AESTHETIC-v2"].sort_values("sort_order"); C2 = C_ds[C_ds.dataset_code == "CONTROL-v2"].sort_values("sort_order")
log("v1 == v2 membership: AESTHETIC", set(A1.image_code) == set(A2.image_code), "CONTROL", set(C1.image_code) == set(C2.image_code), "| same order:", list(C1.image_code) == list(C2.image_code))
meta = C1.iloc[0]
log("stored: method", meta.control_method, "variables", meta.matching_variables, "seed", meta.random_seed, "reference", meta.reference_dataset, "excluded_reference", meta.excluded_reference_images)
variables = str(meta.matching_variables).split(",")
seed = int(meta.random_seed)
imgs = []
for _, r in SI.iterrows():
    m = M.loc[r.image_code]
    imgs.append(dict(id=int(r.image_asset_id), code=r.image_code, BuildingType=m.building_type if isinstance(m.building_type, str) else None, Style=m.architectural_style if isinstance(m.architectural_style, str) else None,
                     Period=m.period, Continent=m.continent, Country=m.country, active=str(r.is_active).lower() == "true"))
by_code = {i["code"]: i for i in imgs}
aes_codes = list(A1.image_code)
reference = [by_code[c] for c in aes_codes]
pool = [i for i in imgs if i["active"] and i["code"] not in set(aes_codes)]


def key(img, vars_):
    return " | ".join(f"{v}={img.get(v) if img.get(v) is not None else '∅'}" for v in vars_)


picked = sample_control(pool, reference, variables, seed, key)
re_codes = [p[0]["code"] for p in picked]; re_reasons = [p[1] for p in picked]
hist_codes = list(C1.image_code); hist_reasons = list(C1.reason)
same_set = set(re_codes) == set(hist_codes); same_order = re_codes == hist_codes; same_reasons = re_reasons == hist_reasons
log("RE-EXECUTION: same membership", same_set, "| same order", same_order, "| same reasons", same_reasons, "| n", len(re_codes))
if not same_set:
    log("  only historical:", sorted(set(hist_codes) - set(re_codes)), " only re-executed:", sorted(set(re_codes) - set(hist_codes)))
# NOTE on metadata: the export metadata are the current ones; the audit log records no metadata change (no ImageAsset/ImageMetadata
# events except corpus.extended), so the current BuildingType/Style are those of 2026-09-27.

# ---------------------------------------------------------------- strata, not pairs
rows = []
A_key2 = {c: key(by_code[c], variables) for c in aes_codes}
A_key1 = {c: key(by_code[c], variables[:1]) for c in aes_codes}
for (img, reason), hist_reason in zip(picked, hist_reasons):
    if reason.startswith("matched (relaxed"):
        stratum, k = "type_only", key(img, variables[:1]); mates = [c for c in aes_codes if A_key1[c] == k]
    elif reason == "matched: random fill":
        stratum, k, mates = "random_fill", "", []
    else:
        stratum, k = "type_and_style", key(img, variables); mates = [c for c in aes_codes if A_key2[c] == k]
    rows.append(dict(control_image=img["code"], sort_order=len(rows), stratum=stratum, stratum_key=k, reason_recorded=hist_reason, reason_reexecuted=reason,
                     aesthetic_in_same_stratum=";".join(mates), n_aesthetic_in_stratum=len(mates),
                     building_type=img["BuildingType"], style=img["Style"], period=img["Period"], area=img["Continent"], country=img["Country"]))
CC = pd.DataFrame(rows)
CC.to_csv(os.path.join(OUT, "control_construction.csv"), index=False)
counts = CC.stratum.value_counts().to_dict()
log("strata:", counts)
# how many AESTHETIC photographs have at least one CONTROL in their exact stratum / type stratum
ctl_keys2 = set(CC[CC.stratum == "type_and_style"].stratum_key); ctl_keys1 = set(CC[CC.stratum == "type_only"].stratum_key)
a_cov2 = sum(A_key2[c] in ctl_keys2 for c in aes_codes); a_cov1 = sum(A_key1[c] in ctl_keys1 for c in aes_codes)
# AESTHETIC strata that could NOT be matched (deficits): singleton strata with no other photo of the same type+style in the pool
pool_keys2 = pd.Series([key(i, variables) for i in pool]).value_counts(); pool_keys1 = pd.Series([key(i, variables[:1]) for i in pool]).value_counts()
A_strata = pd.Series(list(A_key2.values())).value_counts()
deficit2 = {k: int(v - pool_keys2.get(k, 0)) for k, v in A_strata.items() if pool_keys2.get(k, 0) < v}
log("AESTHETIC type+style strata:", len(A_strata), "| strata fully matchable in the pool:", int((A_strata <= pool_keys2.reindex(A_strata.index).fillna(0)).sum()), "| total deficit:", sum(deficit2.values()))

# ---------------------------------------------------------------- composition and imbalance (period, area, type, style, industrial)
Mx = M.copy(); Mx["set"] = np.where(Mx.index.isin(aes_codes), "AESTHETIC", np.where(Mx.index.isin(hist_codes), "CONTROL", "other"))
comp = []
for var in ["period", "continent", "industrial_or_nonindustrial"]:
    ct = pd.crosstab(Mx[Mx.set != "other"][var], Mx[Mx.set != "other"].set)
    chi = stats.chi2_contingency(ct)[1] if ct.shape[0] > 1 else np.nan
    for cat, r in ct.iterrows():
        comp.append(dict(variable=var, category=cat, AESTHETIC=int(r.get("AESTHETIC", 0)), CONTROL=int(r.get("CONTROL", 0)), chi2_p_variable=round(chi, 4)))
    log(var, "chi2 p", round(chi, 4), ct.to_dict())
for var in ["building_type", "architectural_style", "country"]:
    a_, c_ = set(Mx[Mx.set == "AESTHETIC"][var].dropna()), set(Mx[Mx.set == "CONTROL"][var].dropna())
    comp.append(dict(variable=var, category="distinct values A / C / shared", AESTHETIC=len(a_), CONTROL=len(c_), chi2_p_variable=len(a_ & c_)))
    log(var, "distinct", len(a_), len(c_), "shared", len(a_ & c_))
post90 = lambda s: int(Mx[(Mx.set == s) & Mx.period.isin(["1990-2009", "2010-today"])].shape[0])
eur = lambda s: int(Mx[(Mx.set == s) & (Mx.continent == "Europe")].shape[0])
ind = lambda s: int(Mx[(Mx.set == s) & (Mx.industrial_or_nonindustrial == "industrial")].shape[0])
pd.DataFrame(comp).to_csv(os.path.join(OUT, "control_composition.csv"), index=False)
# by stratum: composition of the three CONTROL subgroups vs their AESTHETIC counterparts
sub = []
for st in ["type_and_style", "type_only", "random_fill"]:
    cc = CC[CC.stratum == st]
    sub.append(dict(stratum=st, n=len(cc), post_1990=int(cc.period.isin(["1990-2009", "2010-today"]).sum()), europe=int((cc.area == "Europe").sum()), industrial=int(M.loc[cc.control_image].industrial_or_nonindustrial.eq("industrial").sum())))
sub = pd.DataFrame(sub)
log(sub.to_string())

# ---------------------------------------------------------------- Tab. 1 check
tab1 = {"AESTHETIC": dict(periods=[int(Mx[(Mx.set == 'AESTHETIC') & (Mx.period == p)].shape[0]) for p in ["1919-1945", "1946-1969", "1970-1989", "1990-2009", "2010-today"]], countries=Mx[Mx.set == 'AESTHETIC'].country.nunique(), europe=eur("AESTHETIC"), types=Mx[Mx.set == 'AESTHETIC'].building_type.nunique(), industrial=ind("AESTHETIC"), licences=Mx[Mx.set == 'AESTHETIC'].license.nunique(), ccbysa4=int((Mx[Mx.set == 'AESTHETIC'].license == 'CC BY-SA-4.0').sum())),
        "CONTROL": dict(periods=[int(Mx[(Mx.set == 'CONTROL') & (Mx.period == p)].shape[0]) for p in ["1919-1945", "1946-1969", "1970-1989", "1990-2009", "2010-today"]], countries=Mx[Mx.set == 'CONTROL'].country.nunique(), europe=eur("CONTROL"), types=Mx[Mx.set == 'CONTROL'].building_type.nunique(), industrial=ind("CONTROL"), licences=Mx[Mx.set == 'CONTROL'].license.nunique(), ccbysa4=int((Mx[Mx.set == 'CONTROL'].license == 'CC BY-SA-4.0').sum()))}
log("Tab.1 recomputed:", json.dumps(tab1))
log("licence values:", Mx.license.value_counts().to_dict())

L = ["# CONTROL: how it was built, re-executed from the platform algorithm (audit rev12)", "",
     f"Stored parameters (control_dataset.csv): method `{meta.control_method}`, matching variables `{meta.matching_variables}`, seed `{seed}`, reference `{meta.reference_dataset}`, reference images excluded from the pool `{meta.excluded_reference_images}`. "
     f"Pool = active photographs not in AESTHETIC-v1 ({len(pool)}), ordered by image_asset_id, shuffled once with xoshiro256**(SplitMix64({seed})).", "",
     "## Re-execution", "",
     f"- Same 89 photographs: **{same_set}**; same order (sort_order 0–88): **{same_order}**; same recorded reasons: **{same_reasons}**.",
     f"- v1 and v2 datasets have identical membership and order (v2 only re-snapshots the captions): {set(C1.image_code) == set(C2.image_code) and list(C1.image_code) == list(C2.image_code)}.",
     "- The export carries the current BuildingType/Style; the audit log has no metadata-edit event for photographs after import, so the strata used here are those of 2026-09-27 13:39 UTC.", "",
     "## What the algorithm does — and does not do", "",
     "`SampleControl(MatchedControl)` matches **stratum counts**, not photographs: for every stratum `BuildingType | Style` of the 89 AESTHETIC photographs (ordered by key) it takes the same number of pool photographs from that stratum (in shuffled order); "
     "strata with a deficit are refilled by `BuildingType` alone; the remainder is random. **No photograph-to-photograph pairing is created or stored**: the '1:1 matching' of the manuscript and the '61 pairs' of the previous reply do not correspond to any recorded object. "
     "The recoverable unit is the stratum. Row order (`sort_order`) is the order of the strata by key, not a pairing.", "",
     f"| CONTROL subgroup | n | AESTHETIC photographs sharing the stratum | post-1990 | Europe | industrial |", "|---|---|---|---|---|---|"]
for _, r in sub.iterrows():
    L.append(f"| {r.stratum} | {r.n} | {'same type and style' if r.stratum == 'type_and_style' else 'same building type' if r.stratum == 'type_only' else 'none (random)'} | {r.post_1990} | {r.europe} | {r.industrial} |")
L += ["", f"AESTHETIC has {len(A_strata)} distinct type+style strata; {int((A_strata <= pool_keys2.reindex(A_strata.index).fillna(0)).sum())} could be matched completely in the pool; the deficit of {sum(deficit2.values())} photographs was refilled by type ({counts.get('type_only', 0)}) and at random ({counts.get('random_fill', 0)}). "
      f"AESTHETIC photographs with at least one CONTROL in their exact stratum: {a_cov2} of 89; with at least one CONTROL of the same type (relaxed strata): {a_cov1}.", "",
      "## Composition (whole sets)", "",
      f"- Period, post-1990: AESTHETIC {post90('AESTHETIC')} vs CONTROL {post90('CONTROL')} (of 89 each). Europe: {eur('AESTHETIC')} vs {eur('CONTROL')}. Industrial: {ind('AESTHETIC')} vs {ind('CONTROL')}.",
      f"- Tab. 1 recomputed: {json.dumps(tab1)}.",
      "- Period and area are NOT matching variables; type and style are matched only for the stratum-count subgroups. The review's observation that 'exact 1:1 matching would give identical type distributions' is correct; the recorded procedure never promised that.", "",
      "## Consequence for the manuscript", "",
      "Replace 'abbinate 1:1 per tipologia e stile' with: 'controllo di pari numerosità (89) estratto dalle fotografie non selezionate, con riproduzione dei conteggi per strato tipologia×stile dove possibile "
      f"({counts.get('type_and_style', 0)} fotografie), rilassato alla sola tipologia ({counts.get('type_only', 0)}) e completato a caso ({counts.get('random_fill', 0)}); seed {seed}'. Period and geography were not controlled (sensitivity in `report_direction_adjusted.md`).", ""]
write_md("report_control.md", L)
json.dump(dict(same_membership=same_set, same_order=same_order, same_reasons=same_reasons, strata=counts, seed=seed, pool=len(pool)), open(os.path.join(OUT, "control_reexecution.json"), "w"), indent=1)
