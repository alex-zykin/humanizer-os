<div align="center">

<img src="assets/hero.svg" alt="HumanizerOS — открытая платформа для очеловечивания текста" width="100%">

[![CI](https://github.com/alex-zykin/humanizer-os/actions/workflows/ci.yml/badge.svg)](https://github.com/alex-zykin/humanizer-os/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%E2%80%933.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Лицензия: MIT](https://img.shields.io/badge/license-MIT-1F6FEB.svg)](LICENSE)
[![Языки](https://img.shields.io/badge/languages-English%20%7C%20Russian-0EA5E9.svg)](#отдельные-языковые-пакеты)
[![Зависимости ядра](https://img.shields.io/badge/runtime%20dependencies-0-059669.svg)](pyproject.toml)

**[English version](README.md)**

### ИИ пишет быстро. Проблема в том, что он слишком часто пишет одинаково.

**HumanizerOS находит шаблонность, помогает агенту переписать только нужные места и проверяет, что факты не потерялись.**

Русский и английский — полноценные отдельные языки. Имена, числа, даты, цены, ссылки, цитаты и код остаются защищёнными.

[До и после](#до--после) · [Claude и Codex](#как-использовать-с-агентом) · [Как это работает](#как-это-работает) · [CLI](#cli-и-python) · [План развития](#развитие-платформы)

</div>

HumanizerOS — локальная и объяснимая платформа для очеловечивания текста в агентах, редакторах и CI. Это не один большой промпт: проект объединяет отдельные языковые пакеты, детерминированный аудит, осторожные безопасные исправления, Fact Guard, JSON/SARIF-контракты и Agent Skills.

Проект **не доказывает**, написал текст человек или модель. Он находит конкретные редакторские паттерны, показывает точный фрагмент и объясняет, что стоит проверить.

## До → после

### Русский

**До**

> В современном мире качественный текст является не просто инструментом, а ключевым фактором эффективной коммуникации. Важно отметить, что ясная формулировка позволяет раскрыть потенциал сообщения и значительно улучшить взаимодействие с читателем.

**После**

> Ясный текст помогает читателю быстрее понять мысль. Универсальные вступления, канцелярские связки и фразы вроде «важно отметить» часто можно убрать без потери смысла.

HumanizerOS отдельно замечает «в современном мире», `является`, конструкцию «не просто X, а Y», вводную фразу «важно отметить» и маркетинговое усиление.

### English

**Before**

> In today's fast-paced digital landscape, clear communication is not just helpful, but absolutely essential. It is important to note that concise writing can significantly enhance the reader experience and unlock the full potential of your message.

**After**

> Clear writing helps readers understand the point faster. Concise sentences usually work better than generic introductions, inflated claims, and phrases that announce the point before making it.

Английский пакет использует свои правила, а не перевод русского каталога.

## Как использовать с агентом

Лучший режим HumanizerOS — **Agent Skill + CLI**.

Установите папку `skills/humanizer-os/` в Claude Code, Codex или другой агент с поддержкой skills. CLI желательно установить в то же окружение: тогда агент сможет выполнять детерминированный аудит и Fact Guard до и после смысловой правки.

```bash
git clone https://github.com/alex-zykin/humanizer-os.git
cd humanizer-os
python -m pip install -e .
```

После этого можно писать агенту обычным языком:

```text
Очеловечь этот текст на русском. Сохрани все числа, ссылки, имена и код.

[текст]
```

Или указать файл:

```text
Очеловечь текст в docs/launch-post.md. Не меняй кодовые блоки и адреса ссылок.
```

Предпочтительный процесс выглядит так:

```text
черновик
   ↓
HumanizerOS audit (RU или EN + жанр)
   ↓
агент смыслово переписывает текст
   ↓
Fact Guard проверяет защищённые значения
   ↓
готовый текст + объяснимые изменения
```

**Установка скилла не означает, что агент будет переписывать вообще каждый ваш текст.** Он должен использовать HumanizerOS, когда вы просите очеловечить, переписать, убрать шаблонность или провести редакторский аудит.

Полное смысловое переписывание делает сам агент. Детерминированный CLI без агента применяет только те локальные замены, которые явно отмечены безопасными.

Если установить только Skill без CLI, агент всё равно сможет следовать инструкции, но у него не будет самого сильного слоя детерминированной проверки и Fact Guard.

## Как это работает

HumanizerOS разделяет задачу на три уровня:

1. **Найти.** Языковые правила обнаруживают следы ассистента, штампы, канцелярит, слабую риторику, оформление и контекстные структурные сигналы.
2. **Переписать.** Агент использует найденные проблемы и смыслово редактирует прозу, не считая исходную структуру абзацев обязательной.
3. **Проверить.** Fact Guard сравнивает защищённые значения до и после и обнаруживает потерю или подмену фактов.

Такое разделение сделано намеренно. Regex может безопасно заменить «на сегодняшний день» на «сейчас», но не должен решать, как должен звучать весь абзац. Смысловую редактуру делает модель; движок отвечает за проверяемые сигналы, ограничения и верификацию.

## Как выглядит движок

```bash
$ humanizer-os audit launch.md --lang ru --genre landing
launch.md  [ru/landing]
37 words · 3 sentences · 4 findings · review priority 100/100
W RU-OPEN-001  1:1  Общее вступление [medium]
W RU-RHET-001  1:31  Контраст «не просто X, а Y» [medium]
W RU-LANG-006  1:72  Маркетинговое клише [medium]
W RU-RHET-004  3:1  Формульный вывод [medium]
```

<img src="assets/terminal-demo.svg" alt="Пример аудита HumanizerOS в терминале" width="100%">

Безопасные замены включаются явно:

```bash
$ humanizer-os fix draft.md --diff
-На сегодняшний день мы тестируем релиз для того чтобы запустить его.
+Сейчас мы тестируем релиз чтобы запустить его.

$ humanizer-os verify original.md revised.md
OK  Protected facts match (7 checked).
```

## Чем HumanizerOS отличается

| Принцип | На практике |
|---|---|
| **Свои правила для каждого языка** | Русский и английский используют разные каталоги, примеры, пороги, жанровые ограничения и eval-наборы. |
| **Сохранение фактов** | Имена, числа, даты, цены, единицы, ссылки, версии, идентификаторы и код сравниваются до и после правки. |
| **Объяснимость** | У каждого замечания есть стабильный ID, уверенность, точный фрагмент, рекомендация, жанровая область и происхождение. |
| **Осторожность** | Автоматически применяются только замены, явно отмеченные безопасными. Остальное остаётся рекомендацией редактору. |
| **Локальное ядро** | У ядра нет runtime-зависимостей и сетевых запросов. |
| **Работа с агентом** | Skill задаёт процесс смысловой правки, а движок выполняет проверяемые проверки до и после неё. |
| **Архитектура платформы** | CLI, Python API, JSON, SARIF, схемы, языковые пакеты, Agent Skills и будущий Studio используют общие контракты. |

## Что входит в 0.1

- 65 встроенных правил: 31 английское и 34 русских;
- проверки артефактов, содержания, языка, риторики, оформления и структуры;
- профили `general`, `social`, `email`, `landing`, `article`, `docs`, `fiction`, `academic`, `legal`;
- Fact Guard для защищённых значений и кода;
- текстовый, versioned JSON и SARIF 2.1.0 вывод;
- команды `audit`, `fix`, `verify`, `rules`, `explain`, `profile`;
- Python API и три Agent Skills;
- 164 автоматических теста и 57 двуязычных eval-сценариев.

## CLI и Python

Нужен Python 3.11 или новее.

```bash
git clone https://github.com/alex-zykin/humanizer-os.git
cd humanizer-os
python -m pip install -e .
humanizer-os --version
```

Изолированная установка CLI:

```bash
pipx install git+https://github.com/alex-zykin/humanizer-os.git
```

### Быстрый старт

```bash
# Аудит файла или папки
humanizer-os audit post.md --lang auto --genre social
humanizer-os audit docs/ --lang ru --genre docs --fail-on warning

# Машиночитаемые отчёты
humanizer-os audit post.md --format json > audit.json
humanizer-os audit docs/ --format sarif > humanizer-os.sarif

# Безопасные детерминированные исправления
humanizer-os fix post.md --diff
humanizer-os fix post.md --check
humanizer-os fix post.md --write

# Проверка фактов
humanizer-os verify original.md revised.md

# Каталог правил
humanizer-os rules --lang ru --genre social
humanizer-os explain RU-LANG-002

# Наблюдаемые характеристики авторского текста
humanizer-os profile samples/ --lang auto --format json
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

## Отдельные языковые пакеты

Английский пакет проверяет размытые ссылки на экспертов, преувеличение значимости, универсальные вступления, `not just X but Y`, длинные связки, служебные фразы ассистента, Title Case и механически ровный ритм.

Русский пакет отдельно проверяет канцелярские отглагольные существительные, `является`, переводные вводные конструкции, `не просто X, а Y`, размытые модальные обещания, безличный пассив, шаблонный терапевтический регистр, служебные артефакты и структурную равномерность.

Сводный каталог находится в [docs/RULE_CATALOG.md](docs/RULE_CATALOG.md). Полное объяснение одного правила: `humanizer-os explain RULE_ID`.

## Fact Guard

Fact Guard защищает числа, проценты, цены, единицы измерения, даты, время, URL, email, хендлы, хештеги, semantic version, UUID, commit-like хеши, идентификаторы в верхнем регистре и код.

Факты сравниваются как multiset: исчезновение одного из двух одинаковых значений считается изменением. Fact Guard не доказывает истинность или полную смысловую эквивалентность; ограничения описаны в [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Структура репозитория

```text
humanizer-os/
├── src/humanizer_os/          ядро без runtime-зависимостей
│   └── data/rules/{en,ru}/    отдельные языковые каталоги
├── schemas/                   публичные JSON-контракты
├── skills/                    Agent Skills
├── evals/{en,ru}/             двуязычные regression fixtures
├── tests/                     unit, CLI, schema и eval-тесты
├── docs/                      методология и документация платформы
└── .github/workflows/         CI, dependency review и релизы
```

Подробнее: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/METHODOLOGY.md](docs/METHODOLOGY.md), [docs/PLATFORM.md](docs/PLATFORM.md).

## Контроль качества

```bash
python -m pip install -e ".[dev]"
make all
```

Проверяются тесты, покрытие с ветвлениями, двуязычные eval-сценарии, JSON Schema, ссылки документации, Ruff, mypy, сборка пакета и самоаудит публичной документации.

## Развитие платформы

HumanizerOS спроектирован как система, а не один промпт:

- **Core** — анализ, безопасные правки, контракты и Fact Guard;
- **RU / EN** — независимые языковые пакеты;
- **Voice** — настройка по добровольно предоставленным образцам автора;
- **Expressive RU** — опциональное сохранение, нормализация, маскирование, а позднее управляемая русская экспрессия;
- **Providers** — явные адаптеры локальных и облачных моделей;
- **Studio** — визуальный аудит, diff, профили, политики и командная работа;
- **Integrations** — редакторы, CI, Creator Content OS и внешние пакеты.

План: [docs/ROADMAP.md](docs/ROADMAP.md).

## Участие, приватность и лицензия

Начните с [CONTRIBUTING.md](CONTRIBUTING.md) и [docs/RULE_AUTHORING.md](docs/RULE_AUTHORING.md). Не отправляйте приватные пользовательские тексты, закрытые корпуса и словари без лицензии.

HumanizerOS 0.1 не исполняет анализируемый текст и не делает сетевых запросов. Уязвимости сообщаются по инструкции в [SECURITY.md](SECURITY.md).

[MIT](LICENSE) © 2026 Alex Zykin.