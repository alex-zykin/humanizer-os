#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".venv", "venv", "build", "dist", "node_modules"}

FENCED_CODE_RE = re.compile(r"(?ms)^(```|~~~).*?^\1\s*$")
INLINE_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REFERENCE_LINK_RE = re.compile(r"(?m)^\s*\[[^\]]+\]:\s*(\S+)")
HTML_LINK_RE = re.compile(r"(?i)\b(?:href|src)=[\"']([^\"']+)[\"']")


def markdown_files() -> list[Path]:
    return sorted(
        path for path in ROOT.rglob("*.md") if not any(part in IGNORED_PARTS for part in path.parts)
    )


def normalize_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    return unquote(target.strip())


def local_target(source: Path, target: str) -> Path | None:
    if not target or target.startswith(("#", "http://", "https://", "mailto:", "tel:", "data:")):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None
    if target.startswith("/"):
        return ROOT / target.lstrip("/")
    return source.parent / target


def main() -> int:
    failures: list[str] = []
    for source in markdown_files():
        text = FENCED_CODE_RE.sub("", source.read_text(encoding="utf-8"))
        raw_targets = [
            *(match.group(1) for match in INLINE_LINK_RE.finditer(text)),
            *(match.group(1) for match in REFERENCE_LINK_RE.finditer(text)),
            *(match.group(1) for match in HTML_LINK_RE.finditer(text)),
        ]
        for raw in raw_targets:
            target = normalize_target(raw)
            path = local_target(source, target)
            if path is not None and not path.exists():
                failures.append(f"{source.relative_to(ROOT)}: missing local link {target!r}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Documentation links passed ({len(markdown_files())} Markdown files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
