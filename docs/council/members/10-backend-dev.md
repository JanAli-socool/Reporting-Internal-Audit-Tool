# Staff Backend Developer

## P4
The data is correct; it's seeded noise. Don't "fix" it by tuning the generator to look nicer; that's manufacturing a story. Change the chart (agree with 05-visual-design.md).

## P5
`validate_report` already parses every figure. Return `figures_checked` and `figures_matched` alongside the warnings. Small change, and covered by the existing workflow tests.

## P8
One structured call, a 60 s timeout, and one retry: typically 5–15 s with gpt-4o-mini. Using `workflow.stream()` for real node events (re: 09-frontend-dev.md) is supported in LangGraph 1.2.
