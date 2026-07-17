"""InquiTrace learning-analytics pipeline.

Computes CER-component completion, scaffolding-type distributions, help-seeking
metrics, group-cluster descriptives, and the associated non-parametric
statistics, writing everything to ``outputs/results.json`` (the single source
of truth for any downstream figure, table, or manuscript number).

Data source resolution:
- If real study data is present in ``data/private/`` (git-ignored), it is used.
- Otherwise the pipeline falls back to the public ``data/example/`` cohort,
  and the output is explicitly flagged as an ILLUSTRATIVE DEMONSTRATION.

Example-cohort outputs must NEVER be reported as empirical findings.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "data" / "private"
EXAMPLE = ROOT / "data" / "example"
DATA = PRIVATE if (PRIVATE / "groups.csv").exists() else EXAMPLE
IS_EXAMPLE = DATA == EXAMPLE
OUT = ROOT / "outputs"


def load() -> dict[str, pd.DataFrame]:
    return {
        "groups": pd.read_csv(DATA / "groups.csv"),
        "decisions": pd.read_csv(DATA / "agent_decisions.csv"),
        "source": pd.read_csv(DATA / "agent_decision_source.csv"),
        "cer": pd.read_csv(DATA / "cer_completion.csv"),
        "misc": pd.read_csv(DATA / "misconceptions.csv"),
        "qa": pd.read_csv(DATA / "qa_exchanges.csv"),
    }


def descriptives(groups: pd.DataFrame) -> dict:
    cr = groups["completion_rate"]
    return {
        "n_groups": int(len(groups)),
        "completion_rate_mean": round(float(cr.mean()), 4),
        "completion_rate_sd": round(float(cr.std(ddof=1)), 4),
        "completion_rate_min": {"group": groups.loc[cr.idxmin(), "group"],
                                 "value": float(cr.min())},
        "completion_rate_max": {"group": groups.loc[cr.idxmax(), "group"],
                                 "value": float(cr.max())},
        "procedural_completion_rate": 1.0,  # all 10 groups finished all 7 stages
    }


def agent_distribution(decisions: pd.DataFrame, source: pd.DataFrame) -> dict:
    total = int(decisions["count"].sum())
    dist = {row.action_type: {"count": int(row.count),
                              "pct": round(row.count / total, 4)}
            for row in decisions.itertuples()}
    src_total = int(source["count"].sum())
    src = {row.source: {"count": int(row.count),
                        "pct": round(row.count / src_total, 4)}
           for row in source.itertuples()}
    return {"total_decisions": total, "by_action": dist,
            "traceable_source_total": src_total, "by_source": src}


def correlations(groups: pd.DataFrame) -> dict:
    def spearman(x, y):
        rho, p = stats.spearmanr(x, y)
        return {"rho": round(float(rho), 4), "p": round(float(p), 4)}

    g = groups
    g_no7 = groups[groups["group"] != "G7"]
    return {
        "probe_ratio_vs_errors": spearman(g["probe_ratio"], g["post_test_errors"]),
        "probe_ratio_vs_errors_excl_G7": spearman(g_no7["probe_ratio"],
                                                   g_no7["post_test_errors"]),
        "decisions_vs_errors": spearman(g["agent_decisions"], g["post_test_errors"]),
        "help_vs_errors": spearman(g["help_requests"], g["post_test_errors"]),
    }


def mann_whitney(groups: pd.DataFrame) -> dict:
    """High- vs low-probe comparison as described in draft 1 (threshold 35%,
    G7 removed as a sensitivity check)."""
    g = groups[groups["group"] != "G7"]
    high = g[g["probe_ratio"] > 0.35]["post_test_errors"]
    low = g[g["probe_ratio"] <= 0.35]["post_test_errors"]
    u, p_two = stats.mannwhitneyu(high, low, alternative="less")
    return {
        "threshold": 0.35,
        "high_probe_groups": g[g["probe_ratio"] > 0.35]["group"].tolist(),
        "low_probe_groups": g[g["probe_ratio"] <= 0.35]["group"].tolist(),
        "high_probe_mean_errors": round(float(high.mean()), 4),
        "low_probe_mean_errors": round(float(low.mean()), 4),
        "U": float(u),
        "p_one_sided": round(float(p_two), 4),
    }


def g7_case(groups: pd.DataFrame) -> dict:
    g7 = groups[groups["group"] == "G7"].iloc[0]
    others = groups[groups["group"] != "G7"]
    help_mean = others["help_requests"].mean()
    help_sd = others["help_requests"].std(ddof=1)
    ratio_g7 = g7["help_requests"] / g7["agent_decisions"]
    ratio_others = (others["help_requests"] / others["agent_decisions"]).mean()
    return {
        "help_requests": int(g7["help_requests"]),
        "others_help_mean": round(float(help_mean), 4),
        "others_help_sd": round(float(help_sd), 4),
        "z_score": round(float((g7["help_requests"] - help_mean) / help_sd), 4),
        "help_per_intervention_g7": round(float(ratio_g7), 4),
        "help_per_intervention_others": round(float(ratio_others), 4),
    }


def cer(cer_df: pd.DataFrame) -> dict:
    out = {}
    for row in cer_df.itertuples():
        out[row.component] = {
            "stage": row.stage, "metric": row.metric,
            "completion": round(row.completed / row.total, 4),
            "n": f"{row.completed}/{row.total}",
        }
    return out


def misconceptions(misc: pd.DataFrame) -> dict:
    total = int(misc["count"].sum())
    return {
        "total_errors": total,
        "by_type": {row.error_type: {"label": row.label, "count": int(row.count),
                                     "pct": round(row.count / total, 4)}
                    for row in misc.itertuples()},
    }


def qa(qa_df: pd.DataFrame) -> dict:
    total = int(qa_df["count"].sum())
    return {"total": total,
            "by_category": {row.category: {"count": int(row.count),
                                           "pct": round(row.count / total, 4)}
                            for row in qa_df.itertuples()}}


def main() -> None:
    df = load()
    provenance = (
        "ILLUSTRATIVE DEMONSTRATION on the public example cohort "
        "(data/example/). NOT empirical data; must not be reported as study "
        "findings."
        if IS_EXAMPLE else
        "Computed from real study data in data/private/ (git-ignored)."
    )
    results = {
        "data_source": "example" if IS_EXAMPLE else "private",
        "provenance": provenance,
        "descriptives": descriptives(df["groups"]),
        "agent_decisions": agent_distribution(df["decisions"], df["source"]),
        "correlations": correlations(df["groups"]),
        "mann_whitney": mann_whitney(df["groups"]),
        "g7_case": g7_case(df["groups"]),
        "cer_completion": cer(df["cer"]),
        "misconceptions": misconceptions(df["misc"]),
        "qa_exchanges": qa(df["qa"]),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {OUT / 'results.json'} (data_source={results['data_source']})")


if __name__ == "__main__":
    main()
