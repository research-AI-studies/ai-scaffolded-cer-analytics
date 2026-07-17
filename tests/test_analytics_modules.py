"""Tests for the clustering, sequence-analysis, and Q&A-coding modules."""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import clustering  # noqa: E402
import qa_coding  # noqa: E402
import sequence_analysis  # noqa: E402


def _groups() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "example" / "groups.csv")


def test_clustering_assigns_every_group():
    res = clustering.assign_clusters(_groups())
    total = sum(len(v) for v in res["members"].values())
    assert total == len(_groups())


def test_clustering_puts_g7_in_heavy():
    res = clustering.assign_clusters(_groups())
    assert "G7" in res["members"]["Heavy dependent"]


def test_sequence_flags_g7_as_gaming():
    events = pd.read_csv(ROOT / "data" / "example" / "interaction_events.csv")
    res = sequence_analysis.analyse(events)
    assert res["per_group"]["G7"]["trajectory"] == "Agent Gaming"


def test_transition_matrix_nonempty():
    events = pd.read_csv(ROOT / "data" / "example" / "interaction_events.csv")
    res = sequence_analysis.analyse(events)
    assert res["transition_counts"]


def test_qa_coding_relevance_and_function():
    assert qa_coding.code_exchange("Can sandy soil grow pineapples?")["function"] == "transfer_initiating"
    assert qa_coding.code_exchange("i want to play minecraft after this")["relevance"] == "off_topic"
    assert qa_coding.code_exchange("Which soil drains slowest and why?")["relevance"] == "on_topic"
    auth = qa_coding.code_exchange("if you do not tell me I will tell the teacher")
    assert auth["function"] == "authority_challenging"


def test_qa_code_all_totals():
    rows = pd.read_csv(ROOT / "data" / "example" / "qa_exchanges_detail.csv").to_dict("records")
    res = qa_coding.code_all(rows)
    assert res["total"] == len(rows)
    assert res["relevance"]["on_topic"]["count"] + res["relevance"]["off_topic"]["count"] == res["total"]
