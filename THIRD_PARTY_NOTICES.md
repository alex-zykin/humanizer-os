# Third-party notices and research provenance

HumanizerOS is an original implementation. No source repository was merged or vendored into this codebase. Public projects and research informed the taxonomy, product constraints, and evaluation strategy.

## StoryScope

- Paper: *StoryScope: Investigating idiosyncrasies in AI fiction* by Jenna Russell, Rishanth Rajendhran, Chau Minh Pham, Mohit Iyyer, and John Wieting.
- Paper: https://arxiv.org/abs/2604.03136
- Code: https://github.com/jenna-russell/storyscope
- Code license at time of review: MIT.

StoryScope motivates a separate discourse-level layer and the warning that narrative findings from long fiction should not be treated as universal rules for short business text.

## Human Detectors

- Paper: *People who frequently use ChatGPT for writing tasks are accurate and robust detectors of AI-generated text* by Jenna Russell, Marzena Karpinska, and Mohit Iyyer.
- Paper: https://arxiv.org/abs/2501.15654
- Code and dataset: https://github.com/jenna-russell/human_detectors
- Repository license at time of review: MIT.

The real-world demo in `examples/real-world-ai-*` uses one machine-generated record from the released dataset. The record is labeled `AI-generated`, lists `gpt-4o` as the generation model, and is paired with metadata for a human reference article. HumanizerOS does not reproduce the paired human-written article.

The demo's revised version is original HumanizerOS documentation. It preserves the generated sample's claims and direct quotations for editorial comparison. Fact Guard verifies consistency between the two demo files; it does not certify the truth of the generated source material.

## Public humanizer projects reviewed

- https://github.com/gc-tilda/pishi-chelovechno — MIT at time of review.
- https://github.com/smixs/humanizer-ru — MIT at time of review.
- https://github.com/blader/humanizer — MIT at time of review.
- https://github.com/ilyautov/humanizer-ru — MIT at time of review.
- https://github.com/Vladimir-Human/humanizer-ru — MIT at time of review.

They informed questions such as rule grouping, audit modes, false-positive handling, deterministic checks, and author-voice preservation. HumanizerOS's rule wording, examples, schemas, detectors, CLI, tests, and documentation were written independently except where a third-party sample is explicitly attributed, as above.

## Wikipedia references

- https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- https://ru.wikipedia.org/wiki/Википедия:Признаки_сгенерированности_текста

These pages are referenced as living catalogs. HumanizerOS does not reproduce their article text. Contributors who copy or adapt Wikipedia content must follow the applicable CC BY-SA terms and record attribution.

## Dependency notices

The runtime package has no third-party Python dependencies. Development and CI tools retain their own licenses and are not redistributed in the wheel.
