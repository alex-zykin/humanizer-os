# Third-party notices and research provenance

HumanizerOS is an original implementation. No source repository was merged or vendored into this codebase. Public projects and research informed the taxonomy, product constraints, and evaluation strategy.

## StoryScope

- Paper: *StoryScope: Investigating idiosyncrasies in AI fiction* by Jenna Russell, Rishanth Rajendhran, Chau Minh Pham, Mohit Iyyer, and John Wieting.
- Paper: https://arxiv.org/abs/2604.03136
- Code: https://github.com/jenna-russell/storyscope
- Code license at time of review: MIT.

StoryScope motivates a separate discourse-level layer and the warning that narrative findings from long fiction should not be treated as universal rules for short business text.

## Public humanizer projects reviewed

- https://github.com/gc-tilda/pishi-chelovechno — MIT at time of review.
- https://github.com/smixs/humanizer-ru — MIT at time of review.
- https://github.com/blader/humanizer — MIT at time of review.
- https://github.com/ilyautov/humanizer-ru — MIT at time of review.
- https://github.com/Vladimir-Human/humanizer-ru — MIT at time of review.

They informed questions such as rule grouping, audit modes, false-positive handling, deterministic checks, and author-voice preservation. HumanizerOS's rule wording, examples, schemas, detectors, CLI, tests, and documentation were written independently.

## Wikipedia references

- https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- https://ru.wikipedia.org/wiki/Википедия:Признаки_сгенерированности_текста

These pages are referenced as living catalogs. HumanizerOS does not reproduce their article text. Contributors who copy or adapt Wikipedia content must follow the applicable CC BY-SA terms and record attribution.

## Dependency notices

The runtime package has no third-party Python dependencies. Development and CI tools retain their own licenses and are not redistributed in the wheel.
