# Releasing HumanizerOS

## Before tagging

```bash
make all
```

The gate runs tests, coverage, evals, documentation validation, release consistency, catalog freshness, Ruff, mypy, self-audit, package build, and wheel smoke tests.

Update:

- `pyproject.toml`;
- `src/humanizer_os/_version.py`;
- `CHANGELOG.md`;
- `CITATION.cff`;
- README version-specific examples when necessary.

Then run:

```bash
python scripts/check_release.py
```

## Tag

Use an annotated tag:

```bash
git tag -a v0.1.0 -m "HumanizerOS 0.1.0"
git push origin v0.1.0
```

The release workflow validates the tag against the package version, reruns the complete gate, builds the wheel and source distribution, smoke-tests both paths, creates SHA-256 sums, uploads an Actions artifact, and publishes a GitHub Release.

Do not move a published version tag. Issue a patch release instead.

## PyPI

PyPI publication is intentionally not automated in 0.1. Add trusted publishing only after the package owner, release environment, and recovery process have been documented.
