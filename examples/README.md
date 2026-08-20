# Reproducible demos

HumanizerOS keeps public Before → After claims reproducible. The examples in this directory are covered by tests so README numbers cannot drift silently as rules evolve.

## 1. Controlled product-launch demo

[`product-launch-before.md`](product-launch-before.md) intentionally contains common AI-assisted writing patterns plus concrete values that must survive the edit.

Run:

```bash
humanizer-os audit examples/product-launch-before.md --lang en --genre landing
```

The source contains **10 findings across 8 rules**:

- `EN-OPEN-001` — generic scene-setting opening;
- `EN-RHET-001` — `not just X, but Y` contrast;
- `EN-LANG-001` — two inflated-importance matches;
- `EN-LANG-005` — two meta/hedging matches;
- `EN-LANG-006` — marketing adjective stack;
- `EN-LANG-002` — vague attribution;
- `EN-RHET-003` — formulaic conclusion;
- `EN-CONTENT-001` — generic positive ending.

[`product-launch-after.md`](product-launch-after.md) keeps the launch information while removing the formulaic framing.

```bash
humanizer-os verify \
  examples/product-launch-before.md \
  examples/product-launch-after.md
```

Expected result:

```text
OK  Protected facts match (6 checked).
```

## 2. Real-world Human Detectors sample

[`real-world-ai-before.md`](real-world-ai-before.md) is a machine-generated article from the MIT-licensed **Human Detectors** research dataset. The released record is labeled `AI-generated`, lists `gpt-4o` as its generation model, and has `Machine-Generated` majority and expert-majority annotations.

[`real-world-ai-after.md`](real-world-ai-after.md) is the HumanizerOS-guided rewrite. It is original to this repository and preserves the generated sample's claims and five direct quotations while removing inflated framing and a formulaic conclusion.

Full source and attribution details are in [`real-world-ai-source.md`](real-world-ai-source.md).

Run:

```bash
humanizer-os audit examples/real-world-ai-before.md --lang en --genre article
humanizer-os audit examples/real-world-ai-after.md --lang en --genre article
humanizer-os verify examples/real-world-ai-before.md examples/real-world-ai-after.md
```

The current engine reports **5 findings** on the 348-word source and **0 findings** on the 251-word rewrite. Fact Guard verifies **8 protected items**.

Expected verification:

```text
OK  Protected facts match (8 checked).
```

Fact Guard checks consistency, not truth. The real-world source is itself model-generated, so its claims and quotations are not independently certified by this demo.
