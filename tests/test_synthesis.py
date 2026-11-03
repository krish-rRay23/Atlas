"""Unit tests for Research Synthesis Engine."""

import pytest
from atlas.synthesis.engine import ResearchSynthesisEngine

def test_synthesis_generates_twelve_sections():
    engine = ResearchSynthesisEngine()
    memo = engine.generate_comparative_memo("PROJ-TEST")
    assert len(memo.sections) == 12
    assert memo.sections[0].title.startswith("1. Executive Summary")
    assert memo.sections[10].title.startswith("11. Strategic & Policy Implications")
    assert memo.sections[11].title.startswith("12. Sources & Bibliography")
    assert memo.validation_status in ["fully_grounded", "grounded_with_caveats"]

