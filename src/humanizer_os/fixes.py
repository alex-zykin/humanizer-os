from __future__ import annotations

import re
from collections.abc import Iterator

from .models import Replacement, Rule


def autofix_flags(rule: Rule) -> re.RegexFlag:
    """Return the regex flags shared by a rule detector and its safe fixes."""
    flags = re.UNICODE
    params = rule.detector.params
    if not bool(params.get("case_sensitive", False)):
        flags |= re.IGNORECASE
    if bool(params.get("multiline", True)):
        flags |= re.MULTILINE
    if bool(params.get("dotall", False)):
        flags |= re.DOTALL
    return flags


def iter_autofix_matches(rule: Rule, text: str) -> Iterator[tuple[Replacement, re.Match[str]]]:
    if not rule.autofix or not rule.autofix.safe:
        return
    flags = autofix_flags(rule)
    for replacement in rule.autofix.replacements:
        for match in re.finditer(replacement.pattern, text, flags):
            yield replacement, match


def span_has_autofix(rule: Rule, text: str, start: int, end: int) -> bool:
    return any(
        match.start() == start and match.end() == end
        for _, match in iter_autofix_matches(rule, text)
    )


def preserve_case(before: str, after: str) -> str:
    """Preserve all-caps or initial-capital casing for deterministic replacements."""
    if not after:
        return after

    before_letters = [char for char in before if char.isalpha()]
    after_letters = [index for index, char in enumerate(after) if char.isalpha()]
    if not before_letters or not after_letters:
        return after

    if all(char.isupper() for char in before_letters):
        return after.upper()

    first_before = before_letters[0]
    first_after_index = after_letters[0]
    if first_before.isupper() and after[first_after_index].islower():
        return (
            after[:first_after_index]
            + after[first_after_index].upper()
            + after[first_after_index + 1 :]
        )
    return after
