<div align="center">

<img src="assets/hero.svg" alt="HumanizerOS — humanize the writing, verify the facts" width="100%">

[![CI](https://github.com/alex-zykin/humanizer-os/actions/workflows/ci.yml/badge.svg)](https://github.com/alex-zykin/humanizer-os/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%E2%80%933.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-1F6FEB.svg)](LICENSE)
[![Runtime dependencies](https://img.shields.io/badge/runtime%20dependencies-0-059669.svg)](pyproject.toml)
[![Russian available](https://img.shields.io/badge/locale-Russian%20available-7C3AED.svg)](README.ru.md)

### AI drafts are fast. Generic writing is expensive.

**HumanizerOS helps your agent rewrite AI-assisted English so it sounds natural, while Fact Guard checks that names, numbers, dates, links, citations, and code survive the edit.**

English is the default product experience. Russian is available as an optional language switch.

[Install](#install-in-10-seconds) · [Before & after](#before--after) · [Use with Claude or Codex](#use-it-with-claude-or-codex) · [How it works](#how-it-works) · [Russian support](#russian-when-you-need-it) · [CLI & API](#cli-and-python)

</div>

HumanizerOS is an English-first, local-first text-humanization platform for agents, editors, and CI. It is more than a prompt: it combines an Agent Skill with deterministic analysis, explainable rules, conservative safe fixes, Fact Guard, JSON/SARIF contracts, and a tested runtime.

It does **not** claim to prove whether a human or a model wrote a text. It finds concrete editorial patterns, shows the exact span, and gives the agent evidence to rewrite only what needs work.

## Install in 10 seconds

Install the HumanizerOS Agent Skill globally with the open [`skills`](https://github.com/vercel-labs/skills) CLI:

```bash
npx skills add alex-zykin/humanizer-os --skill humanizer-os -g -y
```

The installer supports Claude Code, Codex, Cursor, OpenCode, and many other agents. To target Claude Code and Codex explicitly:

```bash
npx skills add alex-zykin/humanizer-os --skill humanizer-os -g -a claude-code -a codex -y
```

Install only for Codex:

```bash
npx skills add alex-zykin/humanizer-os --skill humanizer-os -g -a codex -y
```

Install only for Claude Code:

```bash
npx skills add alex-zykin/humanizer-os --skill humanizer-os -g -a claude-code -y
```

Then reload the agent and ask normally:

```text
Humanize this. Keep every name, number, date, URL, citation and code block unchanged.

[paste text]
```

Want the deterministic audit and Fact Guard too? Add the CLI:

```bash
pipx install git+https://github.com/alex-zykin/humanizer-os.git
```

The Skill works without the CLI. The strongest workflow uses both.

## Before → after

**Before**

> In today's fast-paced digital landscape, clear communication is not just helpful, but absolutely essential. It is important to note that concise writing can significantly enhance the reader experience and unlock the full potential of your message.

**After**

> Clear writing helps readers understand the point faster. Concise sentences usually work better than generic introductions, inflated claims, and phrases that announce the point before making it.

HumanizerOS can flag the generic opening, the `not just X but Y` contrast, the meta phrase `it is important to note`, and inflated wording before the agent rewrites the passage.

The important part is not just the rewrite. The same workflow can also verify that protected facts did not drift.

```text
AI-assisted draft
      ↓
HumanizerOS audit
      ↓
Claude / Codex rewrites the prose
      ↓
Fact Guard verifies protected values
      ↓
final text + explainable changes
```

## Why not just use a prompt?

A good prompt can improve prose. HumanizerOS adds a control layer around the prompt.

| Prompt-only humanizer | HumanizerOS |
|---|---|
| The model decides what looks artificial | Deterministic rules produce stable findings with rule IDs and source spans |
| Facts are preserved by instruction | Fact Guard compares protected values before and after editing |
| Behavior depends heavily on the model | Auditing, safe fixes, verification, JSON, and SARIF are model-independent |
| Usually one generic style policy | Genre-aware rules and false-positive boundaries |
| Hard to use in CI | CLI exit codes, SARIF, schemas, tests, and Python API |
| English patterns often get translated to other languages | Russian is a separate optional language pack with its own rules |

## Use it with Claude or Codex

HumanizerOS works best as **Agent Skill + CLI**.

The one-command install above places the canonical root [`SKILL.md`](SKILL.md) into the selected agent. You can also install it only in the current project by leaving off `-g`.

Ask the agent normally:

```text
Humanize this product launch post. Keep the claims and technical details, but remove generic AI phrasing.

[paste text]
```

Or point it at a file:

```text
Humanize the prose in docs/launch-post.md. Keep code blocks and link targets untouched.
```

**Installing the skill does not rewrite every message automatically.** The skill is meant to activate when you ask to humanize, de-template, rewrite, or review prose. Clean text should stay clean.

A full semantic rewrite is performed by the agent. The deterministic CLI alone only applies replacements explicitly marked safe.

If the CLI is unavailable, the Skill can still guide the agent, but you lose the strongest deterministic audit and fact-verification layer.

## How it works

HumanizerOS separates the job into three layers.

### 1. Detect

The engine finds observable patterns such as:

- assistant wrappers and chatbot residue;
- vague attribution;
- inflated importance and sales language;
- `not just X but Y` framing;
- filler and hedging;
- repeated openings and clipped punchlines;
- formatting habits that often make AI-assisted prose feel templated;
- contextual structural signals such as overly uniform rhythm.

Every finding has a stable rule ID, confidence level, exact source span, review advice, genre scope, and provenance.

### 2. Rewrite

The Agent Skill uses those findings as editorial evidence. The model can restructure a paragraph, merge or split sentences, remove formulaic framing, and preserve deliberate voice.

This is intentionally not done by regex. A regex can safely shorten `in order to` to `to`; it should not decide how an entire paragraph should sound.

### 3. Verify

Fact Guard compares protected values between the original and revised text. It currently covers deterministic surface facts such as:

- numbers, percentages, prices, and common units;
- dates and times;
- URLs, email addresses, handles, and hashtags;
- semantic versions, UUIDs, and commit-like hashes;
- uppercase identifiers;
- inline, fenced, and indented code.

Facts are compared as a multiset, so deleting one of two identical values still counts as a change.

Fact Guard does not prove factual truth or full semantic equivalence. It protects values that should not silently drift during editing.

## See the engine work

```bash
$ humanizer-os audit launch.md --lang en --genre landing
launch.md  [en/landing]
44 words · 3 sentences · 4 findings · review priority 100/100
W EN-OPEN-001  1:1  Generic scene-setting opening [medium]
W EN-RHET-001  1:34  Not-just contrast [medium]
W EN-LANG-001  1:74  Inflated importance language [medium]
W EN-RHET-003  3:1  Formulaic conclusion [medium]
```

<img src="assets/terminal-demo.svg" alt="HumanizerOS terminal audit example" width="100%">

Safe replacements are opt-in:

```bash
$ humanizer-os fix draft.md --diff
-In order to publish, test the release.
+To publish, test the release.
```

Fact verification is separate:

```bash
$ humanizer-os verify original.md revised.md
OK  Protected facts match (7 checked).
```

## Russian when you need it

English is the default experience. Russian is a supported locale, not a second marketing surface competing for attention on the main page.

Switch the CLI explicitly:

```bash
humanizer-os audit post.md --lang ru --genre social
humanizer-os fix post.md --lang ru --diff
```

The root Agent Skill switches to Russian when the source is clearly Russian or the user asks for Russian. The Russian pack is not an English prompt translated word-for-word: it has its own rules for bureaucratic nominalization, `является`, translationese, `не просто X, а Y`, impersonal passive phrasing, templated therapeutic tone, and Russian-specific discourse patterns.

Russian documentation: **[README.ru.md](README.ru.md)**  
Russian-only skill: **[`skills/humanizer-os-ru/`](skills/humanizer-os-ru/)**

## CLI and Python

HumanizerOS requires Python 3.11 or newer.

```bash
git clone https://github.com/alex-zykin/humanizer-os.git
cd humanizer-os
python -m pip install -e .
humanizer-os --version
```

For an isolated CLI installation:

```bash
pipx install git+https://github.com/alex-zykin/humanizer-os.git
```

### Core commands

```bash
# Audit English by default in product workflows
humanizer-os audit article.md --lang en --genre article

# Safe deterministic fixes
humanizer-os fix article.md --lang en --diff
humanizer-os fix article.md --lang en --check
humanizer-os fix article.md --lang en --write

# Verify protected facts after any rewrite
humanizer-os verify original.md revised.md

# Machine-readable reports
humanizer-os audit article.md --lang en --format json > audit.json
humanizer-os audit docs/ --lang en --format sarif > humanizer-os.sarif

# Explore the rule catalog
humanizer-os rules --lang en --genre article
humanizer-os explain EN-LANG-004

# Measure observable writing characteristics
humanizer-os profile samples/ --lang en --format json
```

### Python API

```python
from humanizer_os import Analyzer, Rewriter, verify_texts

report = Analyzer().audit(
    "In today's fast-paced world, this is not just a tool, but a game-changer.",
    locale="en",
    genre="landing",
)

for finding in report.findings:
    print(finding.rule_id, finding.line, finding.column, finding.message)

rewrite = Rewriter().fix("In order to ship, test.", locale="en")
assert rewrite.revised == "To ship, test."
assert rewrite.verification.ok

assert verify_texts("Price: $49", "The price is $49").ok
```

## What ships today

- one canonical root `SKILL.md` for the open Agent Skills ecosystem;
- 31 English rules in the default language pack;
- 34 Russian rules in the optional Russian pack;
- checks for artifacts, content, language, rhetoric, formatting, and structure;
- genre profiles for `general`, `social`, `email`, `landing`, `article`, `docs`, `fiction`, `academic`, and `legal`;
- text, versioned JSON, and SARIF 2.1.0 output;
- CLI, Python API, and locale-specific Agent Skills;
- 164 automated tests and 57 bilingual eval cases;
- a local runtime with no runtime dependencies or network requests.

The generated rule catalog is in [docs/RULE_CATALOG.md](docs/RULE_CATALOG.md).

## Repository layout

```text
humanizer-os/
├── SKILL.md                  canonical English-first Agent Skill
├── src/humanizer_os/         dependency-free runtime
│   └── data/rules/
│       ├── en/               default English catalog
│       └── ru/               optional Russian catalog
├── skills/
│   ├── humanizer-os-en/      explicit English-only skill
│   └── humanizer-os-ru/      explicit Russian-only skill
├── schemas/                  public JSON contracts
├── evals/                    regression fixtures
├── tests/                    unit, CLI, schema, and eval tests
├── docs/                     methodology and platform docs
└── .github/workflows/        CI, dependency review, releases
```

Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/METHODOLOGY.md](docs/METHODOLOGY.md), and [docs/PLATFORM.md](docs/PLATFORM.md).

## Quality gates

```bash
python -m pip install -e ".[dev]"
make all
```

The suite checks tests, branch-aware coverage, evals, JSON Schema, documentation links, Ruff, mypy, packaging smoke tests, and a self-audit of public documentation.

## Roadmap

HumanizerOS is designed as a platform rather than one prompt:

- **Core** — analysis, safe fixes, contracts, and Fact Guard;
- **English** — the default product language and primary public experience;
- **Russian** — an optional language-native pack and localized documentation;
- **Voice** — consented author-sample matching;
- **Providers** — explicit local or hosted model adapters;
- **Studio** — visual audit, diff, profiles, policy, and team workflows;
- **Integrations** — editors, CI, and external products;
- **Expressive RU** — opt-in Russian expression support behind the Russian locale.

See [docs/ROADMAP.md](docs/ROADMAP.md).

## Contributing, privacy, and license

Start with [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/RULE_AUTHORING.md](docs/RULE_AUTHORING.md). Do not submit private user text, proprietary corpora, or unlicensed dictionaries.

HumanizerOS executes none of the analyzed text and makes no network requests in the deterministic core. Security reporting is documented in [SECURITY.md](SECURITY.md).

[MIT](LICENSE) © 2026 Alex Zykin.
