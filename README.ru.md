<div align="center">

<img src="assets/hero.svg" alt="HumanizerOS — очеловечивание текста с проверкой фактов" width="100%">

[![CI](https://github.com/alex-zykin/humanizer-os/actions/workflows/ci.yml/badge.svg)](https://github.com/alex-zykin/humanizer-os/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%E2%80%933.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Лицензия: MIT](https://img.shields.io/badge/license-MIT-1F6FEB.svg)](LICENSE)

**[Main English README](README.md)**

### HumanizerOS — English-first продукт. Русский включается как отдельный язык.

**Он помогает агенту переписать AI-assisted текст естественнее и проверяет, что имена, числа, даты, ссылки, цитаты и код не потерялись при редактуре.**

[Установка](#установка-за-10-секунд) · [До и после](#до--после) · [Как работает](#как-это-работает) · [CLI](#cli-и-python)

</div>

Основная публичная витрина HumanizerOS рассчитана на англоязычную аудиторию. Эта страница описывает тот же продукт для русскоязычного пользователя. Русский не является переводом английских правил: для него используется отдельный language pack с собственными конструкциями, исключениями и eval-сценариями.

## Установка за 10 секунд

Canonical Skill находится в корне репозитория и устанавливается через открытый `skills` CLI:

```bash
npx skills add alex-zykin/humanizer-os --skill humanizer-os -g -y
```

Только для Codex:

```bash
npx skills add alex-zykin/humanizer-os --skill humanizer-os -g -a codex -y
```

Только для Claude Code:

```bash
npx skills add alex-zykin/humanizer-os --skill humanizer-os -g -a claude-code -y
```

После перезапуска агента можно написать:

```text
Очеловечь этот текст на русском. Сохрани все имена, числа, даты, ссылки, цитаты и код.

[текст]
```

Root Skill сам переключается на русский, когда исходный текст явно русский или пользователь просит русский. Для жёстко русского режима также есть [`skills/humanizer-os-ru/`](skills/humanizer-os-ru/).

Для детерминированного аудита и Fact Guard дополнительно установите CLI:

```bash
pipx install git+https://github.com/alex-zykin/humanizer-os.git
```

Skill работает и без CLI. Максимальный контроль получается при использовании обоих слоёв.

## До → после

**До**

> В современном мире качественный текст является не просто инструментом, а ключевым фактором эффективной коммуникации. Важно отметить, что ясная формулировка позволяет раскрыть потенциал сообщения и значительно улучшить взаимодействие с читателем.

**После**

> Ясный текст помогает читателю быстрее понять мысль. Универсальные вступления, канцелярские связки и фразы вроде «важно отметить» часто можно убрать без потери смысла.

Русский пакет отдельно замечает `в современном мире`, `является`, конструкцию `не просто X, а Y`, вводные фразы, канцелярит и маркетинговые усиления.

## Как это работает

HumanizerOS разделяет задачу на три слоя:

```text
черновик
   ↓
HumanizerOS audit --lang ru
   ↓
Claude / Codex смыслово переписывает текст
   ↓
Fact Guard проверяет защищённые значения
   ↓
готовый текст + объяснимые изменения
```

### 1. Найти

Русские правила обнаруживают, например:

- канцелярские отглагольные существительные;
- `является` и тяжёлые связки;
- переводные вводные конструкции;
- `не просто X, а Y`;
- размытые модальные обещания;
- безличный пассив;
- шаблонный терапевтический регистр;
- служебные артефакты ассистента;
- контекстные структурные сигналы.

### 2. Переписать

Полное смысловое переписывание делает агент. HumanizerOS Skill задаёт редакторские ограничения: сохранить смысл, не выдумывать опыт и факты, учитывать жанр и не менять хороший текст только ради отличия.

### 3. Проверить

Fact Guard сравнивает защищённые значения до и после. Он умеет контролировать числа, проценты, цены, единицы, даты, время, URL, email, версии, UUID, commit-like хеши, идентификаторы и код.

Fact Guard не доказывает истинность текста и полную смысловую эквивалентность. Его задача — не дать конкретным значениям тихо измениться во время редактуры.

## Важно: Skill не переписывает всё автоматически

После установки HumanizerOS не должен вмешиваться в каждое сообщение. Он предназначен для запросов вроде:

```text
очеловечь текст
перепиши естественнее
убери шаблонность
сделай менее нейросетевым
проведи редакторский аудит
```

Чистый текст не нужно переписывать только ради того, чтобы он стал другим. Код, цитаты, юридические и технические фрагменты получают более осторожные правила.

## CLI и Python

Нужен Python 3.11 или новее.

```bash
git clone https://github.com/alex-zykin/humanizer-os.git
cd humanizer-os
python -m pip install -e .
humanizer-os --version
```

### Основные команды

```bash
# Русский аудит
humanizer-os audit post.md --lang ru --genre social

# Безопасные детерминированные правки
humanizer-os fix post.md --lang ru --diff
humanizer-os fix post.md --lang ru --write

# Проверка фактов после любой смысловой правки
humanizer-os verify original.md revised.md

# Каталог русских правил
humanizer-os rules --lang ru --genre social
humanizer-os explain RU-LANG-002

# JSON / SARIF
humanizer-os audit post.md --lang ru --format json > audit.json
humanizer-os audit docs/ --lang ru --format sarif > humanizer-os.sarif
```

### Python API

```python
from humanizer_os import Analyzer, Rewriter, verify_texts

report = Analyzer().audit(
    "В современном мире это не просто инструмент, а революционное решение.",
    locale="ru",
    genre="landing",
)

for finding in report.findings:
    print(finding.rule_id, finding.line, finding.column, finding.message)

rewrite = Rewriter().fix(
    "На сегодняшний день мы работаем для того чтобы запустить тест.",
    locale="ru",
)
assert rewrite.revised == "Сейчас мы работаем чтобы запустить тест."
assert rewrite.verification.ok

assert verify_texts("Цена: 4900 ₽", "Стоимость — 4900 ₽").ok
```

## Что входит в 0.1

- 31 английское правило в основном English pack;
- 34 русских правила в optional Russian pack;
- жанры `general`, `social`, `email`, `landing`, `article`, `docs`, `fiction`, `academic`, `legal`;
- Fact Guard;
- text, JSON и SARIF 2.1.0;
- CLI и Python API;
- root `SKILL.md` для Agent Skills ecosystem;
- отдельные `humanizer-os-en` и `humanizer-os-ru` skills;
- 164 автоматических теста и 57 двуязычных eval-сценариев.

## Архитектура

```text
humanizer-os/
├── SKILL.md                  основной English-first Skill
├── src/humanizer_os/
│   └── data/rules/
│       ├── en/               основной английский pack
│       └── ru/               optional Russian pack
├── skills/
│   ├── humanizer-os-en/
│   └── humanizer-os-ru/
├── schemas/
├── evals/
├── tests/
├── docs/
└── .github/workflows/
```

Подробнее: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/METHODOLOGY.md](docs/METHODOLOGY.md), [docs/PLATFORM.md](docs/PLATFORM.md).

## Развитие платформы

- **Core** — аудит, safe fixes, контракты и Fact Guard;
- **English** — основной язык продукта;
- **Russian** — дополнительный language-native pack;
- **Voice** — работа с добровольно предоставленными образцами автора;
- **Providers** — адаптеры локальных и облачных моделей;
- **Studio** — визуальный аудит, diff, профили и политики;
- **Expressive RU** — опциональная русская экспрессия внутри Russian locale.

План: [docs/ROADMAP.md](docs/ROADMAP.md).

## Участие, приватность и лицензия

Начните с [CONTRIBUTING.md](CONTRIBUTING.md) и [docs/RULE_AUTHORING.md](docs/RULE_AUTHORING.md). Не отправляйте приватные пользовательские тексты, закрытые корпуса и словари без лицензии.

Детерминированное ядро HumanizerOS не исполняет анализируемый текст и не делает сетевых запросов. Уязвимости сообщаются по инструкции в [SECURITY.md](SECURITY.md).

[MIT](LICENSE) © 2026 Alex Zykin.
