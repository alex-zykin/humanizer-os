# Release process

HumanizerOS releases are built from reviewed commits on `main`.

## Before tagging

1. Update `src/humanizer_os/_version.py`, `pyproject.toml`, `CHANGELOG.md`, and `CITATION.cff`.
2. Run the complete local gate:

```bash
python -m pip install -e ".[dev]"
make all
```

3. Confirm that the generated rule catalog is current and that the bilingual eval suite passes.
4. Review `git diff` for generated artifacts, secrets, private text, and unrelated changes.

## Publish

Create and push an annotated tag:

```bash
git tag -a vX.Y.Z -m "HumanizerOS X.Y.Z"
git push origin vX.Y.Z
```

The release workflow verifies that the tag matches the package version, runs the release gates, builds wheel and source-distribution artifacts, installs the wheel in a clean environment, and publishes a GitHub Release with SHA-256 checksums.

PyPI publishing remains disabled until trusted publishing is configured for the repository and documented in the security model.

## Recovery

A failed workflow must not be worked around by uploading an unchecked artifact. Fix the source, rerun the same gates, and publish a new patch tag when a public tag already points at a faulty commit.
