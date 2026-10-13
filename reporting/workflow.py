import json
import os
from typing import TypedDict

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()

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
    report: dict
    validation_message: str

def generate_report(state: ReportState) -> dict:
    """Generate structured narrative from calculated metrics."""
    model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        timeout=60,
        max_retries=1,
    )

    structured_model = model.with_structured_output(ReportOutput)

    prompt = f"""
You are an internal business reporting analyst.

Create a concise management report using ONLY the supplied
metrics and department aggregates.

Rules:
- Never invent figures, causes, targets, or business context.
- Distinguish observed facts from possible explanations.
- Do not claim a trend unless the data supports it.
- Use percentages and financial values as provided.
- Recommendations must be tied to observed evidence.
- If context is missing, state what needs investigation.
- Synthetic demo data must not be represented as real company data.

Overall metrics:
{json.dumps(state["metrics"], indent=2)}

Department aggregates:
{json.dumps(state["departments"], indent=2)}
"""

    result = structured_model.invoke(prompt)
    return {"report": result.model_dump()}

def validate_report(state: ReportState) -> dict:
    """Apply basic deterministic checks to the generated report."""
    report = state["report"]
    required = [
        "executive_summary",
        "key_findings",
        "recommendations",
        "risks_or_caveats",
    ]

    missing = [
        key for key in required
        if key not in report or not report[key]
    ]

    if missing:
        raise ValueError(
            f"Generated report is missing sections: {missing}"
        )

    if not isinstance(report["key_findings"], list):
        raise ValueError("Key findings must be a list.")

    if not isinstance(report["recommendations"], list):
        raise ValueError("Recommendations must be a list.")

    return {
        "validation_message": "Report structure validated successfully."
    }

def build_reporting_graph():
    graph = StateGraph(ReportState)

    graph.add_node("generate_report", generate_report)
    graph.add_node("validate_report", validate_report)

    graph.add_edge(START, "generate_report")
    graph.add_edge("generate_report", "validate_report")
    graph.add_edge("validate_report", END)

    return graph.compile()

def create_report(metrics: dict, departments: list[dict]) -> dict:
    workflow = build_reporting_graph()

    result = workflow.invoke({
        "metrics": metrics,
        "departments": departments,
        "report": {},
        "validation_message": "",
    })

    return {
        "report": result["report"],
        "validation_message": result["validation_message"],
    }