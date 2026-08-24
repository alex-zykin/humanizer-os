# Releasing HumanizerOS

## Before tagging

```bash
make all
```

The gate runs tests, coverage, evals, documentation validation, release consistency, catalog freshness, Ruff, mypy, self-audit, package build, and wheel smoke tests.

Update:

- `pyproject.toml`;
- `src/humanizer_os/_version.py`;
- `SKILL.md` and locale-specific Skill metadata;
- `CHANGELOG.md`;
- `CITATION.cff`;
- README version-specific examples when necessary.

Then run:

```bash
python scripts/check_release.py
```

## Tag

Use an annotated tag. For example:

```bash
VERSION=0.1.1
git tag -a "v${VERSION}" -m "HumanizerOS ${VERSION}"
git push origin "v${VERSION}"
```

The release workflow validates the tag against the package version, reruns the complete gate, builds the wheel and source distribution, smoke-tests both paths, creates SHA-256 sums, uploads an Actions artifact, and publishes a GitHub Release.

Do not move a published version tag. Issue a patch release instead.

## PyPI

PyPI publication is intentionally not automated in 0.1. Add trusted publishing only after the package owner, release environment, and recovery process have been documented.
