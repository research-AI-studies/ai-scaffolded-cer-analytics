"""Render figures from ``outputs/results.json``.

Figures are treated as processed artifacts: they are written to ``figures/``
which is git-ignored (kept offline). Every figure is stamped with a provenance
banner when the underlying data is the illustrative example cohort, so a reader
can never mistake a demonstration plot for an empirical result.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "outputs" / "results.json"
FIG = ROOT / "figures"


def _banner(fig, results: dict) -> None:
    if results.get("data_source") == "example":
        fig.text(0.5, 0.01,
                 "ILLUSTRATIVE DEMONSTRATION - example cohort, not empirical data",
                 ha="center", fontsize=8, color="crimson", style="italic")


def fig_cer_gap(results: dict) -> None:
    cer = results["cer_completion"]
    labels = list(cer.keys())
    vals = [cer[k]["completion"] * 100 for k in labels]
    colors = ["#d62728" if v == 0 else "#2ca02c" for v in vals]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(labels, vals, color=colors)
    ax.set_ylabel("Completion (%)")
    ax.set_ylim(0, 105)
    ax.set_title("CER Component Completion (the reasoning gap)")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.0f}%",
                ha="center", fontsize=9)
    _banner(fig, results)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIG / "fig_cer_gap.png", dpi=200)
    plt.close(fig)


def fig_agent_distribution(results: dict) -> None:
    dist = results["agent_decisions"]["by_action"]
    labels = list(dist.keys())
    vals = [dist[k]["pct"] * 100 for k in labels]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(labels, vals, color="#1f77b4")
    ax.set_ylabel("Share of agent decisions (%)")
    ax.set_title("Agent scaffolding-action distribution")
    for i, v in enumerate(vals):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=9)
    _banner(fig, results)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIG / "fig_agent_distribution.png", dpi=200)
    plt.close(fig)


def fig_probe_vs_errors(results: dict) -> None:
    groups = ROOT / "data" / ("private" if results["data_source"] == "private" else "example")
    import csv
    xs, ys, names = [], [], []
    with (groups / "groups.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            xs.append(float(row["probe_ratio"]) * 100)
            ys.append(int(row["post_test_errors"]))
            names.append(row["group"])
    rho = results["correlations"]["probe_ratio_vs_errors"]["rho"]
    p = results["correlations"]["probe_ratio_vs_errors"]["p"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(xs, ys, color="#ff7f0e", s=60, zorder=3)
    for x, y, n in zip(xs, ys, names):
        ax.annotate(n, (x, y), textcoords="offset points", xytext=(5, 4), fontsize=8)
    ax.set_xlabel("Probe ratio (%)")
    ax.set_ylabel("Post-test errors")
    ax.set_title(f"Probe ratio vs post-test errors (Spearman rho = {rho}, p = {p})")
    _banner(fig, results)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIG / "fig_probe_vs_errors.png", dpi=200)
    plt.close(fig)


def main() -> None:
    if not RESULTS.exists():
        raise SystemExit("outputs/results.json missing - run src/analyze.py first.")
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    FIG.mkdir(parents=True, exist_ok=True)
    fig_cer_gap(results)
    fig_agent_distribution(results)
    fig_probe_vs_errors(results)
    print(f"Wrote figures to {FIG} (data_source={results['data_source']})")


if __name__ == "__main__":
    main()
