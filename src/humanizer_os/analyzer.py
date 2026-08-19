from __future__ import annotations

import collections
from collections.abc import Iterable

from .detectors import run_detector
from .fixes import span_has_autofix
from .language import resolve_locale
from .models import AuditReport, Confidence, Finding
from .registry import RuleRegistry
from .text import (
    excerpt,
    find_code_spans,
    find_quote_spans,
    find_url_spans,
    line_col,
    mask_spans,
    paragraphs,
    sentences,
    word_count,
)

_CONFIDENCE_RANK: dict[Confidence, int] = {"low": 0, "medium": 1, "high": 2}
_SEVERITY_WEIGHT = {"info": 1.0, "warning": 2.0, "error": 3.0}
_CONFIDENCE_WEIGHT = {"low": 0.4, "medium": 0.7, "high": 1.0}


class Analyzer:
    def __init__(self, registry: RuleRegistry | None = None) -> None:
        self.registry = registry or RuleRegistry()

    def audit(
        self,
        text: str,
        *,
        locale: str = "auto",
        genre: str = "general",
        source: str = "<text>",
        min_confidence: Confidence = "low",
        only_rules: Iterable[str] | None = None,
        exclude_rules: Iterable[str] | None = None,
    ) -> AuditReport:
        resolved_locale, guess = resolve_locale(text, locale)
        allow = set(only_rules or ())
        deny = set(exclude_rules or ())
        self._validate_rule_filters(allow, deny, resolved_locale)

        rules = self.registry.active(resolved_locale, genre, len(text))
        code_spans = find_code_spans(text)
        url_spans = find_url_spans(text)
        quote_spans = find_quote_spans(text)

        findings: list[Finding] = []
        for rule in rules:
            if allow and rule.id not in allow:
                continue
            if rule.id in deny:
                continue
            if _CONFIDENCE_RANK[rule.confidence] < _CONFIDENCE_RANK[min_confidence]:
                continue

            ignored = []
            if rule.ignore_in_code:
                ignored.extend(code_spans)
            if rule.ignore_in_urls:
                ignored.extend(url_spans)
            if rule.ignore_in_quotes:
                ignored.extend(quote_spans)
            scan_text = mask_spans(text, ignored)

            for detection in run_detector(rule, scan_text):
                line, column = line_col(text, detection.start)
                findings.append(
                    Finding(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        confidence=rule.confidence,
                        message=rule.message,
                        suggestion=rule.suggestion,
                        start=detection.start,
                        end=detection.end,
                        line=line,
                        column=column,
                        excerpt=excerpt(text, detection.start, detection.end),
                        fixable=span_has_autofix(rule, text, detection.start, detection.end),
                    )
                )

        findings.sort(key=lambda item: (item.start, item.end, item.rule_id))
        metrics = self._metrics(text, findings)
        return AuditReport(
            source=source,
            locale=resolved_locale,
            detected_language=guess,
            genre=genre,
            findings=findings,
            metrics=metrics,
        )

    def _validate_rule_filters(self, allow: set[str], deny: set[str], locale: str) -> None:
        for rule_id in sorted(allow | deny):
            try:
                rule = self.registry.get(rule_id)
            except KeyError as exc:
                raise ValueError(str(exc)) from exc
            if rule_id in allow and rule.locale != locale:
                raise ValueError(
                    f"Rule {rule_id} belongs to {rule.locale}, "
                    f"but the resolved language is {locale}"
                )

    @staticmethod
    def _metrics(text: str, findings: list[Finding]) -> dict[str, object]:
        words_total = word_count(text)
        sentences_total = len(sentences(text))
        paragraphs_total = len(paragraphs(text))
        categories = collections.Counter(item.category for item in findings)
        severities = collections.Counter(item.severity for item in findings)
        weighted = sum(
            _SEVERITY_WEIGHT[item.severity] * _CONFIDENCE_WEIGHT[item.confidence]
            for item in findings
        )
        # Review priority is a triage index, not an authorship probability.
        per_thousand = weighted * 1000 / max(words_total, 120)
        review_priority = min(100, round(per_thousand * 2.5))
        return {
            "characters": len(text),
            "words": words_total,
            "sentences": sentences_total,
            "paragraphs": paragraphs_total,
            "findings": len(findings),
            "categories": dict(sorted(categories.items())),
            "severities": dict(sorted(severities.items())),
            "review_priority": review_priority,
            "review_priority_note": "Triage index only; not an AI-authorship score.",
        }
