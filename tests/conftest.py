import pandas as pd
import pytest

from reporting.data import generate_sample_data, validate_data
from reporting.workflow import ReportOutput


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return validate_data(generate_sample_data(days=90, end_date="2026-10-14"))


GOOD_REPORT = {
    "executive_summary": "Revenue reached $360,188 with a 50.5% margin.",
    "key_findings": [
        "Profit was $181,991.",
        "SLA compliance fell 3.6 percentage points to 85.4%.",
        "Revenue grew 2.9% versus the previous period.",
    ],
    "recommendations": ["Investigate the SLA decline in Operations."],
    "risks_or_caveats": ["The data is synthetic."],
}


class FakeStructuredLLM:
    """Stands in for ChatOpenAI: returns a fixed report or raises."""

    def __init__(self, report: dict | None = None, error: Exception | None = None):
        self.report = report if report is not None else GOOD_REPORT
        self.error = error
        self.prompts: list[str] = []

    def with_structured_output(self, schema):
        assert schema is ReportOutput
        return self

    def invoke(self, prompt):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return dict(self.report)
