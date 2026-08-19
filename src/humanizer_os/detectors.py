from __future__ import annotations

import collections
import re
import statistics
from collections.abc import Callable
from dataclasses import dataclass

from .models import Rule
from .text import normalized_start, paragraphs, sentences, word_count


@dataclass(frozen=True, slots=True)
class Detection:
    start: int
    end: int


Detector = Callable[[Rule, str], list[Detection]]


def _starts_in_markdown_structure(text: str, start: int, segment: str = "") -> bool:
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", start)
    if line_end == -1:
        line_end = len(text)
    line = text[line_start:line_end]
    if re.match(r"\s*(?:[-*+] |\d+[.)]\s+|#{1,6}\s+|>\s*|\|)", line):
        return True
    return bool(re.match(r"\s*\*\*[^*\n]{1,80}:?\*\*\s+", segment))


def detect_regex(rule: Rule, text: str) -> list[Detection]:
    params = rule.detector.params
    flags = re.UNICODE
    if not bool(params.get("case_sensitive", False)):
        flags |= re.IGNORECASE
    if bool(params.get("multiline", True)):
        flags |= re.MULTILINE
    if bool(params.get("dotall", False)):
        flags |= re.DOTALL

    findings: list[Detection] = []
    for pattern in rule.detector.patterns:
        for match in re.finditer(pattern, text, flags):
            start, end = match.span()
            if start < end:
                findings.append(Detection(start, end))
    return _deduplicate(findings)


def detect_short_sentence_stack(rule: Rule, text: str) -> list[Detection]:
    params = rule.detector.params
    max_words = int(params.get("max_words", 4))
    min_words = int(params.get("min_words", 1))
    min_run = int(params.get("min_run", 3))
    candidates = sentences(text)
    findings: list[Detection] = []
    run: list = []

    def flush() -> None:
        nonlocal run
        if len(run) >= min_run:
            findings.append(Detection(run[0].start, run[-1].end))
        run = []

    for segment in candidates:
        count = word_count(segment.text)
        is_structured = _starts_in_markdown_structure(text, segment.start, segment.text)
        if min_words <= count <= max_words and not is_structured:
            run.append(segment)
        else:
            flush()
    flush()
    return findings


def detect_uniform_paragraphs(rule: Rule, text: str) -> list[Detection]:
    params = rule.detector.params
    min_paragraphs = int(params.get("min_paragraphs", 4))
    min_words = int(params.get("min_words", 12))
    max_cv = float(params.get("max_cv", 0.16))
    items = [
        item
        for item in paragraphs(text)
        if not item.text.lstrip().startswith(("#", "- ", "* ", ">"))
    ]
    counts = [word_count(item.text) for item in items]
    if len(counts) < min_paragraphs or statistics.fmean(counts) < min_words:
        return []
    mean = statistics.fmean(counts)
    cv = statistics.pstdev(counts) / mean if mean else 0.0
    if cv <= max_cv:
        return [Detection(items[0].start, items[-1].end)]
    return []


def detect_uniform_sentences(rule: Rule, text: str) -> list[Detection]:
    params = rule.detector.params
    min_sentences = int(params.get("min_sentences", 8))
    min_words = int(params.get("min_words", 6))
    max_cv = float(params.get("max_cv", 0.20))
    items = [item for item in sentences(text) if word_count(item.text) >= min_words]
    counts = [word_count(item.text) for item in items]
    if len(counts) < min_sentences:
        return []
    mean = statistics.fmean(counts)
    cv = statistics.pstdev(counts) / mean if mean else 0.0
    if cv <= max_cv:
        return [Detection(items[0].start, items[-1].end)]
    return []


def detect_repeated_starts(rule: Rule, text: str) -> list[Detection]:
    params = rule.detector.params
    prefix_words = int(params.get("prefix_words", 2))
    min_count = int(params.get("min_count", 3))
    min_sentences = int(params.get("min_sentences", 5))
    items = sentences(text)
    if len(items) < min_sentences:
        return []

    groups: dict[str, list] = collections.defaultdict(list)
    for item in items:
        if _starts_in_markdown_structure(text, item.start, item.text):
            continue
        key = normalized_start(item.text, prefix_words)
        if key and len(key) >= 3:
            groups[key].append(item)

    findings: list[Detection] = []
    for group in groups.values():
        if len(group) >= min_count:
            findings.append(Detection(group[0].start, group[-1].end))
    return _deduplicate(findings)


def detect_transition_density(rule: Rule, text: str) -> list[Detection]:
    params = rule.detector.params
    phrases = [str(item) for item in params.get("phrases", [])]
    min_count = int(params.get("min_count", 3))
    min_paragraphs = int(params.get("min_paragraphs", 4))
    min_ratio = float(params.get("min_ratio", 0.5))
    if not phrases:
        return []

    items = paragraphs(text)
    if len(items) < min_paragraphs:
        return []
    phrase_re = re.compile(r"^(?:" + "|".join(phrases) + r")\b", re.IGNORECASE)
    hits = [item for item in items if phrase_re.search(item.text.lstrip())]
    if len(hits) >= min_count and len(hits) / len(items) >= min_ratio:
        return [Detection(hits[0].start, hits[-1].end)]
    return []


def detect_dash_density(rule: Rule, text: str) -> list[Detection]:
    params = rule.detector.params
    chars = str(params.get("characters", "—"))
    min_count = int(params.get("min_count", 4))
    max_per_1000 = float(params.get("max_per_1000", 5.0))
    positions = [index for index, char in enumerate(text) if char in chars]
    denominator = max(len(text), 1)
    density = len(positions) * 1000 / denominator
    if len(positions) >= min_count and density > max_per_1000:
        return [Detection(positions[0], positions[-1] + 1)]
    return []


def detect_title_case_headings(rule: Rule, text: str) -> list[Detection]:
    params = rule.detector.params
    min_words = int(params.get("min_words", 3))
    min_ratio = float(params.get("min_ratio", 0.75))
    small_words = {
        "a",
        "an",
        "and",
        "as",
        "at",
        "but",
        "by",
        "for",
        "in",
        "of",
        "on",
        "or",
        "the",
        "to",
        "vs",
        "with",
    }
    findings: list[Detection] = []
    for match in re.finditer(r"(?m)^(#{1,6})\s+(.+?)\s*$", text):
        title = re.sub(r"[`*_]", "", match.group(2)).strip()
        tokens = [
            token
            for token in re.findall(r"[A-Za-z][A-Za-z'’-]*", title)
            if token.casefold() not in small_words
        ]
        if len(tokens) < min_words:
            continue
        titled = sum(1 for token in tokens if token[:1].isupper())
        if titled / len(tokens) >= min_ratio:
            start, end = match.span(2)
            findings.append(Detection(start, end))
    return findings


def detect_bold_list_headings(rule: Rule, text: str) -> list[Detection]:
    pattern = re.compile(r"(?m)^\s*(?:[-*+] |\d+[.)]\s+)\*\*[^*\n]{2,80}:?\*\*\s+")
    return [Detection(match.start(), match.end()) for match in pattern.finditer(text)]


def detect_emoji_bullets(rule: Rule, text: str) -> list[Detection]:
    # Broad emoji ranges are intentional here; the detector only fires at line starts.
    pattern = re.compile(r"(?m)^\s*(?:[-*+]\s+)?[\U0001F300-\U0001FAFF\u2600-\u27BF](?:\uFE0F)?\s+")
    return [Detection(match.start(), match.end()) for match in pattern.finditer(text)]


def detect_list_density(rule: Rule, text: str) -> list[Detection]:
    params = rule.detector.params
    min_lines = int(params.get("min_lines", 8))
    min_items = int(params.get("min_items", 5))
    min_ratio = float(params.get("min_ratio", 0.55))
    lines = list(re.finditer(r"(?m)^.*$", text))
    meaningful = [item for item in lines if item.group(0).strip()]
    if len(meaningful) < min_lines:
        return []
    bullets = [item for item in meaningful if re.match(r"\s*(?:[-*+] |\d+[.)]\s+)", item.group(0))]
    if len(bullets) >= min_items and len(bullets) / len(meaningful) >= min_ratio:
        return [Detection(bullets[0].start(), bullets[-1].end())]
    return []


def _deduplicate(items: list[Detection]) -> list[Detection]:
    seen: set[tuple[int, int]] = set()
    result: list[Detection] = []
    for item in sorted(items, key=lambda value: (value.start, value.end)):
        key = (item.start, item.end)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


DETECTORS: dict[str, Detector] = {
    "regex": detect_regex,
    "short_sentence_stack": detect_short_sentence_stack,
    "uniform_paragraphs": detect_uniform_paragraphs,
    "uniform_sentences": detect_uniform_sentences,
    "repeated_starts": detect_repeated_starts,
    "transition_density": detect_transition_density,
    "dash_density": detect_dash_density,
    "title_case_headings": detect_title_case_headings,
    "bold_list_headings": detect_bold_list_headings,
    "emoji_bullets": detect_emoji_bullets,
    "list_density": detect_list_density,
}


def run_detector(rule: Rule, text: str) -> list[Detection]:
    try:
        detector = DETECTORS[rule.detector.type]
    except KeyError as exc:
        raise ValueError(f"Unknown detector type: {rule.detector.type}") from exc
    return detector(rule, text)[: rule.max_findings]
