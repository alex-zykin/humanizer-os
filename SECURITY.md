# Security policy

## Supported versions

Security fixes are applied to the latest release line.

## Reporting a vulnerability

Please do not open a public issue for a vulnerability that could expose user text, execute untrusted code, or alter protected facts silently. Use GitHub's private vulnerability reporting for this repository.

Include:

- affected version and command;
- a minimal reproducer that contains no confidential text;
- expected and observed behavior;
- whether the issue can change facts, read arbitrary files, or write outside the requested path.

## Security boundaries

The core analyzer is local and dependency-free. It does not make network requests. The `fix` command only applies replacements marked `safe` in the rule catalog and runs Fact Guard afterward. If verification fails, the rewrite is discarded. In-place writes refuse symbolic links and use same-directory atomic replacement while preserving file mode and line endings.

Future provider adapters must remain optional, disclose data flow, and never activate without an explicit user choice.
