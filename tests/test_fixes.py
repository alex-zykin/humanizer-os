from humanizer_os.fixes import preserve_case


def test_preserve_case_handles_initial_capital() -> None:
    assert preserve_case("In order to", "to") == "To"


def test_preserve_case_handles_all_caps() -> None:
    assert preserve_case("IN ORDER TO", "to") == "TO"


def test_preserve_case_keeps_lowercase() -> None:
    assert preserve_case("in order to", "to") == "to"
