from __future__ import annotations

import argparse
import difflib
import os
import stat
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .analyzer import Analyzer
from .models import AuditReport
from .output import (
    profile_json,
    render_audit_text,
    render_profile_text,
    render_rewrite_text,
    render_rule_text,
    render_rules_text,
    render_verification_text,
    reports_json,
    reports_sarif,
    rewrite_json,
    rules_json,
    verification_json,
)
from .profiles import build_voice_profile
from .registry import SUPPORTED_GENRES, RuleRegistry
from .rewriter import Rewriter
from .verify import verify_texts

_TEXT_EXTENSIONS = {".md", ".markdown", ".mdx", ".txt", ".rst", ".adoc"}
_IGNORED_DIRECTORIES = {".git", ".venv", "venv", "node_modules", "dist", "build", "vendor"}
_SEVERITY_RANK = {"info": 0, "warning": 1, "error": 2}
_GENRES = SUPPORTED_GENRES


class CliError(RuntimeError):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="humanizer-os",
        description="Local-first multilingual text humanization platform.",
        epilog=(
            "Examples:\n"
            "  humanizer-os audit README.md --lang en --genre docs\n"
            "  humanizer-os audit posts/ --lang ru --genre social --format sarif\n"
            "  humanizer-os fix draft.md --lang auto --diff\n"
            "  humanizer-os verify original.md revised.md"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="Find formulaic patterns without rewriting text.")
    audit.add_argument(
        "paths",
        nargs="*",
        default=["-"],
        help="Files, directories, or - for stdin.",
    )
    _add_language_and_genre(audit)
    audit.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    audit.add_argument("--min-confidence", choices=("low", "medium", "high"), default="low")
    audit.add_argument(
        "--rule",
        action="append",
        default=[],
        help="Run only this rule ID; repeatable.",
    )
    audit.add_argument(
        "--exclude-rule",
        action="append",
        default=[],
        help="Disable this rule ID; repeatable.",
    )
    audit.add_argument("--fail-on", choices=("never", "info", "warning", "error"), default="never")
    audit.add_argument("--no-suggestions", action="store_true")

    fix = subparsers.add_parser("fix", help="Apply only deterministic fixes marked safe.")
    fix.add_argument("paths", nargs="+", help="Files or - for stdin.")
    _add_language_and_genre(fix)
    fix.add_argument("--write", action="store_true", help="Write changes back to files.")
    fix.add_argument("--diff", action="store_true", help="Print unified diffs.")
    fix.add_argument("--check", action="store_true", help="Exit 1 when a safe fix is available.")
    fix.add_argument("--format", choices=("text", "json"), default="text")

    verify = subparsers.add_parser("verify", help="Verify protected facts after a rewrite.")
    verify.add_argument("original")
    verify.add_argument("revised")
    verify.add_argument("--format", choices=("text", "json"), default="text")

    rules = subparsers.add_parser("rules", help="List the active rule catalog.")
    rules.add_argument("--lang", choices=("ru", "en"), required=True)
    rules.add_argument("--genre", choices=_GENRES, default="general")
    rules.add_argument("--format", choices=("text", "json"), default="text")

    explain = subparsers.add_parser("explain", help="Explain one rule and its provenance.")
    explain.add_argument("rule_id")
    explain.add_argument("--format", choices=("text", "json"), default="text")

    profile = subparsers.add_parser("profile", help="Measure observable voice characteristics.")
    profile.add_argument("paths", nargs="+", help="Writing samples.")
    profile.add_argument("--lang", choices=("auto", "ru", "en"), default="auto")
    profile.add_argument("--format", choices=("text", "json"), default="text")

    return parser


def _add_language_and_genre(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--lang", choices=("auto", "ru", "en"), default="auto")
    parser.add_argument(
        "--genre",
        choices=_GENRES,
        default="general",
    )


def _read_text(path: Path) -> str:
    # newline="" preserves CRLF/LF exactly so a targeted fix does not rewrite
    # every line ending in the file.
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _atomic_write_text(path: Path, text: str) -> None:
    if path.is_symlink():
        raise CliError(f"Refusing to replace a symbolic link: {path}")
    mode = stat.S_IMODE(path.stat().st_mode)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _iter_files(paths: Sequence[str], *, allow_directories: bool) -> list[tuple[str, str]]:
    sources: list[tuple[str, str]] = []
    seen_paths: set[Path] = set()
    stdin_used = False

    def add_file(path: Path) -> None:
        key = path.resolve()
        if key in seen_paths:
            return
        seen_paths.add(key)
        sources.append((str(path), _read_text(path)))

    for raw in paths:
        if raw == "-":
            if stdin_used:
                raise CliError("stdin can only be read once")
            sources.append(("<stdin>", sys.stdin.read()))
            stdin_used = True
            continue
        path = Path(raw)
        if not path.exists():
            raise CliError(f"Path does not exist: {path}")
        if path.is_dir():
            if not allow_directories:
                raise CliError(f"Directories are not supported by this command: {path}")
            for child in sorted(path.rglob("*")):
                if any(part in _IGNORED_DIRECTORIES for part in child.parts):
                    continue
                if child.is_file() and child.suffix.casefold() in _TEXT_EXTENSIONS:
                    add_file(child)
            continue
        add_file(path)
    if not sources:
        raise CliError("No supported text files found")
    return sources


def _should_fail(report: AuditReport, threshold: str) -> bool:
    if threshold == "never":
        return False
    target = _SEVERITY_RANK[threshold]
    return any(_SEVERITY_RANK[item.severity] >= target for item in report.findings)


def command_audit(args: argparse.Namespace) -> int:
    analyzer = Analyzer()
    reports = [
        analyzer.audit(
            text,
            locale=args.lang,
            genre=args.genre,
            source=source,
            min_confidence=args.min_confidence,
            only_rules=args.rule,
            exclude_rules=args.exclude_rule,
        )
        for source, text in _iter_files(args.paths, allow_directories=True)
    ]
    if args.format == "json":
        print(reports_json(reports))
    elif args.format == "sarif":
        print(reports_sarif(reports))
    else:
        print(
            "\n\n".join(
                render_audit_text(item, show_suggestions=not args.no_suggestions)
                for item in reports
            )
        )
    return 1 if any(_should_fail(item, args.fail_on) for item in reports) else 0


def command_fix(args: argparse.Namespace) -> int:
    sources = _iter_files(args.paths, allow_directories=False)
    if len(sources) > 1 and not (args.write or args.diff or args.check or args.format == "json"):
        raise CliError("Use --write, --diff, --check, or --format json when fixing multiple files")
    rewriter = Rewriter()
    reports = [
        rewriter.fix(text, locale=args.lang, genre=args.genre, source=source)
        for source, text in sources
    ]

    if args.write:
        for report in reports:
            if report.source == "<stdin>":
                raise CliError("--write cannot be used with stdin")
            if report.changed and not report.blocked:
                _atomic_write_text(Path(report.source), report.revised)

    if args.format == "json":
        print(rewrite_json(reports))
    elif args.diff:
        for report in reports:
            diff = difflib.unified_diff(
                report.original.splitlines(keepends=True),
                report.revised.splitlines(keepends=True),
                fromfile=report.source,
                tofile=report.source,
            )
            sys.stdout.writelines(diff)
    elif args.write or args.check or len(reports) > 1:
        print("\n\n".join(render_rewrite_text(item) for item in reports))
    else:
        print(reports[0].revised, end="" if reports[0].revised.endswith("\n") else "\n")

    if any(item.blocked for item in reports):
        return 3
    if args.check and any(item.changed for item in reports):
        return 1
    return 0


def command_verify(args: argparse.Namespace) -> int:
    original = _iter_files([args.original], allow_directories=False)[0][1]
    revised = _iter_files([args.revised], allow_directories=False)[0][1]
    report = verify_texts(original, revised)
    print(verification_json(report) if args.format == "json" else render_verification_text(report))
    return 0 if report.ok else 3


def command_rules(args: argparse.Namespace) -> int:
    registry = RuleRegistry()
    rows = registry.list(args.lang, args.genre)
    print(rules_json(rows) if args.format == "json" else render_rules_text(rows))
    return 0


def command_explain(args: argparse.Namespace) -> int:
    registry = RuleRegistry()
    try:
        rule = registry.get(args.rule_id)
    except KeyError as exc:
        raise CliError(str(exc)) from exc
    if args.format == "json":
        print(rules_json([rule]))
    else:
        print(render_rule_text(rule))
    return 0


def command_profile(args: argparse.Namespace) -> int:
    samples = [text for _, text in _iter_files(args.paths, allow_directories=True)]
    profile = build_voice_profile(samples, locale=args.lang)
    print(profile_json(profile) if args.format == "json" else render_profile_text(profile))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    commands = {
        "audit": command_audit,
        "fix": command_fix,
        "verify": command_verify,
        "rules": command_rules,
        "explain": command_explain,
        "profile": command_profile,
    }
    try:
        return commands[args.command](args)
    except (CliError, OSError, ValueError) as exc:
        print(f"humanizer-os: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
