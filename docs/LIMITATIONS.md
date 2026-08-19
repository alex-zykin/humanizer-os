# Limitations

## Humanization is not authorship detection

HumanizerOS identifies observable patterns. Human writers can use them, and generated text can avoid them. A finding is editing evidence, not proof of authorship.

## Pattern removal is not enough

Replacing clichés can create a cleaner but still generic text. The deterministic core deliberately does not invent experiences, opinions, details, or emotional reactions to compensate.

## Discourse analysis needs length

Uniformity, transitions, and rhythm need enough sentences or paragraphs. Short texts bypass those rules through minimum-length and minimum-sample thresholds.

## StoryScope scope

StoryScope analyzes long English fiction. Its discourse-level findings motivate a separate experimental fiction module, not universal rules for Russian posts, business email, documentation, or short copy.

## Language detection

Automatic resolution uses Cyrillic/Latin ratios and stops on ambiguous or genuinely mixed text. Use `--lang` for transliteration, code-heavy prose, names-only samples, or bilingual documents.

## Fact Guard

Fact Guard protects deterministic surface facts such as numbers, dates, versions, identifiers, URLs, handles, and code. It does not prove semantic equivalence or factual truth. A sentence can preserve every protected token and still change meaning.

Names with ordinary capitalization are not universally protected because doing so would freeze sentence starts and common nouns. Review named entities manually until an optional NLP adapter exists.

## Safe fixes are intentionally narrow

Version 0.1 fixes only a small set of exact fillers and assistant wrappers. A low autofix count is a safety feature.

## Formatting

The Markdown-aware masker protects code, URLs, link targets, quotes, inline code, and fenced blocks. It is not a complete Markdown parser. Nested or malformed markup can require manual review.

## Corpus and metrics

The committed eval fixtures are regression tests, not a representative benchmark. Rule counts, finding counts, and review priority are not quality or probability scores.

## License boundaries

A public repository without a license is not reusable by default. HumanizerOS does not copy the unlicensed `russian-swears` corpus. It is listed only as research navigation until explicit licensing or permission exists.

## No hidden network use

The core runs locally. Future model-provider modules will be optional and must disclose when and where text is sent.
