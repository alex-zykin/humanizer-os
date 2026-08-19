# Command-line interface

HumanizerOS reads UTF-8 text and writes diagnostics to standard output. The runtime does not make network requests.

## Exit codes

| Code | Meaning |
|---:|---|
| `0` | Command completed and its requested gate passed |
| `1` | Findings met `audit --fail-on`, or `fix --check` found an available safe fix |
| `2` | Invalid arguments, missing files, unsupported rule/language, decoding error, or other input/configuration problem |
| `3` | Fact Guard rejected a rewrite, or `verify` found protected-fact differences |

Codes `1` and `3` are deliberate machine-readable outcomes, not crashes.

## `audit`

```bash
humanizer-os audit [PATH ...] [--lang auto|en|ru] [--genre GENRE]
                [--format text|json|sarif]
                [--min-confidence low|medium|high]
                [--rule ID] [--exclude-rule ID]
                [--fail-on never|info|warning|error]
```

With no path, `audit` reads stdin. Directories are traversed recursively for `.md`, `.markdown`, `.mdx`, `.txt`, `.rst`, and `.adoc` files. Build, vendor, virtual-environment, and VCS directories are skipped.

Examples:

```bash
humanizer-os audit README.md --lang en --genre docs
humanizer-os audit posts/ --lang ru --genre social --format sarif > humanizer-os.sarif
humanizer-os audit draft.md --rule EN-LANG-004 --fail-on info
```

An unknown rule ID is an error. A rule forced with `--rule` must belong to the resolved language.

## `fix`

```bash
humanizer-os fix PATH... [--lang auto|en|ru] [--genre GENRE]
              [--write] [--diff] [--check] [--format text|json]
```

`fix` applies only replacements that are explicitly marked safe and whose exact spans were reported by the analyzer. It never invokes a model.

`--write` uses a same-directory temporary file, flushes it to disk, preserves the original file mode and line endings, then replaces the target atomically. Symbolic links are refused. Directories and stdin cannot be used with `--write`.

Without `--write`, `--diff`, `--check`, or JSON output, a single input prints the revised text.

## `verify`

```bash
humanizer-os verify ORIGINAL REVISED [--format text|json]
```

Compares multisets of protected facts. The command exits `3` when facts are lost or introduced.

## `rules` and `explain`

```bash
humanizer-os rules --lang en --genre article
humanizer-os rules --lang ru --format json
humanizer-os explain RU-LANG-004
```

Rule IDs are stable within a major version. `explain` includes rationale, genres, confidence, autofix status, and provenance.

## `profile`

```bash
humanizer-os profile samples/ --lang auto --format json
```

Profiles observable surface characteristics such as sentence length, punctuation, pronoun rates, and list usage. It does not infer identity, personality, demographics, or intent.

## Shell and CI examples

Fail a job only on warnings or errors:

```bash
humanizer-os audit docs/ --lang en --genre docs --fail-on warning
```

Review safe fixes without changing files:

```bash
humanizer-os fix article.md --check
humanizer-os fix article.md --diff
```

Upload SARIF to GitHub Code Scanning with the standard GitHub upload action after producing `humanizer-os.sarif`.
