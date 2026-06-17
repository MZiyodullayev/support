# Screener Bot — Django

AI-бот: мониторит папку со скриншотами → анализирует через Groq → рассылает ответ в Telegram.

## Стек

- Django 6 + DRF + JWT
- Django Q2 (очередь задач, хранится в SQLite — Redis не нужен)
- Watchdog (мониторинг папки)
- Groq API (llama-4-scout vision)
- Telegram Bot API

## Структура

```
src/
├── apps/
│   ├── users/          # кастомный User
│   ├── utils/          # утилиты
│   └── screener/       # основное приложение
│       ├── models.py   # WhitelistUser, Screenshot, AnalysisResult
│       ├── tasks.py    # Groq + Telegram рассылка
│       ├── admin.py
│       └── management/commands/run_watcher.py
├── api/
│   ├── serializer/screener.py
│   ├── views/screener.py
│   └── urls.py
└── config/
    └── settings.py
```

## Установка (Windows)

```bash
# 1. Распаковать архив, открыть папку
cd src

# 2. Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate        # Windows CMD
# или
source venv/bin/activate     # Git Bash / WSL

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить .env
copy .env.example .env
# Открыть .env и заполнить своими ключами

# 5. Миграции (создаёт db.sqlite3 с таблицами для очереди)
python manage.py migrate

# 6. Создать суперпользователя (для Django Admin)
python manage.py createsuperuser
```

## Запуск (3 терминала вместо 4)

```bash
# Терминал 1 — воркер очереди задач
cd src
venv\Scripts\activate
python manage.py qcluster

# Терминал 2 — watchdog (слежка за папкой)
cd src
venv\Scripts\activate
python manage.py run_watcher

# Терминал 3 — Django сервер
cd src
venv\Scripts\activate
python manage.py runserver
```

## API эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/v1/screener/upload/` | Загрузить скриншоты (multipart, поле `images`) |
| GET | `/api/v1/screener/screenshots/` | Список скриншотов + результаты |
| GET | `/api/v1/screener/screenshots/{id}/` | Детали + ответ AI |
| GET | `/api/v1/screener/whitelist/` | Вайтлист (только для админов) |

## Добавить пользователей в whitelist

Django Admin → `http://localhost:8000/admin/` → Screener → Whitelist users → Add
