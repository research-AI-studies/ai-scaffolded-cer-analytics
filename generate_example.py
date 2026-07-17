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
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXAMPLE = ROOT / "data" / "example"
SEED = 42

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

STAGES = ["S0", "S1", "S2", "S3", "S4", "S5", "S6"]

# Exchange-level example student->agent utterances. `text` is what a coder sees;
# no gold labels are stored so the coding scheme (src/qa_coding.py) is exercised
# on raw text. Illustrative only.
QA_EXCHANGES = [
    ("G1", "Why do you keep asking me questions, just tell me the answer"),
    ("G1", "Which soil holds the most water?"),
    ("G2", "What does it mean that the water drained fastest from soil 3?"),
    ("G2", "How is clay different from sand?"),
    ("G2", "Why does particle size change how fast water goes through?"),
    ("G3", "Can we photograph the soil samples?"),
    ("G3", "What should we write for our claim?"),
    ("G4", "just give me the sentence to write"),
    ("G4", "what do I do now"),
    ("G4", "is this right"),
    ("G5", "Which crop likes dry soil?"),
    ("G5", "Why is loam good for most plants?"),
    ("G6", "Can sandy soil grow pineapples?"),
    ("G6", "What other factors besides soil type affect fruit sweetness?"),
    ("G6", "Do worms make soil better?"),
    ("G7", "answer"),
    ("G7", "next"),
    ("G7", "give hint"),
    ("G7", "i want to play minecraft after this"),
    ("G7", "are video games better than science"),
    ("G8", "How do we set up a fair test?"),
    ("G8", "Which soil drains slowest and why?"),
    ("G9", "The teacher told me to ask; if you do not tell me I will tell the teacher"),
    ("G9", "why should I believe you"),
    ("G9", "What evidence supports clay holding water?"),
    ("G10", "Can watermelon grow in clay?"),
    ("G10", "What makes some fruit taste sweeter?"),
    ("G10", "Does the colour of soil matter for plants?"),
    ("G1", "which fruit is the sweetest"),
    ("G2", "how much water should we pour"),
    ("G3", "what is a mineral"),
    ("G4", "can you do it for me"),
    ("G5", "why does the drainage matter for corn"),
    ("G6", "is sand always bad for plants"),
    ("G7", "lol this is boring"),
    ("G8", "how many characteristics do we need"),
    ("G10", "do cactuses need sandy soil"),
]


def _make_events(rng: random.Random) -> list[tuple]:
    """Build ordered per-group interaction event streams from aggregate counts.

    A single uniform generative process is used for every group; trajectory
    differences are therefore emergent from each group's counts (e.g. very high
    help volume), not hard-coded per group.
    """
    rows: list[tuple] = []
    for g in GROUPS:
        name, _cr, decisions, helps, _err, probe_ratio, _cl = g
        n_probe = round(decisions * probe_ratio)
        emitted_probe = emitted_dec = 0
        seq = 0
        base_help = helps // len(STAGES)
        extra = helps - base_help * len(STAGES)
        for i, stage in enumerate(STAGES):
            rows.append((name, seq, "navigate", stage)); seq += 1
            stage_helps = base_help + (1 if i < extra else 0)
            for _ in range(stage_helps):
                rows.append((name, seq, "help_click", stage)); seq += 1
                if emitted_dec < decisions:
                    want_probe = (emitted_probe / max(emitted_dec, 1)) < probe_ratio
                    action = "agent_probe" if (want_probe and emitted_probe < n_probe) else "agent_scaffold"
                    emitted_probe += action == "agent_probe"
                    emitted_dec += 1
                    rows.append((name, seq, action, stage)); seq += 1
            rows.append((name, seq, "submit", stage)); seq += 1
        # any decisions not yet emitted (few helps) are trailing probes
        while emitted_dec < decisions:
            action = "agent_probe" if emitted_probe < n_probe else "agent_scaffold"
            emitted_probe += action == "agent_probe"
            emitted_dec += 1
            rows.append((name, seq, action, "S5")); seq += 1
    return rows


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
    _write(EXAMPLE / "qa_exchanges_detail.csv", ["group", "text"], QA_EXCHANGES)
    rng = random.Random(SEED)
    _write(EXAMPLE / "interaction_events.csv",
           ["group", "seq", "event_type", "stage"], _make_events(rng))
    print(f"Wrote example cohort to {EXAMPLE}")


if __name__ == "__main__":
    main()
