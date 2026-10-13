# Design Systems Lead

## P1
No new components needed: an existing `st.container(border=True)` moved up the page.

## P2
Define one theme in `.streamlit/config.toml`: `primaryColor = "#2a78d6"` (categorical slot 1, already validated). Red and green are reserved for status.

## P3
Delta colors follow one rule: good direction = green, bad = red, volume = grey. Document the rule in code next to the tiles.

## P4
Reuse the three validated slots. "Previous period" uses a muted step of the same hue, never a fourth color.

## P5
Use the status palette (success/warning) with an icon and a label, never color alone.

## P7
The wordmark uses theme tokens (ink + primary), so it changes with the theme automatically.

## P8
`st.status` is native and needs no custom CSS.
