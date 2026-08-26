from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN_ROOT = ROOT / "plugins" / "humanizer-os"
PLUGIN_MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"


def test_codex_marketplace_points_to_packaged_plugin() -> None:
    payload = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    assert payload["name"] == "humanizer-os-marketplace"
    assert payload["interface"]["displayName"] == "HumanizerOS"
    assert len(payload["plugins"]) == 1

    plugin = payload["plugins"][0]
    assert plugin["name"] == "humanizer-os"
    assert plugin["source"] == {
        "source": "local",
        "path": "./plugins/humanizer-os",
    }
    assert plugin["policy"]["installation"] == "AVAILABLE"
    assert plugin["policy"]["authentication"] == "ON_INSTALL"
    assert PLUGIN_ROOT.is_dir()


def test_codex_plugin_manifest_matches_release() -> None:
    plugin = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]

    assert plugin["name"] == "humanizer-os"
    assert plugin["version"] == project["version"]
    assert plugin["license"] == "MIT"
    assert plugin["skills"].rstrip("/") == "./skills"

    interface = plugin["interface"]
    for field in (
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
    ):
        assert isinstance(interface[field], str) and interface[field].strip()
    assert interface["capabilities"]
    assert 1 <= len(interface["defaultPrompt"]) <= 3


def test_codex_plugin_skills_stay_in_sync_with_canonical_skills() -> None:
    pairs = (
        (ROOT / "SKILL.md", PLUGIN_ROOT / "skills" / "humanizer-os" / "SKILL.md"),
        (
            ROOT / "skills" / "humanizer-os-en" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "humanizer-os-en" / "SKILL.md",
        ),
        (
            ROOT / "skills" / "humanizer-os-ru" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "humanizer-os-ru" / "SKILL.md",
        ),
    )
    for canonical, packaged in pairs:
        assert packaged.read_text(encoding="utf-8") == canonical.read_text(encoding="utf-8")
