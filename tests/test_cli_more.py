from __future__ import annotations

import io
import json
import sys
from pathlib import Path

from humanizer_os.cli import main


def test_audit_text_clean_and_directory(tmp_path: Path, capsys) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "clean.md").write_text("The release starts on 19 August 2026.", encoding="utf-8")
    (docs / "skip.py").write_text("print('ignore')", encoding="utf-8")
    code = main(["audit", str(docs), "--lang", "en", "--genre", "docs"])
    out = capsys.readouterr().out
    assert code == 0
    assert "No enabled patterns found" in out
    assert "skip.py" not in out


def test_audit_missing_path_returns_usage_error(capsys) -> None:
    code = main(["audit", "/definitely/missing/file.md"])
    captured = capsys.readouterr()
    assert code == 2
    assert "does not exist" in captured.err


def test_audit_stdin_and_no_suggestions(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("In order to ship, test."))
    code = main(["audit", "-", "--lang", "en", "--no-suggestions"])
    out = capsys.readouterr().out
    assert code == 0
    assert "EN-LANG-004" in out
    assert "→" not in out


def test_fix_diff(tmp_path: Path, capsys) -> None:
    path = tmp_path / "draft.md"
    path.write_text("At this point in time we test.", encoding="utf-8")
    code = main(["fix", str(path), "--lang", "en", "--diff"])
    out = capsys.readouterr().out
    assert code == 0
    assert "-At this point in time" in out
    assert "+Now we test." in out


def test_fix_json_multiple_files(tmp_path: Path, capsys) -> None:
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    first.write_text("In order to ship, test.", encoding="utf-8")
    second.write_text("At this point in time we wait.", encoding="utf-8")
    code = main(["fix", str(first), str(second), "--lang", "en", "--format", "json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert len(payload["reports"]) == 2
    assert all(item["changes"] for item in payload["reports"])


def test_fix_multiple_without_output_mode_is_error(tmp_path: Path, capsys) -> None:
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    first.write_text("Plain text.", encoding="utf-8")
    second.write_text("Plain text.", encoding="utf-8")
    code = main(["fix", str(first), str(second)])
    assert code == 2
    assert "multiple files" in capsys.readouterr().err


def test_fix_write_rejects_stdin(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("In order to ship, test."))
    code = main(["fix", "-", "--write", "--lang", "en"])
    assert code == 2
    assert "cannot be used with stdin" in capsys.readouterr().err


def test_rules_and_explain_formats(capsys) -> None:
    assert main(["rules", "--lang", "ru"]) == 0
    assert "RU-ART-001" in capsys.readouterr().out

    assert main(["rules", "--lang", "en", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["rules"][0]["locale"] == "en"

    assert main(["explain", "EN-LANG-004"]) == 0
    assert "Safe autofix: yes" in capsys.readouterr().out

    assert main(["explain", "EN-LANG-004", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["rules"][0]["id"] == "EN-LANG-004"


def test_explain_unknown_rule(capsys) -> None:
    assert main(["explain", "EN-UNKNOWN-999"]) == 2
    assert "Unknown rule" in capsys.readouterr().err


def test_profile_text_and_json(tmp_path: Path, capsys) -> None:
    path = tmp_path / "sample.md"
    path.write_text("I tested it. You can test it too.\n\nWe shipped it.", encoding="utf-8")
    assert main(["profile", str(path), "--lang", "en"]) == 0
    assert "Voice profile" in capsys.readouterr().out

    assert main(["profile", str(path), "--lang", "en", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["locale"] == "en"


def test_verify_json_success(tmp_path: Path, capsys) -> None:
    original = tmp_path / "a.txt"
    revised = tmp_path / "b.txt"
    original.write_text("Launch: 2026-09-01.", encoding="utf-8")
    revised.write_text("We launch on 2026-09-01.", encoding="utf-8")
    assert main(["verify", str(original), str(revised), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["ok"] is True


def test_fix_write_preserves_crlf_and_file_mode(tmp_path: Path, capsys) -> None:
    path = tmp_path / "draft.md"
    path.write_bytes(b"In order to ship, test.\r\nSecond line.\r\n")
    path.chmod(0o640)
    code = main(["fix", str(path), "--lang", "en", "--write"])
    assert code == 0
    assert path.read_bytes() == b"To ship, test.\r\nSecond line.\r\n"
    assert path.stat().st_mode & 0o777 == 0o640
    capsys.readouterr()


def test_directory_audit_deduplicates_overlapping_inputs(tmp_path: Path, capsys) -> None:
    path = tmp_path / "draft.markdown"
    path.write_text("In order to ship, test.", encoding="utf-8")
    code = main(["audit", str(tmp_path), str(path), "--lang", "en", "--format", "json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload["reports"]) == 1


def test_fix_write_refuses_symbolic_link(tmp_path: Path, capsys) -> None:
    target = tmp_path / "target.md"
    target.write_text("In order to ship, test.", encoding="utf-8")
    link = tmp_path / "link.md"
    link.symlink_to(target)
    code = main(["fix", str(link), "--lang", "en", "--write"])
    assert code == 2
    assert "symbolic link" in capsys.readouterr().err
    assert target.read_text(encoding="utf-8") == "In order to ship, test."


def test_rules_reject_unknown_genre(capsys) -> None:
    try:
        main(["rules", "--lang", "en", "--genre", "unknown"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("argparse should reject an unknown genre")
    assert "invalid choice" in capsys.readouterr().err
