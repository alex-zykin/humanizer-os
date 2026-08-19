from __future__ import annotations

import builtins
import json
import re
from collections.abc import Iterable
from functools import lru_cache
from importlib import resources

from .detectors import DETECTORS
from .fixes import autofix_flags
from .models import Rule

_SUPPORTED_LOCALES = {"ru", "en"}
SUPPORTED_GENRES = (
    "general",
    "social",
    "email",
    "landing",
    "article",
    "docs",
    "fiction",
    "academic",
    "legal",
)
_SUPPORTED_GENRES = set(SUPPORTED_GENRES)
_SUPPORTED_SEVERITIES = {"info", "warning", "error"}
_SUPPORTED_CONFIDENCE = {"low", "medium", "high"}
_RULE_ID_RE = re.compile(r"^(EN|RU)-[A-Z]+-\d{3}$")


class RuleRegistry:
    """Loads and validates the built-in rule packs."""

    def __init__(self, extra_rules: Iterable[Rule] | None = None) -> None:
        loaded_rules = builtins.list(_load_all_builtin_rules())
        if extra_rules:
            loaded_rules.extend(extra_rules)
        self._rules = tuple(loaded_rules)
        self._by_id = {rule.id: rule for rule in self._rules}
        if len(self._by_id) != len(self._rules):
            raise ValueError("Rule IDs must be unique")
        for rule in self._rules:
            self._validate(rule)

    @staticmethod
    def _validate(rule: Rule) -> None:
        if rule.locale not in _SUPPORTED_LOCALES:
            raise ValueError(f"Unsupported locale in {rule.id}: {rule.locale}")
        if not _RULE_ID_RE.fullmatch(rule.id):
            raise ValueError(f"Invalid rule ID: {rule.id}")
        expected_prefix = rule.locale.upper() + "-"
        if not rule.id.startswith(expected_prefix):
            raise ValueError(f"Rule ID and locale differ in {rule.id}: {rule.locale}")
        if rule.severity not in _SUPPORTED_SEVERITIES:
            raise ValueError(f"Unsupported severity in {rule.id}: {rule.severity}")
        if rule.confidence not in _SUPPORTED_CONFIDENCE:
            raise ValueError(f"Unsupported confidence in {rule.id}: {rule.confidence}")
        if rule.detector.type not in DETECTORS:
            raise ValueError(f"Unsupported detector in {rule.id}: {rule.detector.type}")
        if rule.min_chars < 0:
            raise ValueError(f"min_chars must be non-negative in {rule.id}")
        if rule.max_findings < 1:
            raise ValueError(f"max_findings must be positive in {rule.id}")
        if not rule.genres:
            raise ValueError(f"At least one genre is required in {rule.id}")
        if len(set(rule.genres)) != len(rule.genres):
            raise ValueError(f"Duplicate genres in {rule.id}")
        if len(set(rule.excluded_genres)) != len(rule.excluded_genres):
            raise ValueError(f"Duplicate excluded genres in {rule.id}")
        if "*" in rule.genres and len(rule.genres) != 1:
            raise ValueError(f"Wildcard genre must be used alone in {rule.id}")
        invalid_genres = {
            genre for genre in rule.genres if genre != "*" and genre not in _SUPPORTED_GENRES
        }
        invalid_excluded = {
            genre for genre in rule.excluded_genres if genre not in _SUPPORTED_GENRES
        }
        if invalid_genres or invalid_excluded:
            values = ", ".join(sorted(invalid_genres | invalid_excluded))
            raise ValueError(f"Unsupported genre in {rule.id}: {values}")
        overlap = (set(rule.genres) - {"*"}) & set(rule.excluded_genres)
        if overlap:
            values = ", ".join(sorted(overlap))
            raise ValueError(f"Genre both included and excluded in {rule.id}: {values}")

        RuleRegistry._validate_detector_params(rule)

        if rule.detector.type == "regex":
            if not rule.detector.patterns:
                raise ValueError(f"Regex detector has no patterns in {rule.id}")
            flags = re.UNICODE
            if not bool(rule.detector.params.get("case_sensitive", False)):
                flags |= re.IGNORECASE
            if bool(rule.detector.params.get("multiline", True)):
                flags |= re.MULTILINE
            if bool(rule.detector.params.get("dotall", False)):
                flags |= re.DOTALL
            for pattern in rule.detector.patterns:
                try:
                    re.compile(pattern, flags)
                except re.error as exc:
                    raise ValueError(f"Invalid regex in {rule.id}: {pattern!r}") from exc

        if rule.detector.type == "transition_density":
            phrases = [str(item) for item in rule.detector.params.get("phrases", [])]
            if not phrases:
                raise ValueError(f"Transition detector has no phrases in {rule.id}")
            try:
                re.compile(r"^(?:" + "|".join(phrases) + r")\b", re.IGNORECASE)
            except re.error as exc:
                raise ValueError(f"Invalid transition phrase regex in {rule.id}") from exc

        if rule.autofix and rule.autofix.safe:
            if not rule.autofix.replacements:
                raise ValueError(f"Safe autofix has no replacements in {rule.id}")
            flags = autofix_flags(rule)
            for replacement in rule.autofix.replacements:
                try:
                    compiled = re.compile(replacement.pattern, flags)
                    # Parsing the replacement template here catches invalid group
                    # references during registry loading, before a user file is read.
                    compiled.sub(replacement.replacement, "")
                except (re.error, IndexError) as exc:
                    raise ValueError(
                        f"Invalid autofix regex in {rule.id}: {replacement.pattern!r}"
                    ) from exc

    @staticmethod
    def _validate_detector_params(rule: Rule) -> None:
        params = rule.detector.params
        positive_integer_keys = {
            "max_words",
            "min_count",
            "min_items",
            "min_lines",
            "min_paragraphs",
            "min_run",
            "min_sentences",
            "min_words",
            "prefix_words",
        }
        for key in positive_integer_keys & params.keys():
            value = params[key]
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(
                    f"Detector parameter {key} must be a positive integer in {rule.id}"
                )

        for key in {"max_cv", "min_ratio"} & params.keys():
            value = params[key]
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise ValueError(f"Detector parameter {key} must be numeric in {rule.id}")
            if not 0 <= float(value) <= 1:
                raise ValueError(f"Detector parameter {key} must be between 0 and 1 in {rule.id}")

        if "max_per_1000" in params:
            value = params["max_per_1000"]
            if isinstance(value, bool) or not isinstance(value, int | float) or value <= 0:
                raise ValueError(f"Detector parameter max_per_1000 must be positive in {rule.id}")

        if "characters" in params:
            value = params["characters"]
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"Detector parameter characters must be a non-empty string in {rule.id}"
                )

        if rule.detector.type == "short_sentence_stack":
            minimum = int(params.get("min_words", 1))
            maximum = int(params.get("max_words", 4))
            if minimum > maximum:
                raise ValueError(f"min_words exceeds max_words in {rule.id}")

    def list(self, locale: str | None = None, genre: str = "general") -> builtins.list[Rule]:
        self._validate_genre(genre)
        if locale is not None and locale not in _SUPPORTED_LOCALES:
            raise ValueError(f"Unsupported locale: {locale}")
        result: builtins.list[Rule] = []
        for rule in self._rules:
            if locale and rule.locale != locale:
                continue
            if rule.applies_to(genre, 10**12):
                result.append(rule)
        return sorted(result, key=lambda item: item.id)

    def active(self, locale: str, genre: str, text_length: int) -> builtins.list[Rule]:
        self._validate_genre(genre)
        if locale not in _SUPPORTED_LOCALES:
            raise ValueError(f"Unsupported locale: {locale}")
        return [
            rule
            for rule in self._rules
            if rule.locale == locale and rule.applies_to(genre, text_length)
        ]

    @staticmethod
    def _validate_genre(genre: str) -> None:
        if genre not in _SUPPORTED_GENRES:
            choices = ", ".join(SUPPORTED_GENRES)
            raise ValueError(f"Unsupported genre {genre!r}; choose one of: {choices}")

    def get(self, rule_id: str) -> Rule:
        try:
            return self._by_id[rule_id]
        except KeyError as exc:
            raise KeyError(f"Unknown rule: {rule_id}") from exc


@lru_cache(maxsize=1)
def _load_all_builtin_rules() -> tuple[Rule, ...]:
    result: builtins.list[Rule] = []
    package = resources.files("humanizer_os.data.rules")
    for locale in sorted(_SUPPORTED_LOCALES):
        locale_dir = package.joinpath(locale)
        pack_paths = sorted(
            (item for item in locale_dir.iterdir() if item.name.endswith(".json")),
            key=lambda item: item.name,
        )
        if not pack_paths:
            raise ValueError(f"No built-in rule packs found for {locale}")
        for pack_path in pack_paths:
            payload = json.loads(pack_path.read_text(encoding="utf-8"))
            if payload.get("version") != 1:
                raise ValueError(f"Unsupported rule-pack version in {pack_path.name}")
            if payload.get("locale") != locale:
                raise ValueError(f"Locale mismatch in {pack_path.name}")
            items = payload.get("rules", [])
            if not isinstance(items, list) or not items:
                raise ValueError(f"Rule pack is empty in {pack_path.name}")
            for item in items:
                rule = Rule.from_dict(item)
                if rule.locale != locale:
                    raise ValueError(f"Rule {rule.id} is stored in the wrong locale pack")
                result.append(rule)
    return tuple(result)
