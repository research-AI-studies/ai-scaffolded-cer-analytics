"""Render schematic figures (system architecture, CER-mapped pipeline).

These are conceptual diagrams that do not depend on results.json. Outputs are
written to ``figures/`` (git-ignored / offline), consistent with the rest of
the figure artifacts.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"


def _box(ax, xy, w, h, text, fc):
    box = FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                         linewidth=1.2, edgecolor="#333333", facecolor=fc)
    ax.add_patch(box)
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center",
            fontsize=9, wrap=True)


def _arrow(ax, start, end):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14,
                                 linewidth=1.1, color="#555555"))


def architecture() -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    ax.set_title("Platform architecture and hybrid scaffolding agent",
                 fontsize=11)
    _box(ax, (0.3, 3.6), 2.4, 1.2, "Client\nReact tablet UI\n(7 inquiry stages)", "#dbeafe")
    _box(ax, (3.6, 3.6), 2.4, 1.2, "Back end\nFastAPI\n(orchestration)", "#dcfce7")
    _box(ax, (7.0, 3.6), 2.6, 1.2, "Data\nSupabase / PostgreSQL\n(analytics store)", "#fef9c3")
    _box(ax, (3.6, 1.4), 2.4, 1.2, "Hybrid agent\nLLM path (primary)", "#e9d5ff")
    _box(ax, (0.3, 1.4), 2.4, 1.2, "Fallback\nrule engine\n(deterministic)", "#fbcfe8")
    _box(ax, (7.0, 1.4), 2.6, 1.2, "Logging layer\nevents + decisions", "#fed7aa")
    _arrow(ax, (2.7, 4.2), (3.6, 4.2))
    _arrow(ax, (6.0, 4.2), (7.0, 4.2))
    _arrow(ax, (4.8, 3.6), (4.8, 2.6))   # backend -> agent
    _arrow(ax, (3.6, 2.0), (2.7, 2.0))   # agent -> fallback
    _arrow(ax, (6.0, 2.0), (7.0, 2.0))   # agent -> logging
    _arrow(ax, (8.3, 2.6), (8.3, 3.6))   # logging -> data
    fig.savefig(FIG / "fig_architecture.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def pipeline() -> None:
    stages = [
        ("S0", "Pretest", "Baseline"),
        ("S1", "Observe", "Evidence"),
        ("S2", "Claim", "Claim"),
        ("S3", "Stickiness", "Evidence"),
        ("S4", "Drainage", "Evidence"),
        ("S5", "Organise", "Evidence\u2192Reasoning"),
        ("S6", "Conclude", "Claim+Reasoning"),
    ]
    fig, ax = plt.subplots(figsize=(11, 3.2))
    ax.set_xlim(0, len(stages) * 1.5); ax.set_ylim(0, 3); ax.axis("off")
    ax.set_title("Seven-stage inquiry pipeline mapped to CER components",
                 fontsize=11)
    for i, (sid, act, cer) in enumerate(stages):
        x = i * 1.5 + 0.15
        fc = "#fecaca" if "Reasoning" in cer else "#dbeafe"
        _box(ax, (x, 1.2), 1.2, 1.0, f"{sid}\n{act}", fc)
        ax.text(x + 0.6, 0.75, cer, ha="center", va="center", fontsize=8,
                color="#b91c1c" if "Reasoning" in cer else "#1e3a8a")
        if i < len(stages) - 1:
            _arrow(ax, (x + 1.2, 1.7), (x + 1.5, 1.7))
    fig.savefig(FIG / "fig_pipeline.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    architecture()
    pipeline()
    print(f"Wrote schematics to {FIG}")


if __name__ == "__main__":
    main()
