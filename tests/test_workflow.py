import pytest

from reporting.workflow import create_report, find_unverified_figures

from .conftest import GOOD_REPORT, FakeStructuredLLM

METRICS = {
    "period_start": "2026-09-15",
    "period_end": "2026-10-14",
    "period_days": 30,
    "revenue": 360188.4,
    "cost": 178197.1,
    "profit": 181991.3,
    "profit_margin_pct": 50.53,
    "sla_compliance_pct": 85.38,
}
DEPARTMENTS = [
    {"department": "Operations", "revenue": 96000.0, "sla_compliance_pct": 79.1}
]
COMPARISON = {
    "available": True,
    "previous_period_start": "2026-08-16",
    "previous_period_end": "2026-09-14",
    "changes": {
        "revenue": {"current": 360188.4, "previous": 350018.0,
                    "change": 10170.4, "change_pct": 2.91},
        "sla_compliance_pct": {"current": 85.38, "previous": 88.98,
                               "change": -3.6, "unit": "percentage points"},
    },
}


def run(llm):
    return create_report(METRICS, DEPARTMENTS, COMPARISON, "Synthetic demo data", llm=llm)


def test_happy_path_returns_validated_report():
    llm = FakeStructuredLLM()
    result = run(llm)
    assert result["report"] == GOOD_REPORT
    assert "validated successfully" in result["validation_message"]
    assert "All quoted figures match" in result["validation_message"]
    assert result["warnings"] == []


def test_prompt_contains_verified_metrics_and_comparison():
    llm = FakeStructuredLLM()
    run(llm)
    prompt = llm.prompts[0]
    assert "360188.4" in prompt
    assert "2026-08-16" in prompt
    assert "Synthetic demo data" in prompt


def test_prompt_forbids_trends_without_comparison():
    llm = FakeStructuredLLM()
    create_report(METRICS, DEPARTMENTS, {"available": False}, llm=llm)
    assert "Do not describe changes over time" in llm.prompts[0]


@pytest.mark.parametrize("section", [
    "executive_summary", "key_findings", "recommendations", "risks_or_caveats",
])
def test_missing_section_fails_validation(section):
    report = dict(GOOD_REPORT, **{section: [] if section != "executive_summary" else ""})
    with pytest.raises(ValueError, match="missing sections"):
        run(FakeStructuredLLM(report))


def test_blank_list_items_fail_validation():
    report = dict(GOOD_REPORT, recommendations=["  "])
    with pytest.raises(ValueError, match="non-empty text"):
        run(FakeStructuredLLM(report))


def test_invented_figure_is_flagged_not_fatal():
    report = dict(GOOD_REPORT, key_findings=GOOD_REPORT["key_findings"] + [
        "Customer churn rose to 17.4%.",
    ])
    result = run(FakeStructuredLLM(report))
    assert any("17.4" in w for w in result["warnings"])
    assert "All quoted figures match" not in result["validation_message"]


def test_finding_count_outside_range_warns():
    report = dict(GOOD_REPORT, key_findings=["Profit was $181,991."])
    result = run(FakeStructuredLLM(report))
    assert any("3-5 key findings" in w for w in result["warnings"])


def test_llm_failure_propagates():
    with pytest.raises(RuntimeError, match="timeout"):
        run(FakeStructuredLLM(error=RuntimeError("timeout")))


@pytest.mark.parametrize("text", [
    "Revenue was $360,188.",            # rounded to whole dollars
    "Revenue was $360.2K.",             # abbreviated thousands
    "Revenue was $0.36M.",              # abbreviated millions
    "Revenue was 0.36 million.",
    "SLA fell by 3.6 percentage points.",
    "Revenue grew 2.9%.",
    "Operations SLA was 79.1%.",
    "Three departments over 30 days, 2026-09-15 to 2026-10-14.",
])
def test_grounded_figures_are_accepted(text):
    report = {"executive_summary": text, "key_findings": []}
    assert find_unverified_figures(report, [METRICS, DEPARTMENTS, COMPARISON]) == []


@pytest.mark.parametrize("text, flagged", [
    ("Revenue was $412,000.", "412,000"),
    ("Margin hit 61.2%.", "61.2"),
    ("Costs fell 12%.", "12"),
])
def test_ungrounded_figures_are_flagged(text, flagged):
    report = {"executive_summary": text, "key_findings": []}
    result = find_unverified_figures(report, [METRICS, DEPARTMENTS, COMPARISON])
    assert result == [flagged]
