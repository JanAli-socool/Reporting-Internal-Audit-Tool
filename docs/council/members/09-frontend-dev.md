# Staff Frontend Developer

## P1
Move the section; about an hour of work. The session-state snapshot logic doesn't change.

## P2
One config file (re: 04-design-systems.md). Multiselect pill color follows `primaryColor` automatically.

## P3
Change the `pp_delta` format string to "pts". Trivial.

## P4
`daily_trend` → weekly resample, plus the previous window from `period_comparison`'s bounds. About two hours including tests.

## P5
Needs counts from the backend (see 10-backend-dev.md); rendering is trivial.

## P6
Streamlit can't switch 2×4 vs. 4×2 by breakpoint without CSS hacks (re: 08-mobile-ux.md). I'll do the table columns only.

## P7
A Markdown header with an inline `<span>` for the wordmark. No assets.

## P8
`st.status`, with the graph run via `stream()` so each node completion updates the status. No fake steps.
