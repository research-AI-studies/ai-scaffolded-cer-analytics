"""Tests for the InquiTrace analytics pipeline (run against the example cohort)."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / script)], check=True, cwd=ROOT)


def setup_module(module):  # noqa: ARG001
    _run("generate_example.py")
    _run("src/analyze.py")


def _results() -> dict:
    return json.loads((ROOT / "outputs" / "results.json").read_text(encoding="utf-8"))


def test_example_is_flagged():
    r = _results()
    assert r["data_source"] == "example"
    assert "ILLUSTRATIVE" in r["provenance"]


def test_agent_decision_shares_sum_to_one():
    r = _results()
    total = sum(v["pct"] for v in r["agent_decisions"]["by_action"].values())
    assert abs(total - 1.0) < 1e-6


def test_reasoning_gap_present_in_example():
    r = _results()
    assert r["cer_completion"]["Reasoning"]["completion"] == 0.0
    assert r["cer_completion"]["Claim"]["completion"] == 1.0


def test_correlations_are_bounded():
    r = _results()
    for c in r["correlations"].values():
        assert -1.0 <= c["rho"] <= 1.0
        assert 0.0 <= c["p"] <= 1.0


def test_misconceptions_total_matches_sum():
    r = _results()
    m = r["misconceptions"]
    assert sum(v["count"] for v in m["by_type"].values()) == m["total_errors"]
