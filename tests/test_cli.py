import json
from pathlib import Path

from humanizer_os.cli import main


def test_audit_json_and_fail_on(tmp_path: Path, capsys) -> None:
    path = tmp_path / "draft.md"
    path.write_text("In order to ship, test.", encoding="utf-8")
    code = main(["audit", str(path), "--lang", "en", "--format", "json", "--fail-on", "info"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    assert payload["reports"][0]["findings"][0]["rule_id"] == "EN-LANG-004"


def test_audit_sarif(tmp_path: Path, capsys) -> None:
    path = tmp_path / "draft.md"
    path.write_text("In conclusion, the future looks bright.", encoding="utf-8")
    code = main(["audit", str(path), "--lang", "en", "--format", "sarif"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["version"] == "2.1.0"
    assert payload["runs"][0]["results"]


def test_fix_check_and_write(tmp_path: Path, capsys) -> None:
    path = tmp_path / "draft.md"
    path.write_text("In order to ship, test.", encoding="utf-8")
    assert main(["fix", str(path), "--lang", "en", "--check"]) == 1
    capsys.readouterr()
    assert main(["fix", str(path), "--lang", "en", "--write"]) == 0
    capsys.readouterr()
    assert path.read_text(encoding="utf-8") == "To ship, test."


def test_verify_exit_code(tmp_path: Path, capsys) -> None:
    original = tmp_path / "original.txt"
    revised = tmp_path / "revised.txt"
    original.write_text("Price: $49.", encoding="utf-8")
    revised.write_text("Price: $59.", encoding="utf-8")
    assert main(["verify", str(original), str(revised)]) == 3
    assert "FAILED" in capsys.readouterr().out
