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