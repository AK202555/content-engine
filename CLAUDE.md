# Content Engine — Claude Code Project

## Purpose

B2B контент-движок для построения личного бренда, создания экспертного контента в LinkedIn
и систематической конвертации внимания аудитории в квалифицированные лиды.

Работает как 5-стадийный пайплайн. Каждая стадия вызывается slash-командой.
Выходные файлы накапливаются в `workspace/` и передаются в следующую стадию.

---

## Контекстные файлы (читать ВСЕГДА первыми)

Перед выполнением любой стадии прочитать все три файла:

- `.claude/context/ICP.md` — идеальный клиент: кто, боли, триггеры, язык
- `.claude/context/positioning.md` — кто я, кому помогаю, какую проблему решаю, в чём отличие
- `.claude/context/offer.md` — оффер: результат, формат, ценность

Если любой файл не заполнен (содержит только шаблонные комментарии) — остановиться и попросить
пользователя заполнить его перед продолжением. Эти файлы — основа каждой стадии.

---

## Стадии пайплайна и slash-команды

| Команда              | Файл стадии                         | Что делает                                         |
|----------------------|-------------------------------------|----------------------------------------------------|
| `/analyse-audience`  | `pipeline/1-audience-analysis.md`   | Строит портрет аудитории и профили персон          |
| `/build-strategy`    | `pipeline/2-strategy.md`            | Определяет ICP, позиционирование, контент-стратегию, OKR |
| `/create-content`    | `pipeline/3-content-generation.md`  | Генерирует LinkedIn-посты и экспертный контент     |
| `/generate-leads`    | `pipeline/4-leadgen-outreach.md`    | Создаёт лид-магниты и outreach-последовательности  |
| `/analyse-results`   | `pipeline/5-analytics.md`           | Анализирует результаты и формирует план оптимизации |

При вводе команды: прочитать соответствующий файл стадии и следовать его инструкциям.

---

## Конвенция загрузки skills

Skills находятся в `.claude/skills/`. Каждый файл стадии указывает, какие skills использовать.

Два источника skills — выбор по качеству содержимого (версия, полнота, inline-контент):

| Скилл | Использовать |
|-------|-------------|
| `copywriting` | `alirezarezvani__claude-skills__copywriting` |
| `copy-editing` | `coreyhaines31__marketingskills__copy-editing` |
| `content-strategy` | `coreyhaines31__marketingskills__content-strategy` |
| `social-content` | `coreyhaines31__marketingskills__social-content` |
| `launch-strategy` | `coreyhaines31__marketingskills__launch-strategy` |
| `marketing-psychology` | `coreyhaines31__marketingskills__marketing-psychology` |
| `marketing-ideas` | `alirezarezvani__claude-skills__marketing-ideas` |
| `free-tool-strategy` | `alirezarezvani__claude-skills__free-tool-strategy` |
| `competitor-alternatives` | `alirezarezvani__claude-skills__competitor-alternatives` |

Для скиллов без пересечений — использовать тот источник, где он есть.

Использовать skill = принять профессиональный фрейм и методологию, описанные в его SKILL.md.
Загружать skills в порядке, указанном в файле стадии.

---

## Структура workspace

```
workspace/
├── analysis/    ← Stage 1 (аудитория) + Stage 5 (аналитика)
├── strategy/    ← Stage 2 (стратегия, ICP, позиционирование)
├── posts/       ← Stage 3 (LinkedIn-посты, контент-календарь)
├── leads/       ← Stage 4 (лид-магниты)
└── outreach/    ← Stage 4 (outreach-последовательности, DM-шаблоны)
```

---

## Соглашение по именованию файлов

- Файлы анализа: `workspace/analysis/[тип]-[YYYY-MM-DD].md`
- Файлы стратегии: `workspace/strategy/[тип].md` (один файл, перезаписывается при каждом запуске)
- Файлы контента: `workspace/posts/[тип]-[YYYY-MM-DD].md`
- Лид-магниты: `workspace/leads/[тип]-[YYYY-MM-DD].md`
- Outreach: `workspace/outreach/[тип]-[YYYY-MM-DD].md`

---

## Цепочка зависимостей

```
[1-аудитория] → [2-стратегия] → [3-контент] → [4-лидген] → [5-аналитика]
      ↑                                                              |
      └──────────────── feedback loop ──────────────────────────────┘
```

Каждая стадия читает выходные файлы всех предыдущих стадий.
Stage 5 возвращает исследовательский бриф в Stage 1.

---

## Быстрый старт

1. Заполнить `.claude/context/ICP.md`, `.claude/context/positioning.md`, `.claude/context/offer.md`
2. `/analyse-audience` — построить портрет аудитории
3. `/build-strategy` — определить позиционирование и контент-план
4. `/create-content` — сгенерировать первую партию постов
5. `/generate-leads` — создать outreach-материалы
6. `/analyse-results` — через 2–4 недели активности проанализировать результаты

---

## Правила поведения

- Не выдумывать статистику, отзывы и цитаты клиентов. Если данных нет — явно это указать.
- Писать в голосе, определённом в `.claude/context/positioning.md`.
- Если context-файл не заполнен — задавать конкретные вопросы, не предполагать самостоятельно.
- Сохранять каждый выходной файл в правильную поддиректорию `workspace/` до конца сессии.
- Если `workspace/strategy/` не существует — создать её перед записью файлов стратегии.
