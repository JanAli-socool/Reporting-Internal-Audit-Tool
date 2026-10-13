"""Compile the council's files into docs/design-council.md.

Members never talk to each other directly: each writes members/NN-role.md
after reading the earlier files. This script only reads those files and
groups positions by problem, followed by the chair's decision.
"""
import re
from pathlib import Path

HERE = Path(__file__).parent
SECTION = re.compile(r"^## (P\d+)\s*$", re.MULTILINE)


def sections(text: str) -> dict[str, str]:
    parts = SECTION.split(text)
    return {
        parts[i]: parts[i + 1].strip()
        for i in range(1, len(parts), 2)
        if parts[i + 1].strip() not in ("", "—")
    }


def main() -> None:
    brief = (HERE / "00-brief.md").read_text(encoding="utf-8")
    problems = dict(re.findall(r"^- \*\*(P\d+) — (.+?):\*\*", brief, re.MULTILINE))

    members = []
    for path in sorted((HERE / "members").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        name = text.splitlines()[0].lstrip("# ").strip()
        members.append((name, path.name, sections(text)))

    decision_text = (HERE / "decisions.md").read_text(encoding="utf-8")
    split_at = decision_text.index("## Implementation order")
    decisions = sections(decision_text[:split_at])
    tail = decision_text[split_at:]

    out = [
        "# PerfectSight Design Council — Deliberation",
        "",
        "Compiled by `docs/council/assemble.py` from the files in "
        "`docs/council/`. Members coordinated only through those files "
        "(see `00-brief.md` for the protocol). Edit the sources, not this file.",
        "",
        "**Members:** " + ", ".join(name for name, _, _ in members),
        "",
    ]
    for pid, title in problems.items():
        out += [f"## {pid}: {title}", ""]
        for name, filename, secs in members:
            if pid in secs:
                body = " ".join(secs[pid].split())
                out.append(f"- **{name}** (`{filename}`): {body}")
        out += ["", decisions.get(pid, "**Decision:** _pending_"), ""]
    out.append(tail.strip())
    out.append("")

    target = HERE.parent / "design-council.md"
    target.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {target} ({len(members)} members, {len(problems)} problems)")


if __name__ == "__main__":
    main()
