from __future__ import annotations

import re
import statistics
from collections.abc import Iterable
from dataclasses import asdict, dataclass

from .language import resolve_locale
from .text import (
    find_code_spans,
    find_url_spans,
    mask_spans,
    paragraphs,
    sentences,
    word_count,
    words,
)


@dataclass(frozen=True, slots=True)
class VoiceProfile:
    locale: str
    characters: int
    words: int
    sentences: int
    paragraphs: int
    avg_sentence_words: float
    sentence_word_stdev: float
    avg_paragraph_words: float
    type_token_ratio: float
    first_person_per_1000: float
    second_person_per_1000: float
    question_marks_per_1000: float
    exclamation_marks_per_1000: float
    em_dashes_per_1000: float
    semicolons_per_1000: float
    emoji_lines_ratio: float
    bullet_lines_ratio: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_voice_profile(samples: Iterable[str], locale: str = "auto") -> VoiceProfile:
    text = "\n\n".join(sample for sample in samples if sample.strip())
    resolved_locale, _ = resolve_locale(text, locale)
    prose = mask_spans(text, [*find_code_spans(text), *find_url_spans(text)])
    token_list = [item.casefold() for item in words(prose)]
    word_total = len(token_list)
    sentence_items = sentences(prose)
    paragraph_items = paragraphs(prose)
    sentence_counts = [word_count(item.text) for item in sentence_items]
    paragraph_counts = [word_count(item.text) for item in paragraph_items]
    lines = [line for line in text.splitlines() if line.strip()]

    if resolved_locale == "ru":
        first = {
            "я",
            "мы",
            "меня",
            "мне",
            "мной",
            "мною",
            "мой",
            "моя",
            "мои",
            "моё",
            "наш",
            "наша",
            "наше",
            "наши",
            "нами",
        }
        second = {
            "ты",
            "вы",
            "тебя",
            "тебе",
            "тобой",
            "вам",
            "вами",
            "вас",
            "твой",
            "твоя",
            "твоё",
            "твои",
            "ваш",
            "ваша",
            "ваше",
            "ваши",
        }
    else:
        first = {
            "i",
            "i'm",
            "i'd",
            "i've",
            "we",
            "we're",
            "we'd",
            "we've",
            "me",
            "my",
            "mine",
            "our",
            "ours",
            "us",
        }
        second = {"you", "you're", "you'd", "you've", "your", "yours"}

    scale = 1000 / max(word_total, 1)
    first_count = sum(1 for token in token_list if token in first)
    second_count = sum(1 for token in token_list if token in second)
    emoji_lines = sum(
        1 for line in lines if re.match(r"\s*[\U0001F300-\U0001FAFF\u2600-\u27BF]", line)
    )
    bullet_lines = sum(1 for line in lines if re.match(r"\s*(?:[-*+] |\d+[.)]\s+)", line))

    return VoiceProfile(
        locale=resolved_locale,
        characters=len(text),
        words=word_total,
        sentences=len(sentence_items),
        paragraphs=len(paragraph_items),
        avg_sentence_words=round(statistics.fmean(sentence_counts), 2) if sentence_counts else 0.0,
        sentence_word_stdev=(
            round(statistics.pstdev(sentence_counts), 2) if len(sentence_counts) > 1 else 0.0
        ),
        avg_paragraph_words=(
            round(statistics.fmean(paragraph_counts), 2) if paragraph_counts else 0.0
        ),
        type_token_ratio=round(len(set(token_list)) / max(word_total, 1), 4),
        first_person_per_1000=round(first_count * scale, 2),
        second_person_per_1000=round(second_count * scale, 2),
        question_marks_per_1000=round(text.count("?") * 1000 / max(len(text), 1), 2),
        exclamation_marks_per_1000=round(text.count("!") * 1000 / max(len(text), 1), 2),
        em_dashes_per_1000=round(text.count("—") * 1000 / max(len(text), 1), 2),
        semicolons_per_1000=round(text.count(";") * 1000 / max(len(text), 1), 2),
        emoji_lines_ratio=round(emoji_lines / max(len(lines), 1), 4),
        bullet_lines_ratio=round(bullet_lines / max(len(lines), 1), 4),
    )
