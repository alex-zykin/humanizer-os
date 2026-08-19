from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from ._version import __version__

Severity = Literal["info", "warning", "error"]
Confidence = Literal["low", "medium", "high"]
LanguageCode = Literal["ru", "en", "mixed", "unknown"]


@dataclass(frozen=True, slots=True)
class Replacement:
    pattern: str
    replacement: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Replacement":
        return cls(pattern=str(data["pattern"]), replacement=str(data.get("replacement", "")))


@dataclass(frozen=True, slots=True)
class Autofix:
    safe: bool = False
    replacements: tuple[Replacement, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Autofix | None":
        if not data:
            return None
        replacements = tuple(Replacement.from_dict(item) for item in data.get("replacements", []))
        return cls(safe=bool(data.get("safe", False)), replacements=replacements)


@dataclass(frozen=True, slots=True)
class DetectorSpec:
    type: str
    patterns: tuple[str, ...] = ()
    params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DetectorSpec":
        return cls(
            type=str(data["type"]),
            patterns=tuple(str(item) for item in data.get("patterns", [])),
            params=dict(data.get("params", {})),
        )


@dataclass(frozen=True, slots=True)
class Rule:
    id: str
    locale: str
    name: str
    description: str
    category: str
    severity: Severity
    confidence: Confidence
    message: str
    suggestion: str
    detector: DetectorSpec
    genres: tuple[str, ...] = ("*",)
    excluded_genres: tuple[str, ...] = ()
    min_chars: int = 0
    max_findings: int = 20
    ignore_in_quotes: bool = True
    ignore_in_code: bool = True
    ignore_in_urls: bool = True
    enabled: bool = True
    autofix: Autofix | None = None
    sources: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rule":
        return cls(
            id=str(data["id"]),
            locale=str(data["locale"]),
            name=str(data["name"]),
            description=str(data.get("description", "")),
            category=str(data["category"]),
            severity=data.get("severity", "warning"),
            confidence=data.get("confidence", "medium"),
            message=str(data.get("message", data["name"])),
            suggestion=str(data.get("suggestion", "")),
            detector=DetectorSpec.from_dict(data["detector"]),
            genres=tuple(data.get("genres", ["*"])),
            excluded_genres=tuple(data.get("excluded_genres", [])),
            min_chars=int(data.get("min_chars", 0)),
            max_findings=int(data.get("max_findings", 20)),
            ignore_in_quotes=bool(data.get("ignore_in_quotes", True)),
            ignore_in_code=bool(data.get("ignore_in_code", True)),
            ignore_in_urls=bool(data.get("ignore_in_urls", True)),
            enabled=bool(data.get("enabled", True)),
            autofix=Autofix.from_dict(data.get("autofix")),
            sources=tuple(data.get("sources", [])),
        )

    def applies_to(self, genre: str, text_length: int) -> bool:
        if not self.enabled or text_length < self.min_chars:
            return False
        if genre in self.excluded_genres:
            return False
        return "*" in self.genres or genre in self.genres


@dataclass(frozen=True, slots=True)
class LanguageGuess:
    code: LanguageCode
    confidence: float
    cyrillic_letters: int
    latin_letters: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Finding:
    rule_id: str
    rule_name: str
    category: str
    severity: Severity
    confidence: Confidence
    message: str
    suggestion: str
    start: int
    end: int
    line: int
    column: int
    excerpt: str
    fixable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AuditReport:
    source: str
    locale: str
    detected_language: LanguageGuess
    genre: str
    findings: list[Finding]
    metrics: dict[str, Any]
    tool_version: str = __version__

    @property
    def has_findings(self) -> bool:
        return bool(self.findings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "locale": self.locale,
            "detected_language": self.detected_language.to_dict(),
            "genre": self.genre,
            "findings": [item.to_dict() for item in self.findings],
            "metrics": self.metrics,
            "tool_version": self.tool_version,
        }


@dataclass(frozen=True, slots=True)
class Fact:
    kind: str
    value: str
    normalized: str
    start: int
    end: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class VerificationReport:
    ok: bool
    lost: list[Fact]
    added: list[Fact]
    original_count: int
    revised_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "lost": [item.to_dict() for item in self.lost],
            "added": [item.to_dict() for item in self.added],
            "original_count": self.original_count,
            "revised_count": self.revised_count,
        }


@dataclass(frozen=True, slots=True)
class Change:
    rule_id: str
    start: int
    end: int
    before: str
    after: str
    line: int
    column: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RewriteReport:
    source: str
    locale: str
    genre: str
    original: str
    revised: str
    changes: list[Change]
    verification: VerificationReport
    before_audit: AuditReport
    after_audit: AuditReport
    blocked: bool = False

    @property
    def changed(self) -> bool:
        return self.original != self.revised

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "locale": self.locale,
            "genre": self.genre,
            "original": self.original,
            "revised": self.revised,
            "changes": [item.to_dict() for item in self.changes],
            "verification": self.verification.to_dict(),
            "before_audit": self.before_audit.to_dict(),
            "after_audit": self.after_audit.to_dict(),
            "blocked": self.blocked,
        }
