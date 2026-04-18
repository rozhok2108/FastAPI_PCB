# 🛠️ FASTAPI_PY_DZ — Сервис управления заказами и услугами

Полнофункциональное веб-приложение на **FastAPI** для автоматизации учёта заказов, управления услугами и распределения ролей пользователей. Проект включает REST API, веб-интерфейс на Jinja2, JWT-аутентификацию, ролевой доступ (RBAC), контейнеризацию и покрытие тестами.

## ✨ Основные возможности
- 🔐 **JWT-аутентификация** и регистрация пользователей
- 👥 **Ролевая модель**: `Guest`, `Client`, `Engineer`, `Manager`, `Admin`
- 📦 **CRUD для заказов и услуг** с отслеживанием статусов
- 🌐 **Адаптивный веб-интерфейс** (Jinja2 + CSS/JS) с персональными дашбордами для каждой роли
- 🐳 **Docker & Docker Compose** для быстрого развёртывания
- 🧪 **Автотесты** на `pytest`
- 📊 Автоматическая документация API (Swagger UI / ReDoc)
- 📧 Система уведомлений и утилита инициализации администратора

## 🛠️ Технологический стек
| Категория | Технологии |
|-----------|------------|
| Backend | FastAPI, Uvicorn, SQLAlchemy 2.0, Pydantic v2 |
| Auth & Security | JWT, passlib, python-jose, bcrypt |
| Database | PostgreSQL / SQLite (настраивается через `config.py`) |
| Frontend | Jinja2, HTML5, CSS3, Vanilla JS |
| DevOps | Docker, Docker Compose, pytest |

## 📁 Структура проекта
```bash
.
├── app/
│   ├── auth.py                 # Логика аутентификации и авторизации
│   ├── config.py               # Настройки приложения
│   ├── database.py             # Подключение к БД
│   ├── dependencies.py         # Зависимости FastAPI
│   ├── __init__.py
│   ├── main.py                 # Точка входа приложения
│   ├── models.py               # SQLAlchemy модели
│   ├── schemas.py              # Pydantic схемы
│   ├── routers/
│   │   ├── auth.py             # Роуты аутентификации
│   │   ├── orders.py           # Роуты заказов
│   │   ├── services.py         # Роуты услуг
│   │   └── users.py            # Роуты пользователей
│   ├── static/
│   │   ├── css/style.css       # Стили
│   │   ├── images/             # Изображения интерфейса
│   │   └── js/app.js           # Клиентская логика
│   ├── templates/              # Jinja2 HTML-шаблоны
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── dashboard_*.html    # Дашборды для разных ролей
│   ├── tests/
│   │   ├── conftest.py         # Фикстуры pytest
│   │   └── test_api.py         # API-тесты
│   └── utils/
│       ├── init_admin.py       # Инициализация админа
│       ├── logic.py            # Бизнес-логика
│       └── notifications.py    # Система уведомлений
├── docker-compose.yml          # Оркестрация контейнеров
├── Dockerfile                  # Образ приложения
├── requirements.txt            # Зависимости Python
├── smd.png                     # Изображения для README
├── контроль_качества.jpg
├── лаборатория.webp
├── производство_печатных_плат.jpg
└── Презентация_FASTAPI.pptx
10 directories, 39 files
```
                                     
Запуск через Docker
```bash
docker-compose up -d --build
```

Приложение будет доступно по адресу: http://localhost:8000
📖 Документация API
После запуска автоматически генерируется интерактивная документация:
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

🧪 Тестирование
```bash
pytest app/tests/ -v
```