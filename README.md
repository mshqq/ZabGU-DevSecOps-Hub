# ZabGU DevSecOps Hub

Сервис автоматического аудита безопасности студенческих Git-репозиториев. Ищет утечки секретов (пароли, ключи, токены) и типовые ошибки конфигурации, выдаёт приоритизированный отчёт.

> Сканирование строго пассивное: код проверяемого проекта не выполняется, эксплуатация уязвимостей не производится. Сервис — учебный инструмент, не замена профессиональному пентесту.

---

## Содержание

- [Как это работает](#как-это-работает)
- [Стек](#стек)
- [Быстрый старт](#быстрый-старт)
- [Структура проекта](#структура-проекта)
- [Переменные окружения](#переменные-окружения)
- [Роли и доступ](#роли-и-доступ)
- [Модель данных](#модель-данных)
- [API](#api)
- [Разработка](#разработка)
- [Roadmap](#roadmap)

---
## Как это работает

```
Студент добавляет репозиторий
        ↓
Подтверждает права (файл-маркер с токеном в репо)
        ↓
Запускает скан → фоновая задача
        ↓
Клонирование во временную папку → поиск секретов по правилам
        ↓
Находки маскируются, приоритизируются (P0/P1/P2)
        ↓
Временная папка удаляется → отчёт доступен в Markdown
```

Секреты никогда не сохраняются в открытом виде — только маска (`ghp_a1b2****xyz`).

## Стек

| Слой                  | Технология                             |
| --------------------- | -------------------------------------- |
| Backend               | Python 3.12, Flask, SQLAlchemy         |
| БД                    | SQLite                                 |
| Фоновые задачи        | Python `threading`                     |
| Frontend              | Jinja2 + Tailwind CSS                  |
| Изоляция сканирования | временная папка, удаляется после скана |
| Отчёт                 | Markdown (PDF - в планах)              |
| Деплой                | VPS, Nginx                             |

Почему так просто: Redis/Docker/PDF добавляют инфраструктурный риск без выигрыша для MVP.

## Быстрый старт

```bash
git clone https://github.com/mshqq/ZabGU-DevSecOps-Hub.git
cd ZabGU-DevSecOps-Hub

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env  # заполнить значения, см. ниже

flask db upgrade       # применить миграции
flask run               # http://localhost:5000
```

## Структура проекта

```
.
├── app/
│   ├── models/          # User, Project, Scan, Finding
│   ├── routes/          # эндпоинты Flask
│   ├── scanner/         # логика сканирования
│   ├── templates/       # Jinja2-шаблоны
│   └── static/          # CSS/JS
├── migrations/
├── .env.example
├── requirements.txt
└── README.md
```

## Переменные окружения

| Переменная           | Описание                     | Пример                                                                                         |
| -------------------- | ---------------------------- | ---------------------------------------------------------------------------------------------- |
| `FLASK_SECRET`       | ключ сессий Flask            | случайная строка 32+ символов (`python -c "import secrets; print(secrets.token_urlsafe(32))"`) |
| `DATABASE_URL`       | строка подключения к БД      | `sqlite:///zabgu-devsecops.db`                                                                 |
| `FLASK_DEBUG`        | режим отладки                | `0` / `1`                                                                                      |
| `FLASK_HOST`         | хост для `flask run`         | `127.0.0.1`                                                                                    |
| `FLASK_PORT`         | порт для `flask run`         | `5000`                                                                                         |
| `SCAN_TEMP_DIR`      | папка для временных клонов   | `/tmp/zabgu-scans`                                                                             |
| `MAX_SCANS_PER_HOUR` | лимит сканов на пользователя | `3`                                                                                            |
| `MAX_REPO_SIZE_MB`   | лимит размера репозитория    | `200`                                                                                          |

## Роли и доступ

| Роль        | Права                                                                 |
| ----------- | --------------------------------------------------------------------- |
| **Студент** | добавляет свои репозитории, запускает сканы, видит только свои отчёты |
| **Админ**   | управляет пользователями, включает/выключает правила детектирования   |

Доступ ролевой. Каждый эндпоинт проверяет `owner_id` - студент не получит чужой отчёт по прямому запросу к API).

## Модель данных

**User**: 
- `id`
- `email`
- `password_hash`,
- `role` (`student`/`admin`)
- `created_at`
- `is_active`

**Project**:
- `id`
- `owner_id`→User
- `title`
- `repo_url`
- `provider` (`github`/`gitlab`)
- `ownership_token`
- `ownership_verified_at`
- `created_at`

**Scan**:
- `id`, 
- `project_id`→Project, 
- `status` (`queued`/`running`/`done`/`failed`)
- `started_at`
- `finished_at`
- `commit_sha`
- `truncated`
- `error_message`
- `created_at`

**Finding**: 
- `id`, 
- `scan_id`→Scan
- `rule_id`
- `severity` (`P0`/`P1`/`P2`)
- `confidence` (`high`/`medium`/`low`)
- `source`
- `file_path`
- `line_no`
- `commit_sha`
- `masked_value`
- `context`
- `status` (`new`/`confirmed`/`false_positive`)

Правила детектирования - не таблица в БД, а код: набор Python-модулей/конфигов в
`app/scanner` (код правила, паттерн). `Finding.rule_id` ссылается на код правила из кода, а не на внешний ключ.

Связи: `User 1—N Project 1—N Scan 1—N Finding`.

## API

| Метод  | Путь                        | Описание                   |
| ------ | --------------------------- | -------------------------- |
| `POST` | `/api/auth/register`        | регистрация                |
| `POST` | `/api/auth/login`           | вход                       |
| `POST` | `/api/projects`             | добавить репозиторий       |
| `POST` | `/api/projects/<id>/verify` | подтвердить права владения |
| `POST` | `/api/projects/<id>/scans`  | запустить скан             |
| `GET`  | `/api/scans/<id>`           | статус скана               |
| `GET`  | `/api/scans/<id>/report`    | отчёт (JSON)               |
| `GET`  | `/api/scans/<id>/report.md` | отчёт (Markdown)           |

Все изменяющие запросы — только по сессии + CSRF-токен.

## Разработка

```bash
# миграция после изменения моделей
flask db migrate -m "описание"
flask db upgrade
```

## Roadmap

Не входит в MVP, но запланировано: GitHub OAuth вместо файла-маркера, проверка задеплоенного стенда, экспорт в PDF, миграция фронтенда на React.

Лицензия: MIT
