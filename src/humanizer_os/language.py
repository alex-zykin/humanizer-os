from __future__ import annotations

import re

from .models import LanguageCode, LanguageGuess
from .text import find_code_spans, find_url_spans, mask_spans

CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
LATIN_RE = re.compile(r"[A-Za-z]")
_SUPPORTED_REQUESTS = {"auto", "ru", "en"}


def detect_language(text: str) -> LanguageGuess:
    # URLs and code can overwhelm a short prose sample with Latin characters.
    scan = mask_spans(text, [*find_code_spans(text), *find_url_spans(text)])
    cyrillic = len(CYRILLIC_RE.findall(scan))
    latin = len(LATIN_RE.findall(scan))
    total = cyrillic + latin
    if total < 4:
        return LanguageGuess("unknown", 0.0, cyrillic, latin)
    cyrillic_ratio = cyrillic / total
    code: LanguageCode
    if cyrillic_ratio >= 0.67:
        code = "ru"
        confidence = cyrillic_ratio
    elif cyrillic_ratio <= 0.33:
        code = "en"
        confidence = 1.0 - cyrillic_ratio
    else:
        code = "mixed"
        confidence = 1.0 - abs(0.5 - cyrillic_ratio) * 2
    return LanguageGuess(code, round(confidence, 4), cyrillic, latin)


def resolve_locale(text: str, requested: str = "auto") -> tuple[str, LanguageGuess]:
    if requested not in _SUPPORTED_REQUESTS:
        choices = ", ".join(sorted(_SUPPORTED_REQUESTS))
        raise ValueError(f"Unsupported language {requested!r}; choose one of: {choices}")

    guess = detect_language(text)
    if requested in {"ru", "en"}:
        return requested, guess
    if guess.code == "ru":
        return "ru", guess
    if guess.code == "en":
        return "en", guess
    if guess.code == "mixed":
        return ("ru" if guess.cyrillic_letters >= guess.latin_letters else "en"), guess
    return "en", guess
