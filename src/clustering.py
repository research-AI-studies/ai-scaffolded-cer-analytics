"""Transparent, deterministic engagement clustering of inquiry groups.

Rather than a black-box clusterer, groups are assigned to three engagement
bands from a standardized composite of scaffolding demand (agent decisions) and
help-seeking volume (help requests). Two design choices keep the method robust
and reviewer-auditable:

  1. Counts are log1p-transformed before standardizing, so a single extreme
     help-seeker (e.g. a gaming group) does not dominate the scale and collapse
     the remaining groups into one band.
  2. Bands are cut at the composite's tertiles (33.3rd / 66.7th percentiles),
     which always yields three non-empty, balanced clusters:
       - "Independent"     : lowest third of composite engagement
       - "Moderate"        : middle third
       - "Heavy dependent" : top third
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _z_log(series: pd.Series) -> pd.Series:
    logged = np.log1p(series.astype(float))
    sd = logged.std(ddof=0)
    if sd == 0:
        return logged * 0.0
    return (logged - logged.mean()) / sd


def assign_clusters(groups: pd.DataFrame) -> dict:
    df = groups.copy()
    df["composite"] = _z_log(df["agent_decisions"]) + _z_log(df["help_requests"])

    low_cut = float(df["composite"].quantile(1 / 3))
    high_cut = float(df["composite"].quantile(2 / 3))

    def band(v: float) -> str:
        if v <= low_cut:
            return "Independent"
        if v > high_cut:
            return "Heavy dependent"
        return "Moderate"

    df["computed_cluster"] = df["composite"].map(band)
    members: dict[str, list[str]] = {"Independent": [], "Moderate": [], "Heavy dependent": []}
    for row in df.itertuples():
        members[row.computed_cluster].append(row.group)

    # Agreement with the illustrative labels shipped in the cohort, if present.
    agreement = None
    if "cluster" in df.columns:
        agree = int((df["cluster"] == df["computed_cluster"]).sum())
        agreement = {"matches": agree, "n": int(len(df)),
                     "rate": round(agree / len(df), 4)}

    return {
        "method": "log1p-standardized composite (z[log agent_decisions] + "
                  "z[log help_requests]); tertile bands",
        "cutpoints": {"low_tertile": round(low_cut, 4), "high_tertile": round(high_cut, 4)},
        "members": members,
        "per_group": {row.group: {"composite": round(float(row.composite), 4),
                                  "computed_cluster": row.computed_cluster}
                      for row in df.itertuples()},
        "agreement_with_shipped_labels": agreement,
    }
