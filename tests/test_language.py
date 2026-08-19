from humanizer_os.language import detect_language, resolve_locale


def test_detects_russian() -> None:
    guess = detect_language("Сегодня мы проверяем русский текст без лишнего шума.")
    assert guess.code == "ru"
    assert guess.confidence > 0.9


def test_detects_english() -> None:
    guess = detect_language("Today we are checking a plain English paragraph.")
    assert guess.code == "en"
    assert guess.confidence > 0.9


def test_detects_mixed_text() -> None:
    guess = detect_language("Проверяем API response и русский интерфейс together.")
    assert guess.code == "mixed"


def test_short_text_is_unknown() -> None:
    assert detect_language("OK").code == "unknown"


def test_explicit_locale_wins() -> None:
    locale, guess = resolve_locale("Русский текст", "en")
    assert locale == "en"
    assert guess.code == "ru"


def test_url_letters_do_not_overwhelm_short_russian_text() -> None:
    guess = detect_language("Готово: https://very-long-example-domain.test/english/path")
    assert guess.code == "ru"


def test_invalid_requested_language_is_rejected() -> None:
    import pytest

    with pytest.raises(ValueError, match="Unsupported language"):
        resolve_locale("Text", "de")
