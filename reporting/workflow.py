import json
import math
import os
import re
from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

load_dotenv()

REPORT_SECTIONS = [
    "executive_summary",
    "key_findings",
    "recommendations",
    "risks_or_caveats",
]


class ReportOutput(BaseModel):
    executive_summary: str = Field(
        description="A concise management summary based on the supplied metrics"
    )
    key_findings: list[str] = Field(
        description="Three to five evidence-based observations"
    )
    recommendations: list[str] = Field(
        description="Practical next steps supported by the data"
    )
    risks_or_caveats: list[str] = Field(
        description="Limitations, data-quality concerns, or missing context"
    )


class ReportState(TypedDict):
    metrics: dict
    departments: list[dict]
    comparison: dict
    data_source: str
    report: dict
    validation_message: str
    warnings: list[str]


def get_chat_model() -> BaseChatModel:
    """Create the configured LLM. Imported lazily so tests need no key."""
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        timeout=60,
        max_retries=1,
    )


def _json_safe(value):
    """Replace NaN/inf (e.g. a 0/0 department ratio) with null for the prompt."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value


def build_prompt(state: ReportState) -> str:
    comparison = state.get("comparison") or {}
    if comparison.get("available"):
        comparison_text = (
            "Previous period "
            f"({comparison['previous_period_start']} to "
            f"{comparison['previous_period_end']}) vs. selected period. "
            "Percentage KPIs change in percentage points:\n"
            + json.dumps(_json_safe(comparison["changes"]), indent=2)
        )
    else:
        comparison_text = (
            "Not available: the dataset does not fully cover the preceding "
            "period of equal length. Do not describe changes over time."
        )

    return f"""
You are an internal business reporting analyst.

Create a concise management report using ONLY the supplied
metrics, department aggregates, and period comparison.

Rules:
- Never invent figures, causes, targets, or business context.
- Distinguish observed facts from possible explanations.
- Do not claim a trend unless the period comparison supports it.
- Use percentages and financial values exactly as provided.
- Recommendations must be tied to observed evidence.
- If context is missing, state what needs investigation.
- Synthetic demo data must not be represented as real company data.

Data source: {state.get("data_source") or "unspecified"}

Overall metrics:
{json.dumps(_json_safe(state["metrics"]), indent=2)}

Department aggregates:
{json.dumps(_json_safe(state["departments"]), indent=2)}

Period-over-period comparison:
{comparison_text}
"""


# --------------------------------------------------
# Figure grounding: flag numbers the evidence cannot account for
# --------------------------------------------------
_NUMBER = re.compile(
    r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?"
    r"(?:\s*(k|m|thousand|million)\b)?",
    re.IGNORECASE,
)
_SCALES = {"k": 1_000, "thousand": 1_000, "m": 1_000_000, "million": 1_000_000}


def _evidence_values(*sources) -> list[float]:
    values: list[float] = []

    def walk(item):
        if isinstance(item, bool):
            return
        if isinstance(item, (int, float)):
            if math.isfinite(item):
                values.append(float(item))
        elif isinstance(item, dict):
            for v in item.values():
                walk(v)
        elif isinstance(item, (list, tuple)):
            for v in item:
                walk(v)

    for source in sources:
        walk(source)
    return values


def _matches_evidence(
    number: float, decimals: int, scale: float, evidence: list[float]
) -> bool:
    """A figure is grounded if some evidence value rounds to it.

    Abbreviated values ("$1.02M") are compared in their written unit and
    precision. The sign is ignored so "a decrease of 3.2" can match a
    change of -3.2.
    """
    tolerance = 0.5 * 10 ** -decimals + 1e-9
    return any(
        abs(abs(value) / scale - number) <= tolerance for value in evidence
    )


def find_unverified_figures(report: dict, evidence: list) -> list[str]:
    """Return figures in the report text that no supplied value supports.

    This is a heuristic safety net, not proof of correctness: small counts
    (e.g. "three departments") and dates are ignored.
    """
    values = _evidence_values(evidence)
    texts = [report.get("executive_summary", "")]
    for key in REPORT_SECTIONS[1:]:
        texts.extend(report.get(key, []))

    unverified = []
    for text in texts:
        # Dates like 2026-07-16 are period labels, not figures.
        text = re.sub(r"\d{4}-\d{2}-\d{2}", " ", text)
        for match in _NUMBER.finditer(text):
            whole, frac, suffix = match.groups()
            raw = match.group(0).strip()
            number = float(whole.replace(",", "") + (frac or ""))
            decimals = len(frac) - 1 if frac else 0

            scale = _SCALES.get((suffix or "").lower(), 1)
            if scale == 1 and not frac and number <= 10:
                continue

            if not _matches_evidence(number, decimals, scale, values):
                if raw not in unverified:
                    unverified.append(raw)
    return unverified


# --------------------------------------------------
# Graph nodes
# --------------------------------------------------
def make_generate_node(llm: BaseChatModel | None = None):
    def generate_report(state: ReportState) -> dict:
        """Generate structured narrative from calculated metrics."""
        model = llm or get_chat_model()
        structured_model = model.with_structured_output(ReportOutput)
        result = structured_model.invoke(build_prompt(state))
        if isinstance(result, BaseModel):
            result = result.model_dump()
        return {"report": result}

    return generate_report


def validate_report(state: ReportState) -> dict:
    """Apply deterministic checks to the generated report.

    Structural problems fail the workflow. Unverified figures do not, but
    they are surfaced so a human reviewer knows what to double-check.
    """
    report = state["report"] or {}

    missing = [key for key in REPORT_SECTIONS if not report.get(key)]
    if missing:
        raise ValueError(f"Generated report is missing sections: {missing}")

    if not isinstance(report["executive_summary"], str):
        raise ValueError("Executive summary must be text.")

    for key in REPORT_SECTIONS[1:]:
        items = report[key]
        if not isinstance(items, list):
            raise ValueError(f"{key} must be a list.")
        if not all(isinstance(i, str) and i.strip() for i in items):
            raise ValueError(f"{key} must contain non-empty text items.")

    warnings = []
    if not 3 <= len(report["key_findings"]) <= 5:
        warnings.append(
            f"Expected 3-5 key findings, received "
            f"{len(report['key_findings'])}."
        )

    unverified = find_unverified_figures(
        report,
        [state["metrics"], state["departments"], state.get("comparison")],
    )
    if unverified:
        warnings.append(
            "Figures not found in the calculated metrics (verify before "
            "use): " + ", ".join(unverified)
        )

    message = "Report structure validated successfully."
    if not unverified:
        message += " All quoted figures match the calculated metrics."

    return {"validation_message": message, "warnings": warnings}


def build_reporting_graph(llm: BaseChatModel | None = None):
    graph = StateGraph(ReportState)

    graph.add_node("generate_report", make_generate_node(llm))
    graph.add_node("validate_report", validate_report)

    graph.add_edge(START, "generate_report")
    graph.add_edge("generate_report", "validate_report")
    graph.add_edge("validate_report", END)

    return graph.compile()


def create_report(
    metrics: dict,
    departments: list[dict],
    comparison: dict | None = None,
    data_source: str = "",
    llm: BaseChatModel | None = None,
) -> dict:
    workflow = build_reporting_graph(llm)

    result = workflow.invoke({
        "metrics": metrics,
        "departments": departments,
        "comparison": comparison or {},
        "data_source": data_source,
        "report": {},
        "validation_message": "",
        "warnings": [],
    })

    return {
        "report": result["report"],
        "validation_message": result["validation_message"],
        "warnings": result["warnings"],
    }
