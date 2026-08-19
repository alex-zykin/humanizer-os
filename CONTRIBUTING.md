# Contributing

HumanizerOS treats false positives as product defects. A new rule needs more than a phrase that “sounds like AI.”

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
make all
```

## Proposing a rule

Every rule must include:

1. a stable ID and one locale;
2. a narrow description of the observable pattern;
3. severity and confidence that match the evidence;
4. genre exclusions and quote/code behavior;
5. at least one positive eval case;
6. at least one clean or adversarial case;
7. provenance links;
8. a safe autofix only when meaning cannot change.

Do not use a detector verdict as evidence by itself. Do not add rules whose only goal is to evade an authorship classifier.

## Pull requests

Keep behavioral changes and catalog expansion reviewable. Explain:

- what changed;
- why the previous behavior was insufficient;
- new false-positive risks;
- tests and evals added;
- whether facts or file writes are affected.

Run `make all` before opening a pull request. Maintainer release steps are documented in [docs/RELEASING.md](docs/RELEASING.md).
