from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from ._version import __version__
from .models import AuditReport, RewriteReport, Rule, VerificationReport
from .profiles import VoiceProfile

_SEVERITY_MARK = {"error": "E", "warning": "W", "info": "I"}


def _count_label(value: int, singular: str, plural: str | None = None) -> str:
    return f"{value} {singular if value == 1 else (plural or singular + 's')}"


def _tool_metadata() -> dict[str, str]:
    return {"name": "humanizer-os", "version": __version__}


def render_audit_text(report: AuditReport, *, show_suggestions: bool = True) -> str:
    lines = [
        f"{report.source}  [{report.locale}/{report.genre}]",
        (
            f"{_count_label(int(report.metrics['words']), 'word')} · "
            f"{_count_label(int(report.metrics['sentences']), 'sentence')} · "
            f"{_count_label(len(report.findings), 'finding')} · "
            f"review priority {report.metrics['review_priority']}/100"
        ),
    ]
    if not report.findings:
        lines.append("OK  No enabled patterns found.")
        return "\n".join(lines)

    for item in report.findings:
        marker = _SEVERITY_MARK[item.severity]
        fix = " · safe fix" if item.fixable else ""
        lines.append(
            f"{marker} {item.rule_id}  {item.line}:{item.column}  "
            f"{item.rule_name} [{item.confidence}{fix}]"
        )
        lines.append(f"  {item.excerpt}")
        lines.append(f"  {item.message}")
        if show_suggestions and item.suggestion:
            lines.append(f"  → {item.suggestion}")
    return "\n".join(lines)


def render_verification_text(report: VerificationReport) -> str:
    if report.ok:
        return f"OK  Protected facts match ({report.original_count} checked)."
    lines = [
        "FAILED  Protected facts changed.",
        f"Original facts: {report.original_count}; revised facts: {report.revised_count}",
    ]
    for item in report.lost:
        lines.append(f"- lost {item.kind}: {item.value}")
    for item in report.added:
        lines.append(f"+ added {item.kind}: {item.value}")
    return "\n".join(lines)


def render_rewrite_text(report: RewriteReport) -> str:
    if report.blocked:
        return "BLOCKED  Fact Guard rejected the rewrite; the original text was restored."
    if not report.changed:
        return "OK  No safe deterministic fixes were needed."
    lines = [
        (
            f"Applied {_count_label(len(report.changes), 'safe fix', 'safe fixes')} "
            f"to {report.source}."
        ),
        f"Findings: {len(report.before_audit.findings)} → {len(report.after_audit.findings)}.",
        render_verification_text(report.verification),
    ]
    for item in report.changes:
        before = item.before.replace("\n", "\\n")
        after = item.after.replace("\n", "\\n")
        lines.append(f"- {item.rule_id} {item.line}:{item.column}: {before!r} → {after!r}")
    return "\n".join(lines)


def render_rules_text(rules: Iterable[Rule]) -> str:
    rows = list(rules)
    if not rows:
        return "No rules match this filter."
    width = max(len(item.id) for item in rows)
    return "\n".join(
        f"{item.id:<{width}}  {item.severity:<7} {item.confidence:<6}  {item.name}"
        for item in rows
    )


def render_rule_text(rule: Rule) -> str:
    genres = ", ".join(rule.genres)
    excluded = ", ".join(rule.excluded_genres) or "none"
    sources = "\n".join(f"- {item}" for item in rule.sources) or "- none"
    return "\n".join(
        [
            f"{rule.id}: {rule.name}",
            f"Locale: {rule.locale}",
            f"Category: {rule.category}",
            f"Severity / confidence: {rule.severity} / {rule.confidence}",
            f"Genres: {genres}; excluded: {excluded}",
            f"Detector: {rule.detector.type}",
            f"Safe autofix: {'yes' if rule.autofix and rule.autofix.safe else 'no'}",
            "",
            rule.description,
            "",
            f"Why it was reported: {rule.message}",
            f"Suggested review: {rule.suggestion}",
            "",
            "Sources:",
            sources,
        ]
    )


def render_profile_text(profile: VoiceProfile) -> str:
    return "\n".join(
        [
            f"Voice profile [{profile.locale}]",
            (
                "Words / sentences / paragraphs: "
                f"{profile.words} / {profile.sentences} / {profile.paragraphs}"
            ),
            f"Sentence length: {profile.avg_sentence_words} ± {profile.sentence_word_stdev} words",
            f"Paragraph length: {profile.avg_paragraph_words} words",
            f"Vocabulary diversity: {profile.type_token_ratio}",
            f"First person / 1000 words: {profile.first_person_per_1000}",
            f"Second person / 1000 words: {profile.second_person_per_1000}",
            (
                "Question / exclamation marks per 1000 chars: "
                f"{profile.question_marks_per_1000} / {profile.exclamation_marks_per_1000}"
            ),
            (
                "Em dashes / semicolons per 1000 chars: "
                f"{profile.em_dashes_per_1000} / {profile.semicolons_per_1000}"
            ),
            f"Emoji-line ratio: {profile.emoji_lines_ratio}",
            f"Bullet-line ratio: {profile.bullet_lines_ratio}",
        ]
    )


def reports_json(reports: Iterable[AuditReport]) -> str:
    payload = {
        "schema_version": 1,
        "tool": _tool_metadata(),
        "reports": [item.to_dict() for item in reports],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def rewrite_json(reports: Iterable[RewriteReport]) -> str:
    payload = {
        "schema_version": 1,
        "tool": _tool_metadata(),
        "reports": [item.to_dict() for item in reports],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def verification_json(report: VerificationReport) -> str:
    payload = {"schema_version": 1, "tool": _tool_metadata(), **report.to_dict()}
    return json.dumps(payload, ensure_ascii=False, indent=2)


def profile_json(profile: VoiceProfile) -> str:
    payload = {"schema_version": 1, "tool": _tool_metadata(), **profile.to_dict()}
    return json.dumps(payload, ensure_ascii=False, indent=2)


def rules_json(rules: Iterable[Rule]) -> str:
    payload = []
    for rule in rules:
        payload.append(
            {
                "id": rule.id,
                "locale": rule.locale,
                "name": rule.name,
                "description": rule.description,
                "category": rule.category,
                "severity": rule.severity,
                "confidence": rule.confidence,
                "message": rule.message,
                "suggestion": rule.suggestion,
                "genres": list(rule.genres),
                "excluded_genres": list(rule.excluded_genres),
                "detector": {
                    "type": rule.detector.type,
                    "patterns": list(rule.detector.patterns),
                    "params": rule.detector.params,
                },
                "safe_autofix": bool(rule.autofix and rule.autofix.safe),
                "sources": list(rule.sources),
            }
        )
    envelope = {"schema_version": 1, "tool": _tool_metadata(), "rules": payload}
    return json.dumps(envelope, ensure_ascii=False, indent=2)


def reports_sarif(reports: Iterable[AuditReport]) -> str:
    reports = list(reports)
    rule_meta: dict[str, dict[str, object]] = {}
    results: list[dict[str, object]] = []
    level_map = {"error": "error", "warning": "warning", "info": "note"}

    for report in reports:
        source = report.source
        if source not in {"<stdin>", "<text>"}:
            try:
                source = Path(source).as_posix()
            except TypeError:
                pass
        for item in report.findings:
            rule_meta.setdefault(
                item.rule_id,
                {
                    "id": item.rule_id,
                    "name": item.rule_name.replace(" ", "_"),
                    "shortDescription": {"text": item.rule_name},
                    "fullDescription": {"text": item.message},
                    "help": {"text": item.suggestion or item.message},
                    "properties": {
                        "category": item.category,
                        "confidence": item.confidence,
                    },
                },
            )
            results.append(
                {
                    "ruleId": item.rule_id,
                    "level": level_map[item.severity],
                    "message": {"text": item.message},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": source},
                                "region": {
                                    "startLine": item.line,
                                    "startColumn": item.column,
                                    "charOffset": item.start,
                                    "charLength": max(1, item.end - item.start),
                                },
                            }
                        }
                    ],
                }
            )

    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "HumanizerOS",
                        "informationUri": "https://github.com/alex-zykin/humanizer-os",
                        "version": __version__,
                        "rules": [rule_meta[key] for key in sorted(rule_meta)],
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
