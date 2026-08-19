from __future__ import annotations

from dataclasses import dataclass

from .analyzer import Analyzer
from .facts import extract_facts, fact_spans, verify_facts
from .fixes import iter_autofix_matches, preserve_case
from .language import resolve_locale
from .models import Change, RewriteReport, Rule
from .registry import RuleRegistry
from .text import find_code_spans, find_url_spans, line_col, overlaps


@dataclass(frozen=True, slots=True)
class _Candidate:
    rule: Rule
    start: int
    end: int
    before: str
    after: str


class Rewriter:
    """Applies only deterministic fixes marked safe by a rule author."""

    def __init__(
        self,
        registry: RuleRegistry | None = None,
        analyzer: Analyzer | None = None,
    ) -> None:
        self.registry = registry or RuleRegistry()
        self.analyzer = analyzer or Analyzer(self.registry)

    def fix(
        self,
        text: str,
        *,
        locale: str = "auto",
        genre: str = "general",
        source: str = "<text>",
    ) -> RewriteReport:
        resolved_locale, _ = resolve_locale(text, locale)
        before_audit = self.analyzer.audit(
            text,
            locale=resolved_locale,
            genre=genre,
            source=source,
        )
        # A replacement is eligible only when the analyzer reported the exact
        # span as fixable. This keeps detector masking, genre gates, and fixes in
        # one consistent decision path.
        allowed = {
            (finding.rule_id, finding.start, finding.end)
            for finding in before_audit.findings
            if finding.fixable
        }
        protected = [
            *fact_spans(extract_facts(text)),
            *find_code_spans(text),
            *find_url_spans(text),
        ]

        candidates: list[_Candidate] = []
        for rule in self.registry.active(resolved_locale, genre, len(text)):
            if not rule.autofix or not rule.autofix.safe:
                continue
            for replacement, match in iter_autofix_matches(rule, text):
                key = (rule.id, match.start(), match.end())
                if key not in allowed:
                    continue
                if overlaps(match.start(), match.end(), protected):
                    continue
                before = match.group(0)
                after = preserve_case(before, match.expand(replacement.replacement))
                if after == before:
                    continue
                candidates.append(
                    _Candidate(
                        rule=rule,
                        start=match.start(),
                        end=match.end(),
                        before=before,
                        after=after,
                    )
                )

        selected = self._select_non_overlapping(candidates)
        revised = text
        for item in reversed(selected):
            revised = revised[: item.start] + item.after + revised[item.end :]

        verification = verify_facts(text, revised)
        blocked = not verification.ok
        if blocked:
            revised = text
            selected = []
            verification = verify_facts(text, revised)

        changes: list[Change] = []
        for item in selected:
            line, column = line_col(text, item.start)
            changes.append(
                Change(
                    rule_id=item.rule.id,
                    start=item.start,
                    end=item.end,
                    before=item.before,
                    after=item.after,
                    line=line,
                    column=column,
                )
            )

        after_audit = self.analyzer.audit(
            revised,
            locale=resolved_locale,
            genre=genre,
            source=source,
        )
        return RewriteReport(
            source=source,
            locale=resolved_locale,
            genre=genre,
            original=text,
            revised=revised,
            changes=changes,
            verification=verification,
            before_audit=before_audit,
            after_audit=after_audit,
            blocked=blocked,
        )

    @staticmethod
    def _select_non_overlapping(candidates: list[_Candidate]) -> list[_Candidate]:
        ordered = sorted(
            candidates,
            key=lambda item: (item.start, -(item.end - item.start), item.rule.id),
        )
        selected: list[_Candidate] = []
        occupied: list[tuple[int, int]] = []
        for item in ordered:
            if overlaps(item.start, item.end, occupied):
                continue
            selected.append(item)
            occupied.append((item.start, item.end))
        return sorted(selected, key=lambda item: item.start)
