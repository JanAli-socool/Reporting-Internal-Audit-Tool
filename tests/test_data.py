import io

import pandas as pd
import pytest

from reporting.data import REQUIRED_COLUMNS, generate_sample_data, validate_data


def read(csv: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(csv))


HEADER = ",".join(REQUIRED_COLUMNS)


def test_generated_data_passes_validation():
    raw = generate_sample_data(days=30, end_date="2026-10-14")
    df = validate_data(raw)
    assert len(df) == 90
    assert df["date"].max() == pd.Timestamp("2026-10-14")
    assert df.attrs["dropped_rows"] == 0


def test_generation_is_reproducible():
    a = generate_sample_data(days=10, end_date="2026-10-14")
    b = generate_sample_data(days=10, end_date="2026-10-14")
    pd.testing.assert_frame_equal(a, b)


def test_bundled_sample_csv_is_valid():
    df = validate_data(pd.read_csv("data/sample_operations.csv"))
    assert set(df["department"]) == {"Sales", "Operations", "Customer Support"}


def test_missing_column_has_clear_error():
    with pytest.raises(ValueError, match="Missing required columns: sla_met"):
        validate_data(read("date,department,revenue,cost,tickets_opened,tickets_resolved\n"))


def test_column_names_are_normalized():
    csv = " Date , DEPARTMENT ,Revenue,Cost,Tickets_Opened,Tickets_Resolved,SLA_Met\n" \
          "2026-01-01,Sales,100,50,10,8,7\n"
    df = validate_data(read(csv))
    assert list(df.columns) == REQUIRED_COLUMNS


def test_invalid_rows_are_excluded_and_counted():
    csv = HEADER + "\n" + "\n".join([
        "2026-01-01,Sales,100,50,10,8,7",
        "not-a-date,Sales,100,50,10,8,7",
        "2026-01-02,,100,50,10,8,7",
        "2026-01-03,Sales,abc,50,10,8,7",
        "2026-01-04,Sales,100,,10,8,7",
    ])
    df = validate_data(read(csv))
    assert len(df) == 1
    assert df.attrs["dropped_rows"] == 4


def test_all_invalid_rows_rejected():
    csv = HEADER + "\nbad,Sales,x,y,1,1,1\n"
    with pytest.raises(ValueError, match="No valid rows remain"):
        validate_data(read(csv))


@pytest.mark.parametrize("row, message", [
    ("2026-01-01,Sales,-1,50,10,8,7", "cannot be negative"),
    ("2026-01-01,Sales,100,50,10.5,8,7", "whole numbers"),
    ("2026-01-01,Sales,100,50,10,8,9", "sla_met cannot exceed"),
    ("2026-01-01,Sales,100,50,10,12,7", "tickets_resolved <= tickets_opened"),
])
def test_business_rule_violations(row, message):
    with pytest.raises(ValueError, match=message):
        validate_data(read(HEADER + "\n" + row))
