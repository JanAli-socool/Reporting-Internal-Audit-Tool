import pandas as pd
import pytest

from reporting.metrics import (
    calculate_metrics,
    compare_periods,
    department_summary,
    period_comparison,
    previous_period_bounds,
)


def frame(rows):
    df = pd.DataFrame(rows, columns=[
        "date", "department", "revenue", "cost",
        "tickets_opened", "tickets_resolved", "sla_met",
    ])
    df["date"] = pd.to_datetime(df["date"])
    return df


SMALL = frame([
    ("2026-01-01", "Sales", 1000.0, 400.0, 10, 8, 6),
    ("2026-01-01", "Ops", 500.0, 300.0, 20, 20, 15),
    ("2026-01-02", "Sales", 1000.0, 600.0, 10, 10, 10),
])


def test_calculate_metrics_values():
    m = calculate_metrics(SMALL)
    assert m["revenue"] == 2500.0
    assert m["cost"] == 1300.0
    assert m["profit"] == 1200.0
    assert m["profit_margin_pct"] == 48.0
    assert m["resolution_rate_pct"] == 95.0          # 38 / 40
    assert m["sla_compliance_pct"] == pytest.approx(81.58, abs=0.01)  # 31 / 38
    assert m["period_start"] == "2026-01-01"
    assert m["departments"] == 2


def test_zero_denominators_return_none():
    m = calculate_metrics(frame([("2026-01-01", "Sales", 0.0, 0.0, 0, 0, 0)]))
    assert m["profit_margin_pct"] is None
    assert m["resolution_rate_pct"] is None
    assert m["sla_compliance_pct"] is None


def test_department_summary():
    summary = department_summary(SMALL).set_index("department")
    assert summary.loc["Sales", "profit"] == 1000.0
    assert summary.loc["Sales", "profit_margin_pct"] == 50.0
    assert summary.loc["Sales", "revenue_share_pct"] == 80.0
    assert summary.loc["Ops", "sla_compliance_pct"] == 75.0


def test_previous_period_bounds():
    start, end = previous_period_bounds(
        pd.Timestamp("2026-10-01"), pd.Timestamp("2026-10-30")
    )
    assert start == pd.Timestamp("2026-09-01")
    assert end == pd.Timestamp("2026-09-30")


def test_compare_periods_units():
    changes = compare_periods(
        {"revenue": 110.0, "sla_compliance_pct": 85.0},
        {"revenue": 100.0, "sla_compliance_pct": 90.0},
    )
    assert changes["revenue"]["change"] == 10.0
    assert changes["revenue"]["change_pct"] == 10.0
    assert changes["sla_compliance_pct"]["change"] == -5.0
    assert changes["sla_compliance_pct"]["unit"] == "percentage points"
    assert compare_periods({"revenue": 1.0}, None) == {}


def test_period_comparison_available(sample_df):
    result = period_comparison(
        sample_df, pd.Timestamp("2026-09-15"), pd.Timestamp("2026-10-14"),
        ["Sales", "Operations", "Customer Support"],
    )
    assert result["available"]
    assert result["previous_period_start"] == "2026-08-16"
    assert result["previous_period_end"] == "2026-09-14"
    # The synthetic Operations SLA slip shows up as a decline.
    assert result["changes"]["sla_compliance_pct"]["change"] < 0


def test_period_comparison_skipped_without_full_history(sample_df):
    start = sample_df["date"].min()
    result = period_comparison(
        sample_df, start, start + pd.Timedelta(days=29), ["Sales"]
    )
    assert not result["available"]
    assert result["changes"] == {}


def test_weekly_comparison_buckets(sample_df):
    from reporting.metrics import weekly_comparison

    depts = ["Sales", "Operations", "Customer Support"]
    start, end = pd.Timestamp("2026-09-15"), pd.Timestamp("2026-10-14")
    weekly = weekly_comparison(sample_df, start, end, depts, "revenue")

    assert list(weekly["bucket"].unique()) == [
        "Days 1–7", "Days 8–14", "Days 15–21", "Days 22–28", "Days 29–30",
    ]
    totals = weekly.groupby("period")["revenue"].sum()
    current = calculate_metrics(
        sample_df[sample_df["date"].between(start, end)]
    )["revenue"]
    assert totals["Selected period"] == pytest.approx(current)


def test_weekly_comparison_empty_without_history(sample_df):
    from reporting.metrics import weekly_comparison

    start = sample_df["date"].min()
    weekly = weekly_comparison(
        sample_df, start, start + pd.Timedelta(days=13), ["Sales"], "revenue"
    )
    assert weekly.empty
