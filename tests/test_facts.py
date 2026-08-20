from humanizer_os.facts import extract_facts, verify_facts


def test_extracts_protected_facts() -> None:
    text = "Alex Zykin paid £49.90 on 19 August 2026 at 14:30. See https://example.com/x?id=7."
    facts = extract_facts(text)
    kinds = {item.kind for item in facts}
    assert {"proper_name", "money", "date", "time", "url"} <= kinds


def test_verification_accepts_style_only_change() -> None:
    original = "The launch is on 2026-09-01. Price: $49. Contact team@example.com."
    revised = "We launch on 2026-09-01. The price is $49. Email team@example.com."
    report = verify_facts(original, revised)
    assert report.ok
    assert not report.lost
    assert not report.added


def test_verification_rejects_changed_number() -> None:
    report = verify_facts("The price is $49.", "The price is $59.")
    assert not report.ok
    assert [item.value for item in report.lost] == ["$49"]
    assert [item.value for item in report.added] == ["$59"]


def test_code_is_protected_as_one_fact() -> None:
    original = "Run `deploy --limit 50` now."
    revised = "Now run `deploy --limit 50`."
    report = verify_facts(original, revised)
    assert report.ok


def test_versions_uuids_and_commit_hashes_are_protected() -> None:
    text = "Release v1.4.2 uses commit a1b2c3d4 and job 550e8400-e29b-41d4-a716-446655440000."
    facts = extract_facts(text)
    values = {(item.kind, item.normalized) for item in facts}
    assert ("version", "v1.4.2") in values
    assert ("commit", "a1b2c3d4") in values
    assert ("uuid", "550e8400-e29b-41d4-a716-446655440000") in values


def test_verification_catches_version_change() -> None:
    report = verify_facts("Ship v1.4.2.", "Ship v1.4.3.")
    assert not report.ok
    assert [item.normalized for item in report.lost] == ["v1.4.2"]
    assert [item.normalized for item in report.added] == ["v1.4.3"]


def test_direct_quotes_are_protected_but_quote_style_can_change() -> None:
    original = 'Dr. Lee said "The result was 42."'
    revised = 'Dr. Lee said “The result was 42.”'
    report = verify_facts(original, revised)
    assert report.ok
    assert any(item.kind == "quote" for item in extract_facts(original))


def test_verification_rejects_changed_direct_quote() -> None:
    report = verify_facts('She said "Ship on Monday."', 'She said "Ship on Tuesday."')
    assert not report.ok
    assert [item.kind for item in report.lost] == ["quote"]
    assert [item.kind for item in report.added] == ["quote"]


def test_proper_name_filter_rejects_sentence_scaffolding() -> None:
    values = {
        (item.kind, item.value)
        for item in extract_facts("As Dr. Thompson explained, Mark Thompson agreed.")
    }
    assert ("proper_name", "As Dr") not in values
    assert ("proper_name", "Mark Thompson") in values
