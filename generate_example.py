"""Generate a runnable EXAMPLE cohort for the InquiTrace analytics pipeline.

This produces an *illustrative, non-real* dataset ("example cohort") whose sole
purpose is to let the pipeline, figures, and tests execute end-to-end in the
public repository without exposing any real classroom data.

IMPORTANT (scientific integrity):
- These numbers are ILLUSTRATIVE. They are NOT measurements from a real study
  and MUST NEVER be injected into a manuscript as empirical findings.
- Real study data, when collected, belongs in ``data/private/`` (git-ignored)
  and is consumed by the same pipeline in place of this example cohort.

The cohort is deterministic (fixed values) so the demonstration is reproducible.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXAMPLE = ROOT / "data" / "example"

# Illustrative 10-group example cohort. Structure mirrors the InquiTrace schema
# (per-group completion, agent decisions, help requests, post-test errors,
# probe ratio, cluster) so the pipeline can be demonstrated realistically.
GROUPS = [
    # group, completion_rate, agent_decisions, help_requests, post_test_errors, probe_ratio, cluster
    ("G1", 0.84, 8, 1, 1, 0.625, "Independent"),
    ("G2", 0.83, 18, 4, 0, 0.778, "Moderate"),
    ("G3", 0.87, 15, 6, 0, 0.600, "Moderate"),
    ("G4", 0.82, 18, 11, 5, 0.167, "Heavy dependent"),
    ("G5", 0.84, 27, 7, 1, 0.370, "Moderate"),
    ("G6", 0.84, 24, 12, 0, 0.333, "Moderate"),
    ("G7", 0.91, 122, 2287, 2, 0.033, "Heavy dependent"),
    ("G8", 0.84, 12, 2, 2, 0.167, "Independent"),
    ("G9", 0.85, 22, 2, 4, 0.273, "Independent"),
    ("G10", 0.80, 15, 10, 0, 0.267, "Moderate"),
]

AGENT_DECISIONS = [("scaffold", 204), ("probe", 65), ("release", 10), ("redirect", 2)]
AGENT_SOURCE = [("llm", 89), ("fallback", 60)]
CER = [
    ("Claim", "S2", "claim_formulated", 10, 10),
    ("Claim+Evidence", "S2", "justification_provided", 6, 10),
    ("Evidence-Observation", "S1/S3/S4", "records_complete", 10, 10),
    ("Evidence-Interpretation", "S5", "seeBox_thinkBox_filled", 10, 10),
    ("Reasoning", "S5", "explain_field_filled", 0, 10),
    ("Conclusion-Crops", "S6", "crop_matching_complete", 10, 10),
]
MISCONCEPTIONS = [
    ("Type I", "Loam overgeneralisation", 5),
    ("Type II", "Stickiness overextension", 6),
    ("Type III", "Drainage misconception", 5),
    ("Type IV", "Random guessing", 4),
]
QA = [("on_topic", 20), ("off_topic", 17)]


def _write(path: Path, header: list[str], rows: list) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main() -> None:
    EXAMPLE.mkdir(parents=True, exist_ok=True)
    _write(EXAMPLE / "groups.csv",
           ["group", "completion_rate", "agent_decisions", "help_requests",
            "post_test_errors", "probe_ratio", "cluster"], GROUPS)
    _write(EXAMPLE / "agent_decisions.csv", ["action_type", "count"], AGENT_DECISIONS)
    _write(EXAMPLE / "agent_decision_source.csv", ["source", "count"], AGENT_SOURCE)
    _write(EXAMPLE / "cer_completion.csv",
           ["component", "stage", "metric", "completed", "total"], CER)
    _write(EXAMPLE / "misconceptions.csv", ["error_type", "label", "count"], MISCONCEPTIONS)
    _write(EXAMPLE / "qa_exchanges.csv", ["category", "count"], QA)
    print(f"Wrote example cohort to {EXAMPLE}")


if __name__ == "__main__":
    main()
