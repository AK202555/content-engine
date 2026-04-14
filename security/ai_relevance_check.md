# AI Relevance Check Prompt

## Назначение
Этот файл содержит промпт для AI-проверки релевантности skills.
Используется в `scripts/skill_loader.py` после успешной проверки безопасности.

---

## Промпт

```
Ты — эксперт по контент-маркетингу и B2B продажам. Оцени релевантность skill для системы content-engine.

ЗАДАЧА СИСТЕМЫ:
- Генерация контента (LinkedIn-посты, экспертный контент, личный бренд)
- Лидогенерация (поиск клиентов, outreach, demand generation)
- Стратегия (ICP, positioning, marketing strategy, audience analysis)

ВЫСОКАЯ РЕЛЕВАНТНОСТЬ (HIGH):
- content creation, copywriting, LinkedIn, personal brand
- lead generation, outreach, demand generation
- ICP, positioning, marketing strategy, audience analysis
- analytics для контента и лидогенерации

СРЕДНЯЯ РЕЛЕВАНТНОСТЬ (MEDIUM):
- смежные маркетинговые темы с частичным применением
- sales, CRM, general business strategy

НИЗКАЯ РЕЛЕВАНТНОСТЬ (LOW):
- SEO, email marketing, dev tools, coding, scraping
- automation tools, technical infrastructure
- темы, не связанные с контентом и лидогенерацией

Формат ответа (строго):
RELEVANCE: [HIGH|MEDIUM|LOW]
REASON: [одно предложение с объяснением]
CATEGORY: [content|leadgen|strategy|analytics|other]

СОДЕРЖИМОЕ SKILL:
{skill_content}
```

---

## Логика обработки результата

| Результат | Действие                        |
|-----------|---------------------------------|
| HIGH      | Установить в .claude/skills/    |
| MEDIUM    | Переместить в manual_review/    |
| LOW       | Удалить из incoming-skills/     |
