"""End-to-end checks that run the real Streamlit script headlessly."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import reporting.workflow as workflow

from .conftest import GOOD_REPORT

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"


@pytest.fixture
def app(monkeypatch):
    # An empty value stops a developer's .env key being used by tests.
    monkeypatch.setenv("OPENAI_API_KEY", "")
    return AppTest.from_file(str(APP_PATH), default_timeout=60)


@pytest.fixture
def fake_llm(monkeypatch):
    calls = []

    def fake_create_report(**kwargs):
        calls.append(kwargs)
        for node, _ in workflow.WORKFLOW_STEPS:
            kwargs["on_step"](node)
        return {
            "report": GOOD_REPORT,
            "validation_message": "Report structure validated successfully.",
            "warnings": ["Figures not found in the calculated metrics: 12"],
            "figures_checked": 7,
            "figures_matched": 6,
        }

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(workflow, "create_report", fake_create_report)
    return calls


def test_dashboard_loads_without_api_key(app):
    app.run()
    assert not app.exception
    assert not app.error
    labels = [m.label for m in app.metric]
    assert labels[:4] == ["Revenue", "Operating cost", "Profit", "Profit margin"]
    assert "SLA compliance" in labels
    # Default 30-day window has a full previous period, so deltas show.
    assert app.metric[0].delta is not None


def test_missing_api_key_shows_setup_message(app):
    app.run()
    app.button[0].click().run()
    assert any("OPENAI_API_KEY is missing" in e.value for e in app.error)


def test_department_filter_changes_kpis(app):
    app.run()
    all_revenue = app.metric[0].value
    app.multiselect[0].set_value(["Sales"]).run()
    assert app.metric[0].value != all_revenue


def test_empty_department_selection_prompts_user(app):
    app.run()
    app.multiselect[0].set_value([]).run()
    assert any("at least one department" in w.value for w in app.warning)


def test_generate_report_and_stale_filter_warning(app, fake_llm):
    app.run()
    app.button[0].click().run()

    assert len(fake_llm) == 1
    assert fake_llm[0]["comparison"]["available"]
    markdown = " ".join(m.value for m in app.markdown)
    assert GOOD_REPORT["key_findings"][0] in markdown
    assert not any("Filters have changed" in w.value for w in app.warning)

    # Changing filters keeps the original report but flags it as stale.
    app.multiselect[0].set_value(["Sales"]).run()
    assert any("Filters have changed" in w.value for w in app.warning)
    assert GOOD_REPORT["key_findings"][0] in " ".join(m.value for m in app.markdown)


def test_llm_failure_is_graceful(app, monkeypatch):
    def boom(**kwargs):
        raise RuntimeError("provider timeout")

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(workflow, "create_report", boom)
    app.run()
    app.button[0].click().run()
    assert not app.exception
    assert any("Report generation failed" in e.value for e in app.error)
    # The dashboard itself still renders.
    assert app.metric[0].label == "Revenue"


def test_single_day_period(app):
    app.run()
    end = app.date_input[0].value[1]
    app.date_input[0].set_value((end, end)).run()
    assert not app.exception
    assert app.metric[0].value.startswith("$")


def test_report_section_comes_before_evidence(app):
    app.run()
    headings = [h.value for h in app.subheader]
    assert headings == ["Overview", "Management report (AI draft)", "Evidence"]


def test_percentage_deltas_use_pts(app):
    app.run()
    sla = next(m for m in app.metric if m.label == "SLA compliance")
    assert sla.delta.endswith(" pts")
    assert any("Compared with the previous 30 days" in c.value for c in app.caption)


def test_report_card_shows_trust_checklist_and_steps(app, fake_llm):
    app.run()
    app.button[0].click().run()
    text = " ".join(m.value for m in app.markdown)
    assert "6 of 7 figures match the calculated data" in text
    assert "1 to verify" in text
    for _, label in workflow.WORKFLOW_STEPS:
        assert f"✓ {label}" in text
    assert any("12" in w.value for w in app.warning)


def test_measure_switch_renders(app):
    app.run()
    app.radio[0].set_value("Profit").run()
    assert not app.exception
