from __future__ import annotations

import collections
import re
from collections.abc import Iterable
from dataclasses import replace

from .models import Fact, VerificationReport
from .text import Span, find_code_spans, overlaps

_MONTHS = (
    "january|february|march|april|may|june|july|august|september|october|november|december|"
    "январ(?:я|ь)|феврал(?:я|ь)|март(?:а)?|апрел(?:я|ь)|ма[йя]|июн(?:я|ь)|июл(?:я|ь)|"
    "август(?:а)?|сентябр(?:я|ь)|октябр(?:я|ь)|ноябр(?:я|ь)|декабр(?:я|ь)"
)

_FACT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "uuid",
        re.compile(
            r"(?<![0-9A-Fa-f])"
            r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[1-8][0-9A-Fa-f]{3}-"
            r"[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}"
            r"(?![0-9A-Fa-f])"
        ),
    ),
    ("url", re.compile(r"https?://[^\s<>()]+", re.IGNORECASE)),
    ("email", re.compile(r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+(?![\w.-])", re.UNICODE)),
    ("date", re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b")),
    (
        "date",
        re.compile(
            rf"\b(?:\d{{1,2}}\s+(?:{_MONTHS})(?:\s+\d{{4}})?|"
            rf"(?:{_MONTHS})\s+\d{{1,2}}(?:,?\s+\d{{4}})?)\b",
            re.IGNORECASE,
        ),
    ),
    ("time", re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d(?:\s?(?:am|pm))?\b", re.IGNORECASE)),
    (
        "money",
        re.compile(
            r"(?<!\w)(?:[$€£¥₽]\s?\d[\d\s.,]*|"
            r"\d[\d\s.,]*\s?(?:USD|EUR|GBP|RUB|₽|€|£|\$))(?!\w)",
            re.IGNORECASE,
        ),
    ),
    ("percent", re.compile(r"(?<!\w)[+-]?\d+(?:[.,]\d+)?\s?%(?!\w)")),
    (
        "measurement",
        re.compile(
            r"(?<!\w)[+-]?\d+(?:[.,]\d+)?\s?"
            r"(?:kg|g|mg|km|m|cm|mm|GB|MB|KB|ms|s|min|h|°C|°F|"
            r"кг|г|мг|км|см|мм|мс|сек|мин|ч)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "version",
        re.compile(
            r"(?<![\w.-])(?:v(?:ersion)?\s*)?\d+\.\d+(?:\.\d+){0,2}"
            r"(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?"
            r"(?:\+[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?"
            r"(?![\w+-]|\.[0-9A-Za-z])",
            re.IGNORECASE,
        ),
    ),
    ("commit", re.compile(r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{7,40}(?![0-9A-Fa-f])")),
    ("handle", re.compile(r"(?<!\w)@[A-Za-z0-9_]{2,30}\b")),
    ("hashtag", re.compile(r"(?<!\w)#[A-Za-zА-Яа-яЁё0-9_]{2,80}\b")),
    ("number", re.compile(r"(?<![\w.-])[+-]?\d+(?:[\s.,]\d+)*(?![\w.-])")),
    ("acronym", re.compile(r"\b(?:[A-ZА-ЯЁ]{2,}(?:-\d+)?|[A-Z]{1,5}\d{1,4})\b")),
    (
        "proper_name",
        re.compile(
            r"\b(?:[A-ZА-ЯЁ][a-zа-яё]+(?:\s+|[-–—])){1,3}"
            r"[A-ZА-ЯЁ][a-zа-яё]+\b"
        ),
    ),
)


def normalize_fact(kind: str, value: str) -> str:
    value = value.strip()
    if kind == "url":
        value = value.rstrip('.,;:!?)]}»”"')
    value = re.sub(r"\s+", " ", value)
    if kind in {"email", "url", "handle", "hashtag", "date", "uuid", "version", "commit"}:
        value = value.casefold()
    return value


def _trim_url_fact(fact: Fact) -> Fact:
    trimmed = fact.value.rstrip('.,;:!?)]}»”"')
    if trimmed == fact.value:
        return fact
    return replace(
        fact,
        value=trimmed,
        normalized=normalize_fact(fact.kind, trimmed),
        end=fact.start + len(trimmed),
    )


def extract_facts(text: str) -> list[Fact]:
    facts: list[Fact] = []
    occupied: list[Span] = []

    for code_span in find_code_spans(text):
        value = text[code_span.start : code_span.end]
        facts.append(Fact("code", value, value, code_span.start, code_span.end))
        occupied.append(code_span)

    for kind, pattern in _FACT_PATTERNS:
        for match in pattern.finditer(text):
            if overlaps(match.start(), match.end(), occupied):
                continue
            value = match.group(0)
            fact = Fact(kind, value, normalize_fact(kind, value), match.start(), match.end())
            if kind == "url":
                fact = _trim_url_fact(fact)
            elif kind in {"money", "percent", "measurement", "number"}:
                trimmed = fact.value.rstrip(".,;:!?")
                if trimmed != fact.value:
                    fact = replace(
                        fact,
                        value=trimmed,
                        normalized=normalize_fact(fact.kind, trimmed),
                        end=fact.start + len(trimmed),
                    )
            if fact.start >= fact.end:
                continue
            facts.append(fact)
            occupied.append(Span(fact.start, fact.end, kind))

    return sorted(facts, key=lambda item: (item.start, item.end, item.kind))


def fact_spans(facts: Iterable[Fact]) -> list[Span]:
    return [Span(item.start, item.end, f"fact:{item.kind}") for item in facts]


def verify_facts(original: str, revised: str) -> VerificationReport:
    original_facts = extract_facts(original)
    revised_facts = extract_facts(revised)

    original_counter = collections.Counter((item.kind, item.normalized) for item in original_facts)
    revised_counter = collections.Counter((item.kind, item.normalized) for item in revised_facts)

    lost_keys = original_counter - revised_counter
    added_keys = revised_counter - original_counter

    lost: list[Fact] = []
    added: list[Fact] = []
    lost_remaining = lost_keys.copy()
    added_remaining = added_keys.copy()

    for item in original_facts:
        key = (item.kind, item.normalized)
        if lost_remaining[key] > 0:
            lost.append(item)
            lost_remaining[key] -= 1
    for item in revised_facts:
        key = (item.kind, item.normalized)
        if added_remaining[key] > 0:
            added.append(item)
            added_remaining[key] -= 1

    return VerificationReport(
        ok=not lost and not added,
        lost=lost,
        added=added,
        original_count=len(original_facts),
        revised_count=len(revised_facts),
    )
