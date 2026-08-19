from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

WORD_RE = re.compile(r"[A-Za-zА-Яа-яЁё]+(?:['’\-][A-Za-zА-Яа-яЁё]+)*|\d+(?:[.,]\d+)?", re.UNICODE)


@dataclass(frozen=True, slots=True)
class Span:
    start: int
    end: int
    kind: str


@dataclass(frozen=True, slots=True)
class TextSegment:
    text: str
    start: int
    end: int


def overlaps(start: int, end: int, spans: Iterable[Span | tuple[int, int]]) -> bool:
    for span in spans:
        span_start, span_end = (span.start, span.end) if isinstance(span, Span) else span
        if start < span_end and end > span_start:
            return True
    return False


def find_code_spans(text: str) -> list[Span]:
    spans: list[Span] = []

    # Markdown treats an unclosed fence as code through end-of-file. Protect it
    # as well; linting prose inside a partially written code block is noisier
    # and potentially unsafe for automated fixes.
    opener = re.compile(r"(?m)^[ \t]{0,3}(`{3,}|~{3,})[^\n]*(?:\n|$)")
    cursor = 0
    while match := opener.search(text, cursor):
        fence = match.group(1)
        marker = re.escape(fence[0])
        closer = re.compile(rf"(?m)^[ \t]{{0,3}}{marker}{{{len(fence)},}}[ \t]*(?:\n|$)")
        closing = closer.search(text, match.end())
        end = closing.end() if closing else len(text)
        spans.append(Span(match.start(), end, "code_block"))
        cursor = max(end, match.end())

    for match in re.finditer(r"(?<!`)`[^`\n]+`(?!`)", text):
        if not overlaps(match.start(), match.end(), spans):
            spans.append(Span(match.start(), match.end(), "inline_code"))
    for match in re.finditer(r"(?m)^ {4,}\S.*$", text):
        if not overlaps(match.start(), match.end(), spans):
            spans.append(Span(match.start(), match.end(), "indented_code"))
    return sorted(spans, key=lambda item: (item.start, item.end))


def find_url_spans(text: str) -> list[Span]:
    spans: list[Span] = []
    for match in re.finditer(r"https?://[^\s<>()]+", text, re.IGNORECASE):
        end = match.end()
        while end > match.start() and text[end - 1] in ".,;:!?)]}»”":
            end -= 1
        spans.append(Span(match.start(), end, "url"))
    for match in re.finditer(r"\[[^\]]+\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", text):
        start, end = match.span(1)
        spans.append(Span(start, end, "markdown_url"))
    return sorted(spans, key=lambda item: (item.start, item.end))


def find_quote_spans(text: str) -> list[Span]:
    spans: list[Span] = []
    patterns = (
        r"«[^»\n]{1,1000}»",
        r"“[^”\n]{1,1000}”",
        r"„[^“\n]{1,1000}“",
        r"(?<!\w)\"[^\"\n]{1,500}\"(?!\w)",
        r"(?m)^(?:[ \t]*>[^\n]*(?:\n|$))+",
    )
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            if not overlaps(match.start(), match.end(), spans):
                spans.append(Span(match.start(), match.end(), "quote"))
    return sorted(spans, key=lambda item: (item.start, item.end))


def mask_spans(text: str, spans: Iterable[Span | tuple[int, int]]) -> str:
    if not text:
        return text
    chars = list(text)
    for span in spans:
        start, end = (span.start, span.end) if isinstance(span, Span) else span
        for index in range(max(0, start), min(len(chars), end)):
            if chars[index] not in "\r\n":
                chars[index] = " "
    return "".join(chars)


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def word_count(text: str) -> int:
    return len(words(text))


def sentences(text: str) -> list[TextSegment]:
    segments: list[TextSegment] = []
    # The splitter is intentionally conservative. It treats line endings as weak
    # boundaries and preserves offsets for diagnostics.
    pattern = re.compile(r"[^.!?…\n]+(?:[.!?…]+(?:[\"'»”’\)\]]*)|(?=\n|$))", re.UNICODE)
    for match in pattern.finditer(text):
        raw = match.group(0)
        left_trim = len(raw) - len(raw.lstrip())
        right_trim = len(raw.rstrip())
        start = match.start() + left_trim
        end = match.start() + right_trim
        if start < end and WORD_RE.search(text[start:end]):
            segments.append(TextSegment(text[start:end], start, end))
    return segments


def paragraphs(text: str) -> list[TextSegment]:
    segments: list[TextSegment] = []
    for match in re.finditer(r"(?:^|\n\s*\n)([^\n](?:[\s\S]*?))(?=\n\s*\n|$)", text):
        start, end = match.span(1)
        raw = text[start:end]
        left_trim = len(raw) - len(raw.lstrip())
        right_trim = len(raw.rstrip())
        start += left_trim
        end = start + max(0, right_trim - left_trim)
        if start < end and WORD_RE.search(text[start:end]):
            segments.append(TextSegment(text[start:end], start, end))
    return segments


def line_col(text: str, offset: int) -> tuple[int, int]:
    offset = max(0, min(len(text), offset))
    line = text.count("\n", 0, offset) + 1
    line_start = text.rfind("\n", 0, offset) + 1
    column = offset - line_start + 1
    return line, column


def excerpt(text: str, start: int, end: int, limit: int = 160) -> str:
    if not text:
        return ""
    start = max(0, start)
    end = min(len(text), max(start, end))
    radius = max(20, (limit - (end - start)) // 2)
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    value = re.sub(r"\s+", " ", text[left:right]).strip()
    if left > 0:
        value = "…" + value
    if right < len(text):
        value += "…"
    return value[: limit + 1]


def normalized_start(value: str, count: int = 2) -> str:
    tokens = [token.casefold() for token in words(value)]
    return " ".join(tokens[:count])
