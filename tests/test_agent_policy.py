"""Tests for the deterministic fallback scaffolding policy."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_policy import fallback_decision  # noqa: E402


def test_scaffold_on_low_completion():
    assert fallback_decision(0.30, 0) == "scaffold"


def test_scaffold_on_help_clicks_overrides_release():
    # Even at high completion, >=2 help clicks forces a scaffold.
    assert fallback_decision(0.95, 2) == "scaffold"


def test_probe_in_mid_range():
    assert fallback_decision(0.50, 0) == "probe"
    assert fallback_decision(0.79, 1) == "probe"


def test_release_when_complete():
    assert fallback_decision(0.80, 0) == "release"
    assert fallback_decision(1.0, 1) == "release"


def test_boundary_at_scaffold_threshold():
    assert fallback_decision(0.40, 0) == "probe"      # not < 0.40
    assert fallback_decision(0.399, 0) == "scaffold"


@pytest.mark.parametrize("rate,clicks", [(-0.1, 0), (1.1, 0), (0.5, -1)])
def test_invalid_inputs_raise(rate, clicks):
    with pytest.raises(ValueError):
        fallback_decision(rate, clicks)
