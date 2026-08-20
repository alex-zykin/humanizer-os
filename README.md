<div align="center">

<img src="assets/hero.svg" alt="HumanizerOS — the open platform for humanizing text" width="100%">

[![CI](https://github.com/alex-zykin/humanizer-os/actions/workflows/ci.yml/badge.svg)](https://github.com/alex-zykin/humanizer-os/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%E2%80%933.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-1F6FEB.svg)](LICENSE)
[![Languages](https://img.shields.io/badge/languages-English%20%7C%20Russian-0EA5E9.svg)](#language-native-by-design)
[![Runtime dependencies](https://img.shields.io/badge/runtime%20dependencies-0-059669.svg)](pyproject.toml)

**[Русская версия](README.ru.md)**

### AI drafts are fast. The problem is they often sound the same.

**HumanizerOS finds formulaic writing, helps your agent rewrite only what needs work, and checks that the facts survive.**

English and Russian are first-class languages. Names, numbers, dates, prices, links, citations, and code stay protected.

[Before & after](#before--after) · [Use with Claude or Codex](#use-it-with-an-agent) · [How it works](#how-it-works) · [CLI](#cli-and-python) · [Roadmap](#roadmap)

</div>

HumanizerOS is a local-first, explainable text-humanization platform for agents, editors, and CI. It is more than a prompt: the project combines language-native rule packs, deterministic diagnostics, conservative safe fixes, Fact Guard, JSON/SARIF contracts, and Agent Skills.

It does **not** claim to prove whether a human or a model wrote a text. It reports concrete editorial patterns, shows the exact span, and explains what deserves review.

## Before → after

### English

**Before**

> In today's fast-paced digital landscape, clear communication is not just helpful, but absolutely essential. It is important to note that concise writing can significantly enhance the reader experience and unlock the full potential of your message.

**After**

> Clear writing helps readers understand the point faster. Concise sentences usually work better than generic introductions, inflated claims, and phrases that announce the point before making it.

HumanizerOS can flag the generic opening, the `not just X but Y` contrast, the meta phrase `it is important to note`, and inflated wording before the agent rewrites the passage.

### Russian

**До**

> В современном мире качественный текст является не просто инструментом, а ключевым фактором эффективной коммуникации. Важно отметить, что ясная формулировка позволяет раскрыть потенциал сообщения и значительно улучшить взаимодействие с читателем.

**После**

> Ясный текст помогает читателю быстрее понять мысль. Универсальные вступления, канцелярские связки и фразы вроде «важно отметить» часто можно убрать без потери смысла.

The Russian pack detects its own constructions rather than translating English rules word-for-word.

## Use it with an agent

HumanizerOS works best as **Agent Skill + CLI**.

Install the `skills/humanizer-os/` folder in a skills-compatible agent such as Claude Code or Codex, then install the CLI in the same environment when you want deterministic auditing and Fact Guard.

```bash
git clone https://github.com/alex-zykin/humanizer-os.git
cd humanizer-os
python -m pip install -e .
```

Then ask the agent normally:

```text
Humanize this in Russian. Keep all numbers, links, names and code unchanged.

[paste text]
```

Or point it at a file:

```text
Humanize the prose in docs/launch-post.md. Keep code blocks and link targets untouched.
```

The preferred agent workflow is:

```text
your draft
   ↓
HumanizerOS audit (RU or EN + genre)
   ↓
agent rewrites the prose semantically
   ↓
Fact Guard verifies protected values
   ↓
final text + explainable changes
```

**Installing the skill does not rewrite every message automatically.** The skill is used when you ask to humanize, de-template, rewrite, or review prose. A full semantic rewrite is performed by the agent. The deterministic CLI alone only applies fixes that are explicitly marked safe.

If the CLI is not installed, the skill can still guide the agent, but you lose the strongest deterministic audit and fact-verification layer.

## How it works

HumanizerOS separates the job into three layers:

1. **Detect.** Language-native rules find assistant artifacts, stock language, weak rhetoric, formatting habits, and contextual structural signals.
2. **Rewrite.** A skills-compatible agent uses those findings to rewrite the prose without treating the original paragraph structure as sacred.
3. **Verify.** Fact Guard compares protected values before and after the rewrite and rejects deterministic changes that drift.

That separation is deliberate. A regex can safely shorten `in order to` to `to`, but it should not decide how an entire paragraph should sound. The agent handles semantic editing; the engine handles evidence, boundaries, and verification.

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

$ humanizer-os verify original.md revised.md
OK  Protected facts match (7 checked).
```

## Why HumanizerOS is different

| Principle | In practice |
|---|---|
| **Language-native** | English and Russian use separate catalogs, examples, thresholds, genre limits, and evals. |
| **Fact-safe** | Names, numbers, dates, prices, units, URLs, versions, identifiers, and code are compared before and after a rewrite. |
| **Explainable** | Every finding has a stable rule ID, confidence, exact source span, suggestion, genre scope, and provenance. |
| **Conservative** | Only replacements explicitly marked safe are applied automatically. Everything else remains a review finding. |
| **Local-first** | The core has no runtime dependencies and performs no network requests. |
| **Agent-ready** | The skill gives the model a rewrite workflow while the engine supplies deterministic checks before and after it. |
| **Platform-shaped** | CLI, Python API, JSON, SARIF, schemas, language packs, Agent Skills, and future Studio modules share contracts. |

## Included in 0.1

- 65 built-in rules: 31 English and 34 Russian;
- artifact, content, language, rhetoric, formatting, and structure checks;
- profiles for `general`, `social`, `email`, `landing`, `article`, `docs`, `fiction`, `academic`, and `legal`;
- Fact Guard for protected values and code;
- text, versioned JSON, and SARIF 2.1.0 output;
- `audit`, `fix`, `verify`, `rules`, `explain`, and `profile` commands;
- Python API and three Agent Skills;
- 164 automated tests and 57 bilingual eval cases.

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

### Quick start

```bash
# Audit a file or directory
humanizer-os audit article.md --lang auto --genre article
humanizer-os audit docs/ --lang en --genre docs --fail-on warning

# Machine-readable reports
humanizer-os audit article.md --format json > audit.json
humanizer-os audit docs/ --format sarif > humanizer-os.sarif

# Safe deterministic fixes
humanizer-os fix article.md --diff
humanizer-os fix article.md --check
humanizer-os fix article.md --write

# Fact verification
humanizer-os verify original.md revised.md

# Explore rules
humanizer-os rules --lang ru --genre social
humanizer-os explain RU-LANG-002

# Measure observable writing characteristics
humanizer-os profile samples/ --lang auto --format json
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

## Language-native by design

The English pack focuses on vague attribution, inflated importance, generic openings, `not just X but Y`, filler connectives, assistant wrappers, title-case headings, and mechanically even rhythm.

The Russian pack separately checks bureaucratic nominalization, `является`, translationese, `не просто X, а Y`, vague modal claims, impersonal passive phrasing, templated therapeutic tone, assistant artifacts, and discourse uniformity.

The generated catalog is available in [docs/RULE_CATALOG.md](docs/RULE_CATALOG.md). Use `humanizer-os explain RULE_ID` for a rule's full rationale and provenance.

## Fact Guard

Fact Guard protects deterministic surface facts including numbers, percentages, prices, common units, dates, times, URLs, email addresses, handles, hashtags, semantic versions, UUIDs, commit-like hashes, uppercase identifiers, and code.

Facts are compared as a multiset, so removing one of two identical values still counts as a change. Fact Guard does not establish truth or full semantic equivalence; see [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Repository layout

```text
humanizer-os/
├── src/humanizer_os/          dependency-free runtime
│   └── data/rules/{en,ru}/    language-native catalogs
├── schemas/                   public JSON contracts
├── skills/                    Agent Skills
├── evals/{en,ru}/             bilingual regression fixtures
├── tests/                     unit, CLI, schema, and eval tests
├── docs/                      methodology and platform docs
└── .github/workflows/         CI, dependency review, releases
```

Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/METHODOLOGY.md](docs/METHODOLOGY.md), and [docs/PLATFORM.md](docs/PLATFORM.md).

## Quality gates

```bash
python -m pip install -e ".[dev]"
make all
```

The suite includes tests, branch-aware coverage, bilingual evals, schema validation, documentation link checks, Ruff, mypy, packaging smoke tests, and a self-audit of public documentation.

## Roadmap

HumanizerOS is designed as a system rather than one prompt:

- **Core** — analysis, safe fixes, contracts, and Fact Guard;
- **RU / EN** — independent language packs;
- **Voice** — consented author-sample matching;
- **Expressive RU** — opt-in preservation, normalization, masking, and later controlled Russian expression;
- **Providers** — explicit local or hosted model adapters;
- **Studio** — visual audit, diff, profiles, policy, and team workflows;
- **Integrations** — editors, CI, Creator Content OS, and external packs.

See [docs/ROADMAP.md](docs/ROADMAP.md).

## Contributing, privacy, and license

Start with [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/RULE_AUTHORING.md](docs/RULE_AUTHORING.md). Do not submit private user text, proprietary corpora, or unlicensed dictionaries.

HumanizerOS 0.1 executes none of the analyzed text and makes no network requests. Security reporting is documented in [SECURITY.md](SECURITY.md).

[MIT](LICENSE) © 2026 Alex Zykin.