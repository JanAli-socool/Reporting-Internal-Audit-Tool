import pandas as pd

def calculate_metrics(df: pd.DataFrame) -> dict:
    """Calculate report KPIs from the selected records."""
    revenue = float(df["revenue"].sum())
    cost = float(df["cost"].sum())
    opened = int(df["tickets_opened"].sum())
    resolved = int(df["tickets_resolved"].sum())
    sla_met = int(df["sla_met"].sum())

    return {
        "period_start": str(df["date"].min().date()),
        "period_end": str(df["date"].max().date()),
        "period_days": int(
            (df["date"].max() - df["date"].min()).days + 1
        ),
        "record_count": int(len(df)),
        "departments": int(df["department"].nunique()),
        "revenue": round(revenue, 2),
        "cost": round(cost, 2),
        "profit": round(revenue - cost, 2),
        "profit_margin_pct": round(
            (revenue - cost) / revenue * 100, 2
        ) if revenue else None,
        "tickets_opened": opened,
        "tickets_resolved": resolved,
        "resolution_rate_pct": round(
            resolved / opened * 100, 2
        ) if opened else None,
        "sla_compliance_pct": round(
            sla_met / resolved * 100, 2
        ) if resolved else None,
    }

def department_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate records without asking an LLM to do arithmetic."""
    result = (
        df.groupby("department", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            cost=("cost", "sum"),
            tickets_opened=("tickets_opened", "sum"),
            tickets_resolved=("tickets_resolved", "sum"),
            sla_met=("sla_met", "sum"),
        )
    )

    result["profit"] = result["revenue"] - result["cost"]

    total_revenue = result["revenue"].sum()
    result["revenue_share_pct"] = (
        result["revenue"] / total_revenue * 100 if total_revenue else float("nan")
    )

    result["profit_margin_pct"] = (
        result["profit"]
        .div(result["revenue"].replace(0, float("nan")))
        * 100
    ).round(2)

    result["resolution_rate_pct"] = (
        result["tickets_resolved"]
        .div(result["tickets_opened"].replace(0, float("nan")))
        * 100
    ).round(2)

    result["sla_compliance_pct"] = (
        result["sla_met"]
        .div(result["tickets_resolved"].replace(0, float("nan")))
        * 100
    ).round(2)

    return result.round(2)

# KPIs compared between periods. Percentages change in percentage points;
# absolute values change in both units and percent.
COMPARABLE_KPIS = [
    "revenue",
    "cost",
    "profit",
    "profit_margin_pct",
    "tickets_opened",
    "tickets_resolved",
    "resolution_rate_pct",
    "sla_compliance_pct",
]


def previous_period_bounds(
    start: pd.Timestamp, end: pd.Timestamp
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return the equal-length window immediately before [start, end]."""
    start = pd.Timestamp(start).normalize()
    end = pd.Timestamp(end).normalize()
    length = end - start + pd.Timedelta(days=1)
    return start - length, start - pd.Timedelta(days=1)


def filter_records(
    df: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
    departments: list[str],
) -> pd.DataFrame:
    """Select records inside an inclusive date window for departments."""
    dates = df["date"].dt.normalize()
    mask = (
        dates.between(pd.Timestamp(start), pd.Timestamp(end))
        & df["department"].isin(departments)
    )
    return df[mask].copy()


def compare_periods(current: dict, previous: dict | None) -> dict:
    """Compute period-over-period changes for the headline KPIs.

    Returns an empty dict when there is no comparable previous period, so
    callers never display a change that was not actually measured.
    """
    if not previous:
        return {}

    comparison = {}
    for kpi in COMPARABLE_KPIS:
        now, before = current.get(kpi), previous.get(kpi)
        if now is None or before is None:
            continue

        entry = {
            "current": now,
            "previous": before,
            "change": round(now - before, 2),
        }
        if kpi.endswith("_pct"):
            entry["unit"] = "percentage points"
        else:
            entry["change_pct"] = (
                round((now - before) / abs(before) * 100, 2)
                if before else None
            )
        comparison[kpi] = entry

    return comparison


def period_comparison(
    df: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
    departments: list[str],
) -> dict:
    """Compare the selected window with the preceding window of equal length.

    The previous window must be fully covered by the dataset; a partial
    window would make the comparison misleading, so it is skipped instead.
    """
    prev_start, prev_end = previous_period_bounds(start, end)
    result = {
        "previous_period_start": str(prev_start.date()),
        "previous_period_end": str(prev_end.date()),
        "available": False,
        "changes": {},
    }

    if df["date"].min().normalize() > prev_start:
        return result

    previous = filter_records(df, prev_start, prev_end, departments)
    if previous.empty:
        return result

    current = filter_records(df, start, end, departments)
    result["available"] = True
    result["changes"] = compare_periods(
        calculate_metrics(current), calculate_metrics(previous)
    )
    return result


def daily_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Daily financial and service totals for trend charts."""
    daily = (
        df.groupby("date", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            cost=("cost", "sum"),
            tickets_resolved=("tickets_resolved", "sum"),
            sla_met=("sla_met", "sum"),
        )
    )
    daily["profit"] = daily["revenue"] - daily["cost"]
    daily["sla_compliance_pct"] = (
        daily["sla_met"]
        .div(daily["tickets_resolved"].replace(0, float("nan")))
        * 100
    ).round(2)
    return daily
