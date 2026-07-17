"""Behavioural sequence / trajectory analysis from event-level interaction logs.

Consumes ordered per-group events (navigate, help_click, agent_probe,
agent_scaffold, submit) and derives:
  - a first-order transition-count matrix (aggregated across groups);
  - per-group trajectory features (help-per-decision, scaffold share, the share
    of help_click events immediately followed by another help_click);
  - a deterministic trajectory label per group.

Trajectory labels (fully specified, reviewer-auditable):
  - "Agent Gaming"        : help_per_decision > 3  (help-seeking dwarfs decisions)
  - "Scaffold-Dependent"  : not gaming AND scaffold_share > 0.65
  - "Linear Progressive"  : otherwise
"""

from __future__ import annotations

import pandas as pd

GAMING_HELP_PER_DECISION = 3.0
SCAFFOLD_SHARE_CUT = 0.65


def transition_matrix(events: pd.DataFrame) -> dict:
    counts: dict[str, dict[str, int]] = {}
    for _, grp in events.sort_values(["group", "seq"]).groupby("group"):
        types = grp["event_type"].tolist()
        for a, b in zip(types, types[1:]):
            counts.setdefault(a, {}).setdefault(b, 0)
            counts[a][b] += 1
    return counts


def _trajectory(help_clicks: int, decisions: int, scaffolds: int) -> str:
    hpd = help_clicks / decisions if decisions else float(help_clicks)
    scaffold_share = scaffolds / decisions if decisions else 0.0
    if hpd > GAMING_HELP_PER_DECISION:
        return "Agent Gaming"
    if scaffold_share > SCAFFOLD_SHARE_CUT:
        return "Scaffold-Dependent"
    return "Linear Progressive"


def analyse(events: pd.DataFrame) -> dict:
    per_group = {}
    labels: dict[str, list[str]] = {}
    for name, grp in events.sort_values(["group", "seq"]).groupby("group"):
        types = grp["event_type"].tolist()
        help_clicks = types.count("help_click")
        scaffolds = types.count("agent_scaffold")
        probes = types.count("agent_probe")
        decisions = scaffolds + probes
        repeats = sum(1 for a, b in zip(types, types[1:])
                      if a == "help_click" and b == "help_click")
        cycle_ratio = repeats / help_clicks if help_clicks else 0.0
        label = _trajectory(help_clicks, decisions, scaffolds)
        per_group[name] = {
            "help_clicks": help_clicks,
            "decisions": decisions,
            "scaffold_share": round(scaffolds / decisions, 4) if decisions else 0.0,
            "help_per_decision": round(help_clicks / decisions, 4) if decisions else None,
            "help_click_repeat_ratio": round(cycle_ratio, 4),
            "trajectory": label,
        }
        labels.setdefault(label, []).append(name)
    return {
        "trajectory_rules": {
            "gaming_help_per_decision_gt": GAMING_HELP_PER_DECISION,
            "scaffold_dependent_scaffold_share_gt": SCAFFOLD_SHARE_CUT,
        },
        "labels": labels,
        "per_group": per_group,
        "transition_counts": transition_matrix(events),
    }
