"""Unit tests for TableDocumentReasoner 2D table parsing, coordinate indexing, and arithmetic."""

import pytest
from atlas.evaluation.table_reasoner import TableDocumentReasoner

@pytest.fixture
def sample_table():
    return {
        "header": ["Country", "2020", "2021", "2022"],
        "table": [
            ["India", "70.0", "77.5", "82.0"],
            ["Indonesia", "48.0", "51.8", "55.0"],
            ["Philippines", "34.0", "51.4", "58.0"]
        ]
    }

@pytest.fixture
def sample_paragraphs():
    return [
        {"order": 1, "text": "In 2021, India recorded a major surge in digital adoption to 77.5 percent."},
        {"order": 2, "text": "The Philippines achieved 51.4 percent account ownership according to survey data."}
    ]

def test_table_reasoner_extreme_year(sample_table, sample_paragraphs):
    reasoner = TableDocumentReasoner(sample_table, sample_paragraphs)
    
    # Highest year for India
    res_high = reasoner.answer_question("Which year had the highest value for India?")
    assert res_high["answer"] == "2022"

    # Lowest year for India
    res_low = reasoner.answer_question("In which year was the number smallest for India?")
    assert res_low["answer"] == "2020"

def test_table_reasoner_difference(sample_table, sample_paragraphs):
    reasoner = TableDocumentReasoner(sample_table, sample_paragraphs)
    
    # Difference between 2021 and 2020 for India (77.5 - 70.0 = 7.5)
    res_diff = reasoner.answer_question("What is the difference between 2021 and 2020 for India?")
    assert res_diff["answer"] == "7.5" or float(res_diff["answer"]) == pytest.approx(7.5, abs=0.1)

def test_table_reasoner_percentage_change(sample_table, sample_paragraphs):
    reasoner = TableDocumentReasoner(sample_table, sample_paragraphs)
    
    # Percentage change for India from 2020 to 2021: (77.5 - 70.0)/70.0 * 100 = 10.71%
    res_pct = reasoner.answer_question("What was the percentage change for India from 2020 to 2021?")
    val = float(res_pct["answer"])
    assert val == pytest.approx(10.71, abs=0.2)

def test_table_reasoner_direct_lookup(sample_table, sample_paragraphs):
    reasoner = TableDocumentReasoner(sample_table, sample_paragraphs)
    
    res = reasoner.answer_question("What was the account ownership in India in 2021?")
    assert "77.5" in res["answer"]

