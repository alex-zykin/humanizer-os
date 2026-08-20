#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from humanizer_os.registry import RuleRegistry  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"release check failed: {message}")


def load_eval_cases(locale: str) -> list[dict[str, object]]:
    path = ROOT / "evals" / locale / "cases.jsonl"
    cases: list[dict[str, object]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSON in {path.relative_to(ROOT)}:{line_number}: {exc}")
        case_id = str(case.get("id", ""))
        if not case_id:
            fail(f"missing eval ID in {path.relative_to(ROOT)}:{line_number}")
        if case_id in seen:
            fail(f"duplicate eval ID {case_id!r} in {path.relative_to(ROOT)}")
        seen.add(case_id)
        if not str(case.get("text", "")).strip():
            fail(f"empty eval text in {case_id}")
        if not (case.get("expect") or case.get("forbid") or case.get("clean")):
            fail(f"eval {case_id} has no assertion")
        if case.get("clean") and case.get("expect"):
            fail(f"eval {case_id} cannot be both clean and positive")
        cases.append(case)
    return cases


def main() -> int:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    package_version = str(project["version"])
    if project.get("dependencies"):
        fail("the runtime package must remain dependency-free in the 0.x core")

    version_text = (ROOT / "src" / "humanizer_os" / "_version.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', version_text)
    if not match or match.group(1) != package_version:
        fail("pyproject and package versions differ")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{package_version}]" not in changelog:
        fail("version is missing from CHANGELOG.md")

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    if not re.search(rf"(?m)^version:\s*[\"']?{re.escape(package_version)}[\"']?\s*$", citation):
        fail("CITATION.cff version differs")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not re.search(rf'(?m)^\s*version:\s*[\"\']?{re.escape(package_version)}[\"\']?\s*$', skill):
        fail("SKILL.md metadata version differs")
    if "name: humanizer-os" not in skill:
        fail("SKILL.md is missing the canonical humanizer-os name")

    registry = RuleRegistry()
    all_rule_ids = {rule.id for rule in registry.list()}
    expected_in_evals: set[str] = set()

    for locale in ("en", "ru"):
        rules = registry.list(locale)
        if len(rules) < 20:
            fail(f"{locale} rule pack is unexpectedly small")
        for rule in rules:
            if not rule.name.strip() or not rule.description.strip() or not rule.message.strip():
                fail(f"rule {rule.id} is missing explanatory prose")
            if not rule.suggestion.strip():
                fail(f"rule {rule.id} is missing a review suggestion")
            if not rule.sources:
                fail(f"rule {rule.id} is missing provenance")

        cases = load_eval_cases(locale)
        if len(cases) < 20:
            fail(f"{locale} eval pack is unexpectedly small")
        for case in cases:
            for field in ("expect", "forbid"):
                for rule_id in case.get(field, []):
                    if rule_id not in all_rule_ids:
                        fail(f"eval {case['id']} references unknown rule {rule_id}")
                    if not str(rule_id).startswith(locale.upper() + "-"):
                        fail(f"eval {case['id']} references the wrong locale rule {rule_id}")
            expected_in_evals.update(str(item) for item in case.get("expect", []))

    for rule in registry.list():
        if rule.autofix and rule.autofix.safe and rule.id not in expected_in_evals:
            fail(f"safe autofix rule {rule.id} has no positive eval case")

    required_files = [
        ".gitattributes",
        ".github/release.yml",
        ".github/workflows/ci.yml",
        ".github/workflows/release.yml",
        "LICENSE",
        "README.md",
        "README.ru.md",
        "SKILL.md",
        "SECURITY.md",
        "SUPPORT.md",
        "THIRD_PARTY_NOTICES.md",
        "assets/verified-rewrite.svg",
        "examples/README.md",
        "examples/product-launch-before.md",
        "examples/product-launch-after.md",
        "docs/CLI.md",
        "docs/EVALUATION.md",
        "docs/JSON_API.md",
        "docs/LIMITATIONS.md",
        "docs/METHODOLOGY.md",
        "docs/PROVENANCE.md",
        "docs/PLATFORM.md",
        "schemas/audit-output.schema.json",
        "schemas/profile-output.schema.json",
        "schemas/rewrite-output.schema.json",
        "schemas/rule.schema.json",
        "schemas/rules-output.schema.json",
        "schemas/verification-output.schema.json",
        "skills/humanizer-os-en/SKILL.md",
        "skills/humanizer-os-ru/SKILL.md",
        "tests/test_readme_demo.py",
    ]
    missing = [item for item in required_files if not (ROOT / item).is_file()]
    if missing:
        fail("required release files are missing: " + ", ".join(missing))

    print(
        f"release check passed for {package_version}: "
        f"{len(registry.list('en'))} EN rules, {len(registry.list('ru'))} RU rules"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
