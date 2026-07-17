"""Deterministic rule-based fallback policy for the Evidence Detective agent.

This is the fallback branch of the hybrid scaffolding agent: it is invoked when
the LLM path times out (>8 s), fails JSON-schema validation, or is filtered for
off-topic content. Because it is fully specified and deterministic, it is
directly testable and forms part of the reproducible systems contribution.

Reference policy (from the platform design):
  - scaffold when stage completion rate < 0.40 OR help_clicks >= 2
  - release  when completion rate >= 0.80
  - probe    otherwise (0.40 <= rate < 0.80)
"""

from __future__ import annotations

SCAFFOLD_RATE_THRESHOLD = 0.40
RELEASE_RATE_THRESHOLD = 0.80
HELP_CLICK_THRESHOLD = 2


def fallback_decision(completion_rate: float, help_clicks: int) -> str:
    """Return one of ``{"scaffold", "probe", "release"}``.

    Args:
        completion_rate: fraction of required fields completed for the stage,
            in the closed interval [0, 1].
        help_clicks: number of help-click events accrued in the stage.
    """
    if not 0.0 <= completion_rate <= 1.0:
        raise ValueError("completion_rate must be in [0, 1]")
    if help_clicks < 0:
        raise ValueError("help_clicks must be non-negative")

    if help_clicks >= HELP_CLICK_THRESHOLD or completion_rate < SCAFFOLD_RATE_THRESHOLD:
        return "scaffold"
    if completion_rate >= RELEASE_RATE_THRESHOLD:
        return "release"
    return "probe"
