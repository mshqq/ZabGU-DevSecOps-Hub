# Отчёт о сканировании — {{ project_title }}

| Параметр | Значение |
|---|---|
| Проект | {{ project_title }} |
| Репозиторий | [{{ repo_url }}]({{ repo_url }}) |
| ID скана | {{ scan_id }} |
| Коммит | `{{ commit_sha }}` |
| Завершён | {{ finished_at or "—" }} |

{% if truncated %}
> **Внимание:** список находок обрезан из-за превышения лимита. Отчёт может быть неполным.
{% endif %}

## Сводка

| Критичность | Кол-во |
|---|---|
| P0 — Критические | {{ summary.get("P0", 0) }} |
| P1 — Высокие | {{ summary.get("P1", 0) }} |
| P2 — Средние | {{ summary.get("P2", 0) }} |
| **Итого** | **{{ summary.get("P0", 0) + summary.get("P1", 0) + summary.get("P2", 0) }}** |

## Находки

{% for severity, title in [("P0", "Критические"), ("P1", "Высокие"), ("P2", "Средние")] %}
### {{ severity }} — {{ title }}

{% for f in grouped.get(severity, []) %}
**Находка {{ loop.index }}**

| Поле | Значение |
|---|---|
| Правило | `{{ f.rule_id }}` |
| Файл | `{{ f.file_path }}` |
| Строка | {{ f.line_no or "—" }} |
| Секрет (маска) | `{{ f.masked_value }}` |
| Уверенность | {{ f.confidence }} |
| Источник | {{ f.source }} |
| Статус | {{ f.status }} |
| Коммит | `{{ f.commit_sha }}` |
{% if f.context %}
| Контекст | `{{ f.context }}` |
{% endif %}

{% else %}
Находок не обнаружено.

{% endfor %}
{% endfor %}
---

*Отчёт сформирован сервисом [ZabGU DevSecOps Hub](https://github.com/mshqq/ZabGU-DevSecOps-Hub). Секреты приведены в маскированном виде.*
