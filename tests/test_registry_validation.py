from __future__ import annotations

from dataclasses import replace

import pytest

from humanizer_os.models import Autofix, DetectorSpec, Replacement
from humanizer_os.registry import RuleRegistry


def base_rule():
    return replace(RuleRegistry().get("EN-LANG-004"), id="EN-TEST-999")


def test_duplicate_rule_id_rejected() -> None:
    duplicate = RuleRegistry().get("EN-LANG-004")
    with pytest.raises(ValueError, match="unique"):
        RuleRegistry([duplicate])


@pytest.mark.parametrize(
    ("rule", "message"),
    [
        (replace(base_rule(), locale="de"), "Unsupported locale"),
        (replace(base_rule(), severity="fatal"), "Unsupported severity"),
        (replace(base_rule(), confidence="certain"), "Unsupported confidence"),
        (replace(base_rule(), detector=DetectorSpec("unknown")), "Unsupported detector"),
        (replace(base_rule(), detector=DetectorSpec("regex", patterns=("[",))), "Invalid regex"),
        (
            replace(
                base_rule(),
                autofix=Autofix(True, (Replacement("[", "x"),)),
            ),
            "Invalid autofix regex",
        ),
    ],
)
def test_invalid_rule_rejected(rule, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        RuleRegistry([rule])


def test_rule_with_unknown_genre_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported genre"):
        RuleRegistry([replace(base_rule(), genres=("unknown",))])


@pytest.mark.parametrize(
    "genres,excluded,message",
    [
        (("docs", "docs"), (), "Duplicate genres"),
        (("*", "docs"), (), "Wildcard genre"),
        (("docs",), ("docs",), "both included and excluded"),
        (("docs",), ("*",), "Unsupported genre"),
    ],
)
def test_rule_genre_configuration_is_validated(
    genres: tuple[str, ...],
    excluded: tuple[str, ...],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        RuleRegistry([replace(base_rule(), genres=genres, excluded_genres=excluded)])


@pytest.mark.parametrize(
    "detector,message",
    [
        (DetectorSpec("repeated_starts", params={"min_count": 0}), "positive integer"),
        (DetectorSpec("uniform_sentences", params={"max_cv": 1.5}), "between 0 and 1"),
        (DetectorSpec("dash_density", params={"max_per_1000": 0}), "must be positive"),
        (DetectorSpec("dash_density", params={"characters": ""}), "non-empty string"),
        (
            DetectorSpec(
                "short_sentence_stack",
                params={"min_words": 5, "max_words": 2},
            ),
            "min_words exceeds max_words",
        ),
    ],
)
def test_detector_parameters_are_validated(detector: DetectorSpec, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        RuleRegistry([replace(base_rule(), detector=detector)])
