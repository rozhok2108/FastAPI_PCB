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
.
├── app
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── routers
│   │   ├── auth.py
│   │   ├── orders.py
│   │   ├── services.py
│   │   └── users.py
│   ├── schemas.py
│   ├── static
│   │   ├── css
│   │   │   └── style.css
│   │   ├── images
│   │   │   ├── smd.png
│   │   │   ├── контроль_качества.jpg
│   │   │   ├── лаборатория.webp
│   │   │   └── производство_печатных плат.jpg
│   │   └── js
│   │       └── app.js
│   ├── templates
│   │   ├── base.html
│   │   ├── dashboard_admin.html
│   │   ├── dashboard_client.html
│   │   ├── dashboard_engineer.html
│   │   ├── dashboard_manager.html
│   │   ├── dashboard_redirect.html
│   │   ├── login.html
│   │   └── register.html
│   ├── tests
│   │   ├── conftest.py
│   │   └── test_api.py
│   └── utils
│       ├── init_admin.py
│       ├── logic.py
│       └── notifications.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── smd.png
├── контроль_качества.jpg
├── лаборатория.webp
├── Презентация_FASTAPI.pptx
└── производство_печатных плат.jpg

10 directories, 39 files
                                     
Запуск через Docker
docker-compose up -d --build

Приложение будет доступно по адресу: http://localhost:8000
📖 Документация API
После запуска автоматически генерируется интерактивная документация:
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

🧪 Тестирование
pytest app/tests/ -v