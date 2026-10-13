from reporting.report import build_report_markdown

from .conftest import GOOD_REPORT


def snapshot(**overrides):
    base = {
        "result": {"report": GOOD_REPORT, "validation_message": "ok",
                   "warnings": ["Figures not found: 17.4%"]},
        "metrics": {
            "period_start": "2026-09-15", "period_end": "2026-10-14",
            "record_count": 90, "revenue": 1000.0, "cost": 400.0,
            "profit": 600.0, "profit_margin_pct": 60.0,
            "tickets_opened": 50, "tickets_resolved": 45,
            "resolution_rate_pct": 90.0, "sla_compliance_pct": None,
        },
        "departments": [{
            "department": "Sales", "revenue": 1000.0, "cost": 400.0,
            "profit": 600.0, "profit_margin_pct": 60.0,
            "resolution_rate_pct": 90.0, "sla_compliance_pct": float("nan"),
        }],
        "comparison": {
            "available": True,
            "previous_period_start": "2026-08-16",
            "previous_period_end": "2026-09-14",
            "changes": {
                "revenue": {"change": -50.0, "change_pct": -4.76},
                "profit_margin_pct": {"change": 1.25},
            },
        },
        "selected_departments": ["Sales"],
        "data_source": "Synthetic demo data",
        "generated_at": "2026-10-14 09:00",
    }
    base.update(overrides)
    return base


def test_markdown_uses_snapshot_period_and_sections():
    md = build_report_markdown(snapshot())
    assert "**Reporting period:** 2026-09-15 to 2026-10-14" in md
    assert "**Compared with:** 2026-08-16 to 2026-09-14" in md
    for heading in ["## Key metrics", "## Department performance",
                    "## Executive summary", "## Key findings",
                    "## Recommendations", "## Risks and caveats",
                    "## Review flags"]:
        assert heading in md
    for finding in GOOD_REPORT["key_findings"]:
        assert f"- {finding}" in md


def test_markdown_formats_values_and_changes():
    md = build_report_markdown(snapshot())
    assert "| Revenue | $1,000.00 | -$50.00 (-4.76%) |" in md
    assert "| Profit margin | 60.00% | +1.25 pp |" in md
    assert "| SLA compliance | N/A | — |" in md
    assert "| Sales | $1,000.00 | $400.00 | $600.00 | 60.00% | 90.00% | N/A |" in md


def test_markdown_without_comparison():
    md = build_report_markdown(snapshot(comparison={"available": False}))
    assert "Compared with" not in md
    assert "| Revenue | $1,000.00 | — |" in md
