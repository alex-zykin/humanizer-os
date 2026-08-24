![HumanizerOS — humanize the writing, verify the facts](assets/hero.svg)

# HumanizerOS

**Make AI-assisted English sound natural, then verify that names, numbers, dates, links, quotations, and code survived the edit.**

English is the default product experience. Russian is available as an optional language-native pack.

[Install](#install-in-10-seconds) · [Verified demo](#a-rewrite-you-can-verify) · [Real-world sample](#real-world-ai-sample) · [Claude and Codex](#claude-and-codex-setup) · [CLI and API](#cli-and-python-api) · [Russian](README.ru.md)

HumanizerOS combines an Agent Skill with a deterministic editing engine. The model handles semantic rewriting; the engine supplies explainable findings, conservative safe fixes, and Fact Guard verification.

The project does not assign an AI-authorship probability. It reports observable editorial patterns and leaves the final judgment to the writer or editor.

## Install in 10 seconds

Install the canonical Agent Skill with the open [`skills`](https://github.com/vercel-labs/skills) CLI:

```bash
npx skills add alex-zykin/humanizer-os --skill humanizer-os -g -y
```

Codex only:

```bash
npx skills add alex-zykin/humanizer-os --skill humanizer-os -g -a codex -y
```

Claude Code only:

```bash
npx skills add alex-zykin/humanizer-os --skill humanizer-os -g -a claude-code -y
```

After reloading the agent, ask normally:

```text
Humanize this announcement. Keep every name, number, date, URL, quotation, citation, and code block unchanged.

[paste text]
```

The Skill works on its own. Add the Python CLI when you also need deterministic auditing, JSON or SARIF reports, safe local fixes, and Fact Guard:

```bash
pipx install git+https://github.com/alex-zykin/humanizer-os.git
```

## A rewrite you can verify

Most humanizers show only the replacement text. HumanizerOS can also show what it found and whether protected values changed.

![Verified rewrite example](assets/verified-rewrite.svg)

The controlled source lives in [`examples/product-launch-before.md`](examples/product-launch-before.md). Its audit currently returns **10 findings across 8 rules**. The revised version removes the formulaic framing while preserving six protected items.

```bash
humanizer-os audit examples/product-launch-before.md --lang en --genre landing
humanizer-os verify \
  examples/product-launch-before.md \
  examples/product-launch-after.md
```

Expected verification result:

```text
OK  Protected facts match (6 checked).
```

A regression test keeps the README claim synchronized with the engine.

## Real-world AI sample

A second demo uses a released machine-generated record from the **Human Detectors** research dataset by Jenna Russell, Marzena Karpinska, and Mohit Iyyer. The record is labeled `AI-generated`, names `gpt-4o` as the model, and includes human annotations. Full provenance and license notes are in [`examples/real-world-ai-source.md`](examples/real-world-ai-source.md).

The original sample contains language like this:

```text
A groundbreaking study has unveiled that the first warm-blooded dinosaurs may have roamed the Earth approximately 180 million years ago, reshaping our understanding of these ancient creatures.

...

In conclusion, the revelation that some dinosaurs were warm-blooded marks a significant milestone in paleontology.
```

HumanizerOS reports five findings on the complete 348-word source: four instances of inflated significance and one formulaic conclusion. The guided rewrite reduces the passage to 251 words, returns no current deterministic findings, and keeps all five direct quotations unchanged apart from quote typography.

```bash
humanizer-os audit examples/real-world-ai-before.md --lang en --genre article
humanizer-os audit examples/real-world-ai-after.md --lang en --genre article
humanizer-os verify examples/real-world-ai-before.md examples/real-world-ai-after.md
```

Expected Fact Guard result:

```text
OK  Protected facts match (8 checked).
```

Fact Guard checks consistency between source and revision. It does not certify that a generated claim or quotation is true.

## Why HumanizerOS

| Prompt-only workflow | HumanizerOS workflow |
|---|---|
| The model decides what looks artificial | Stable rule IDs point to exact source spans |
| Fact preservation is an instruction | Fact Guard compares protected values |
| Behavior depends entirely on the model | Audit, verification, safe fixes, JSON, and SARIF are model-independent |
| One generic style policy | Genre-aware rules include confidence and false-positive boundaries |
| Difficult to automate in CI | Exit codes, schemas, tests, and a Python API are built in |

The working split is deliberate: **the agent edits meaning; HumanizerOS controls evidence, boundaries, and verification.**

## Claude and Codex setup

The canonical [`SKILL.md`](SKILL.md) is English-first and compatible with the open Agent Skills ecosystem.

Installing the Skill does not rewrite every message automatically. It activates when the user asks to humanize, de-template, rewrite, or review prose. Clean text should remain unchanged.

A strong workflow uses both layers:

```text
AI-assisted draft
      ↓
HumanizerOS audit
      ↓
Claude or Codex rewrites the prose
      ↓
Fact Guard verifies protected values
      ↓
final text and explainable changes
```

## How the engine works

### Detect

The analyzer looks for assistant residue, vague attribution, inflated claims, filler, stock contrasts, repeated openings, formatting habits, and contextual structural signals. Each finding carries a stable rule ID, confidence level, source span, suggestion, genre scope, and provenance.

### Rewrite

The Agent Skill uses those findings as editorial evidence. Semantic changes remain with the model because whole-paragraph rewriting is not a safe regex task.

### Verify

Fact Guard protects direct quotations, numbers, prices, dates, URLs, email addresses, versions, identifiers, detected proper names, and code. Values are compared as a multiset, so removing one of two identical facts still counts as drift.

## CLI and Python API

HumanizerOS requires Python 3.11 or newer.

```bash
git clone https://github.com/alex-zykin/humanizer-os.git
cd humanizer-os
python -m pip install -e .
humanizer-os --version
```

Core commands:

```bash
humanizer-os audit article.md --lang en --genre article
humanizer-os fix article.md --lang en --diff
humanizer-os verify original.md revised.md
humanizer-os audit article.md --lang en --format json > audit.json
humanizer-os audit docs/ --lang en --format sarif > humanizer-os.sarif
humanizer-os rules --lang en --genre article
humanizer-os explain EN-LANG-004
```

Python example:

```python
from humanizer_os import Analyzer, Rewriter, verify_texts

report = Analyzer().audit(
    "In today's fast-paced world, this is not just a tool, but a game-changer.",
    locale="en",
    genre="landing",
)

for finding in report.findings:
    print(finding.rule_id, finding.message)

rewrite = Rewriter().fix("In order to ship, test.", locale="en")
assert rewrite.revised == "To ship, test."
assert verify_texts("Price: $49", "The price is $49").ok
```

## Russian when needed

Russian is an optional locale rather than a translated English prompt. It has its own rules for bureaucratic nominalization, `является`, translationese, impersonal passive phrasing, templated therapeutic tone, and Russian-specific discourse patterns.

```bash
humanizer-os audit post.md --lang ru --genre social
humanizer-os fix post.md --lang ru --diff
```

Read the localized guide in [`README.ru.md`](README.ru.md) or install the explicit Russian skill from [`skills/humanizer-os-ru/`](skills/humanizer-os-ru/).

## What ships today

- one canonical English-first Agent Skill;
- separate English and Russian rule packs;
- genre profiles for social, email, landing, article, docs, fiction, academic, legal, and general prose;
- text, versioned JSON, and SARIF output;
- a dependency-free local runtime;
- regression-tested synthetic and real-world demos;
- automated tests across Python 3.11 through 3.14.

Architecture and methodology are documented in [`docs/`](docs/). The generated catalog is available at [`docs/RULE_CATALOG.md`](docs/RULE_CATALOG.md).

## Contributing, privacy, and license

Start with [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`docs/RULE_AUTHORING.md`](docs/RULE_AUTHORING.md). Do not submit private user text, proprietary corpora, or unlicensed dictionaries.

The deterministic core makes no network requests and executes none of the analyzed text. Security reporting is documented in [`SECURITY.md`](SECURITY.md).

[MIT](LICENSE) © 2026 Alex Zykin.
