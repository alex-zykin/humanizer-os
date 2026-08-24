from humanizer_os.text import (
    excerpt,
    find_code_spans,
    find_quote_spans,
    find_url_spans,
    line_col,
    mask_spans,
    paragraphs,
    sentences,
    word_count,
)


def test_span_detection_and_masking() -> None:
    text = "Text `code` and “quote” and https://example.com/x."
    code = find_code_spans(text)
    quotes = find_quote_spans(text)
    urls = find_url_spans(text)
    assert code and quotes and urls
    masked = mask_spans(text, [*code, *quotes, *urls])
    assert "code" not in masked
    assert masked.count("\n") == text.count("\n")


def test_fenced_and_indented_code() -> None:
    text = "```py\nprint(1)\n```\n\n    indented()"
    kinds = {span.kind for span in find_code_spans(text)}
    assert {"code_block", "indented_code"} <= kinds


def test_sentence_paragraph_offsets_and_helpers() -> None:
    text = "First sentence. Second one!\n\nThird paragraph?"
    assert [item.text for item in sentences(text)] == [
        "First sentence.",
        "Second one!",
        "Third paragraph?",
    ]
    assert len(paragraphs(text)) == 2
    assert word_count(text) == 6
    assert line_col(text, text.index("Third")) == (3, 1)
    assert excerpt(text, 0, 5, limit=20).startswith("First")


def test_markdown_blockquotes_are_quote_spans() -> None:
    text = "> Quoted first line.\n> Quoted second line.\n\nOwn paragraph."
    spans = find_quote_spans(text)
    assert any(
        span.kind == "quote" and text[span.start : span.end].startswith(">") for span in spans
    )


def test_blockquote_owns_nested_direct_quotes() -> None:
    text = '> A groundbreaking study said "In conclusion, this changes everything."\n\nOwn text.'
    spans = find_quote_spans(text)
    blockquote = next(span for span in spans if text[span.start : span.end].startswith(">"))
    assert '"In conclusion' in text[blockquote.start : blockquote.end]
    masked = mask_spans(text, spans)
    assert "groundbreaking" not in masked
    assert "In conclusion" not in masked
    assert "Own text" in masked


def test_unclosed_fenced_code_is_protected_through_eof() -> None:
    text = "Before\n\n```python\nprint('in order to')\n"
    spans = find_code_spans(text)
    assert len(spans) == 1
    assert spans[0].start == text.index("```")
    assert spans[0].end == len(text)


def test_longer_tilde_fence_requires_compatible_closer() -> None:
    text = "~~~~\ninside\n~~~\nstill inside\n~~~~\nafter"
    spans = find_code_spans(text)
    assert len(spans) == 1
    assert text[spans[0].start : spans[0].end].endswith("~~~~\n")
