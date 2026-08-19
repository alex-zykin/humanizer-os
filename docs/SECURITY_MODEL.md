# Security model

## Assets to protect

- the user's original text;
- facts and code embedded in that text;
- the boundaries of files the user requested;
- rule catalog integrity;
- future provider credentials.

## Current trust boundaries

The 0.1 core:

- runs locally;
- makes no network requests;
- has no runtime dependency installation hooks;
- reads only requested paths and recursively discovered prose files;
- writes only with `fix --write` and only to explicitly named regular files;
- refuses symbolic links for in-place writes;
- preserves line endings and mode bits and replaces files atomically;
- never executes analyzed code;
- restores the original in memory when Fact Guard fails.

## Untrusted input

Text, Markdown, paths, regex matches, and rule-pack data are untrusted.

Mitigations:

- no `eval` or shell execution;
- package-bundled rule files are validated;
- user text is never interpolated into a regex;
- directory scans ignore common dependency and build trees;
- SARIF and JSON are serialized through the standard library;
- output excerpts are plain text, not rendered HTML.

## Known gaps before 1.0

- custom external rule packs are not yet supported or signed;
- catastrophic-backtracking analysis is manual;
- large-file resource limits are not configurable;
- future LLM adapters need explicit redaction and retention controls.

## Provider adapter requirements

Any future network adapter must:

- remain an optional extra;
- require an explicit provider choice;
- state exactly what text leaves the machine;
- support environment-based credentials;
- never log full text by default;
- run Fact Guard on returned text;
- expose timeouts and retries;
- document provider retention assumptions;
- be disabled in offline mode.
