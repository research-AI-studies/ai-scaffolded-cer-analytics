"""Render manuscript-ready tables from ``outputs/results.json``.

Tables are processed artifacts written to ``tables/`` (git-ignored, offline).
Output is Markdown so the numbers can be injected verbatim into the manuscript
without hand-editing.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "outputs" / "results.json"
TAB = ROOT / "tables"


def _provenance(results: dict) -> str:
    return f"<!-- {results['provenance']} -->\n\n"


def table_groups(results: dict) -> str:
    src = "private" if results["data_source"] == "private" else "example"
    lines = ["| Group | Completion | Agent decisions | Help requests | "
             "Post-test errors | Probe ratio | Cluster |",
             "|---|---|---|---|---|---|---|"]
    with (ROOT / "data" / src / "groups.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            lines.append(
                f"| {r['group']} | {float(r['completion_rate'])*100:.0f}% | "
                f"{r['agent_decisions']} | {r['help_requests']} | "
                f"{r['post_test_errors']} | {float(r['probe_ratio'])*100:.1f}% | "
                f"{r['cluster']} |")
    return "### Table: Group-level summary\n\n" + "\n".join(lines) + "\n"


def table_cer(results: dict) -> str:
    lines = ["| CER component | Stage | Metric | Completion | n |",
             "|---|---|---|---|---|"]
    for comp, d in results["cer_completion"].items():
        lines.append(f"| {comp} | {d['stage']} | {d['metric']} | "
                     f"{d['completion']*100:.0f}% | {d['n']} |")
    return "### Table: CER component completion\n\n" + "\n".join(lines) + "\n"


def table_misconceptions(results: dict) -> str:
    m = results["misconceptions"]
    lines = ["| Error type | Label | Count | Share |", "|---|---|---|---|"]
    for t, d in m["by_type"].items():
        lines.append(f"| {t} | {d['label']} | {d['count']} | {d['pct']*100:.0f}% |")
    lines.append(f"| **Total** |  | **{m['total_errors']}** | 100% |")
    return "### Table: Post-assessment misconception typology\n\n" + "\n".join(lines) + "\n"


def main() -> None:
    if not RESULTS.exists():
        raise SystemExit("outputs/results.json missing - run src/analyze.py first.")
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    TAB.mkdir(parents=True, exist_ok=True)
    doc = _provenance(results) + "\n".join([
        table_groups(results), "", table_cer(results), "",
        table_misconceptions(results)])
    (TAB / "tables.md").write_text(doc, encoding="utf-8")
    print(f"Wrote tables to {TAB / 'tables.md'} (data_source={results['data_source']})")


if __name__ == "__main__":
    main()
