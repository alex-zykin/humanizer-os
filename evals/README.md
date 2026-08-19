# Eval fixtures

The fixtures are original, minimal examples used for regression testing. They are released under the repository's MIT license.

Each JSONL case can contain:

- `id`: stable case name;
- `genre`: built-in genre profile;
- `text`: input text;
- `expect`: rule IDs that must appear;
- `forbid`: rule IDs that must not appear;
- `clean`: require zero findings.

Run:

```bash
python scripts/evaluate.py
```

Do not add confidential or copyrighted user text. Reduce reports to the smallest self-contained example.
