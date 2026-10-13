import numpy as np
import pandas as pd

REQUIRED_COLUMNS = [
    "date",
    "department",
    "revenue",
    "cost",
    "tickets_opened",
    "tickets_resolved",
    "sla_met",
]

def generate_sample_data(days: int = 90) -> pd.DataFrame:
    """Create reproducible synthetic operational data."""
    rng = np.random.default_rng(42)
    dates = pd.date_range(
        end=pd.Timestamp.today().normalize(),
        periods=days,
        freq="D",
    )

    rows = []

    departments = {
        "Sales": (6500, 2600, 24),
        "Operations": (3200, 1900, 38),
        "Customer Support": (1800, 1200, 55),
    }

    for date in dates:
        for department, (revenue, cost, tickets) in departments.items():
            opened = max(1, int(rng.normal(tickets, tickets * 0.15)))
            resolved = min(
                opened,
                max(0, int(opened * rng.uniform(0.82, 1.08))),
            )

            rows.append({
                "date": date,
                "department": department,
                "revenue": round(
                    max(0, rng.normal(revenue, revenue * 0.12)), 2
                ),
                "cost": round(
                    max(0, rng.normal(cost, cost * 0.10)), 2
                ),
                "tickets_opened": opened,
                "tickets_resolved": resolved,
                "sla_met": int(
                    resolved * rng.uniform(0.82, 0.98)
                ),
            })

    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate schema, parse dates, and normalize numeric columns."""
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}"
        )

    df = df[REQUIRED_COLUMNS].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    numeric_columns = [
        "revenue", "cost", "tickets_opened",
        "tickets_resolved", "sla_met",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["department"] = df["department"].astype("string").str.strip()

    df = df.dropna(
        subset=["date", "department"] + numeric_columns
    )

    df = df[df["department"] != ""]

    if df.empty:
        raise ValueError("No valid rows remain after data validation.")

    if (df[numeric_columns] < 0).any().any():
        raise ValueError("Numeric values cannot be negative.")

    for col in ["tickets_opened", "tickets_resolved", "sla_met"]:
        if not np.allclose(df[col], np.round(df[col])):
            raise ValueError(f"{col} must contain whole numbers.")
        df[col] = df[col].astype(int)

    if (df["sla_met"] > df["tickets_resolved"]).any():
        raise ValueError("sla_met cannot exceed tickets_resolved.")

    if (df["tickets_resolved"] > df["tickets_opened"]).any():
        raise ValueError(
            "This demo expects tickets_resolved <= tickets_opened."
        )

    return df.sort_values("date").reset_index(drop=True)