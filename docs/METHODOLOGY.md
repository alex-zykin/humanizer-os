# Methodology

HumanizerOS is an editing system, not an authorship detector. It reports observable problems in context, assigns conservative confidence, applies only fact-safe deterministic fixes, and leaves ambiguous revisions to the author.

## Evidence model

### Artifact

High-confidence contamination that does not belong in published prose: assistant wrappers, internal citation IDs, unresolved placeholders, and copied service parameters. Artifact rules can usually run across genres. Some exact wrappers are safe to delete.

### Content

Unsupported or functionally empty claims: vague authorities, universal optimism, manufactured “deeper truths,” and objections nobody raised. These need author review; automatic rewriting could remove a real claim.

### Language

Local phrasing problems: bureaucratic nominalization, translationese, stacked hedges, inflated copulas, and redundant connectives. Only exact meaning-preserving substitutions receive safe fixes.

### Rhetoric

Reusable frames that often substitute presentation for substance: generic openings, announced transitions, formulaic conclusions, false ranges, fake candor, and canned question-answer beats. Genre boundaries matter.

### Formatting

Presentation patterns such as decorative emoji bullets, dense bold emphasis, list-heavy passages, title case, and high em-dash density. These are low or medium confidence because formatting can be intentional.

### Structure

Signals measured across several units: uniform sentence length, uniform paragraph size, repeated sentence openings, stacks of fragments, and transition-heavy paragraph starts. Structural rules require minimum text lengths and conservative thresholds.

## Rule confidence

- `high`: deterministic artifact or direct language error with narrow exceptions;
- `medium`: strong editorial signal with known genre boundaries;
- `low`: contextual structural or style signal.

Confidence describes the rule's evidence, not the probability that a model produced the text.

## Language packs

English and Russian share contracts but not catalogs. Each pack has its own examples, regexes, thresholds, genre exclusions, eval cases, and provenance.

Shared concepts may have different implementations. English Title Case and Russian bureaucratic nominalization are not translations of one another.

## Genre profiles

Built-in genres are:

```text
general social email landing article docs fiction academic legal
```

A genre can disable a rule or change which rules are active. For example, a sign-off can be legitimate in email, passive voice is common in formal prose, and narrative rhythm does not belong in a two-sentence support reply.

## Protected spans

Before analysis, HumanizerOS identifies spans that must not be treated as ordinary prose:

- fenced and inline code;
- indented code;
- URLs and email addresses;
- Markdown link targets;
- quotations;
- structured factual tokens.

The analyzer masks protected characters with spaces while preserving string length and newlines. Finding offsets therefore map back to the source.

## Fact Guard

Fact Guard extracts deterministic facts before and after a rewrite:

- numbers, percentages, prices, and units;
- common English and Russian date forms;
- times;
- URLs, emails, handles, and hashtags;
- semantic versions;
- UUIDs and commit-like hashes;
- all-caps identifiers;
- inline, fenced, and indented code.

Facts are compared as a multiset. Removing one of two repeated dates is a change.

Fact Guard does not confirm truth and cannot prove semantic equivalence. It blocks the narrow failure modes it can detect reliably.

## Safe-fix process

A deterministic fix is eligible only when:

1. the analyzer reported its exact span;
2. the rule marks the replacement safe;
3. the span does not overlap code, a quote, URL, email, or protected fact;
4. the replacement does not overlap a higher-priority change;
5. Fact Guard accepts the revised document;
6. a second pass produces no new deterministic change.

HumanizerOS restores the original text if verification fails.

## Structural thresholds

Discourse rules operate only above rule-specific minimum lengths and sample counts. Their output is a review prompt, not a deletion instruction.

Uniformity detectors use coefficient of variation. Transition density counts selected discourse markers at paragraph starts. Repeated-opening rules compare normalized prefixes after removing punctuation and stop words.

## Voice profile

Version 0.1 profiles observable surface features:

- sentence and paragraph length;
- punctuation density;
- first- and second-person pronoun rates;
- contraction or particle rates;
- list-line ratio.

It does not infer identity, personality, intent, gender, age, ethnicity, or mental state. Future author matching must require explicit samples and consent.

## Review priority

The bounded `review_priority` metric helps sort files. It uses weighted finding severity and confidence, with a cap at 100. It is not a quality score or authorship probability.

## Evaluation

Every built-in rule needs a positive eval case. New or changed rules also need a clean, adversarial, quote, or genre-boundary case. Releases test:

- exact expected and forbidden rule IDs;
- clean texts;
- fact loss and fact injection;
- idempotence;
- CLI exit codes;
- SARIF validity.

Run the complete gate:

```bash
make all
```

Rule count alone is not a quality metric. New rules require a positive case, a clean or adversarial case, provenance, and a documented false-positive boundary.
