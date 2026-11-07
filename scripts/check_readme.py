#!/usr/bin/env python3
"""Fail when README.md contains mismatched HTML heading tags."""

from __future__ import annotations

import re
import sys
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"
HEADING = re.compile(r"<(/?)(h[1-6])\b[^>]*>", re.IGNORECASE)
FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")


def code_spans(text: str) -> list[tuple[int, int]]:
    spans = [match.span() for match in FENCED_CODE.finditer(text)]
    spans.extend(match.span() for match in INLINE_CODE.finditer(text))
    return spans


def inside_span(spans: list[tuple[int, int]], index: int) -> bool:
    return any(start <= index < end for start, end in spans)


def heading_problems(text: str) -> list[str]:
    spans = code_spans(text)
    stack: list[tuple[str, int]] = []
    found: list[str] = []

    for match in HEADING.finditer(text):
        if inside_span(spans, match.start()):
            continue
        closing = match.group(1) == "/"
        tag = match.group(2).lower()
        line = text.count("\n", 0, match.start()) + 1
        if not closing:
            stack.append((tag, line))
            continue
        if not stack:
            found.append(f"line {line}: </{tag}> has no opening <{tag}>")
            continue
        opened, opened_line = stack.pop()
        if opened != tag:
            found.append(
                f"line {line}: </{tag}> closes <{opened}> opened on line {opened_line}"
            )

    for tag, line in stack:
        found.append(f"line {line}: <{tag}> is never closed")
    return found


def assert_problem_count(text: str, expected: int, label: str) -> None:
    found = heading_problems(text)
    if len(found) != expected:
        details = "\n".join(found) or "(no problems)"
        raise SystemExit(f"self-check failed for {label}:\n{details}")


def self_check() -> None:
    assert_problem_count("<h1>Built with AI Studio</h2>\n", 1, "mismatched heading")
    assert_problem_count("<h1>Title</h1>\n", 0, "matching heading")
    assert_problem_count("# Title\n\nPlain text.\n", 0, "markdown heading")
    assert_problem_count("</h1>\n", 1, "closing tag without an opening tag")
    assert_problem_count("<h2>Section\n", 1, "heading left open")
    assert_problem_count("<H1 id=\"title\">Title</h1>\n", 0, "heading with attributes")
    assert_problem_count(
        "The old file used `<h1>Title</h2>` inside code.\n",
        0,
        "heading mentioned in inline code",
    )
    assert_problem_count(
        "```html\n<h1>Title</h2>\n```\n\n# Title\n",
        0,
        "heading inside a fenced example",
    )


def main() -> int:
    self_check()
    if not README.is_file():
        print(f"Missing {README}", file=sys.stderr)
        return 1
    text = README.read_text(encoding="utf-8")
    if not text.strip():
        print("README.md is empty", file=sys.stderr)
        return 1
    found = heading_problems(text)
    if found:
        print("README.md has broken HTML headings:", file=sys.stderr)
        for item in found:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("README.md headings are balanced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
