import json
from pathlib import Path

from jsonschema import Draft202012Validator

from humanizer_os import Analyzer, Rewriter
from humanizer_os.output import (
    profile_json,
    reports_json,
    rewrite_json,
    rules_json,
    verification_json,
)
from humanizer_os.profiles import build_voice_profile
from humanizer_os.registry import RuleRegistry
from humanizer_os.verify import verify_texts

ROOT = Path(__file__).resolve().parents[1]


def load_schema(name: str) -> dict[str, object]:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def validate(name: str, instance: object) -> None:
    schema = load_schema(name)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)


def test_builtin_rule_packs_match_schema() -> None:
    schema = load_schema("rule.schema.json")
    validator = Draft202012Validator(schema)
    rules_root = ROOT / "src" / "humanizer_os" / "data" / "rules"
    for locale in ("en", "ru"):
        packs = sorted((rules_root / locale).glob("*.json"))
        assert packs
        for pack in packs:
            payload = json.loads(pack.read_text(encoding="utf-8"))
            validator.validate(payload)


def test_audit_json_matches_published_schema() -> None:
    report = Analyzer().audit("In order to ship, test.", locale="en")
    validate("audit-output.schema.json", json.loads(reports_json([report])))


def test_verification_json_matches_published_schema() -> None:
    report = verify_texts("Ship v1.2.0.", "Ship v1.3.0.")
    validate("verification-output.schema.json", json.loads(verification_json(report)))


def test_profile_json_matches_published_schema() -> None:
    profile = build_voice_profile(["I tested it. You reviewed it."], locale="en")
    validate("profile-output.schema.json", json.loads(profile_json(profile)))


def test_rewrite_json_matches_published_schema() -> None:
    report = Rewriter().fix("In order to ship, test.", locale="en")
    validate("rewrite-output.schema.json", json.loads(rewrite_json([report])))


def test_rules_json_matches_published_schema() -> None:
    validate(
        "rules-output.schema.json",
        json.loads(rules_json(RuleRegistry().list("en", "general"))),
    )
