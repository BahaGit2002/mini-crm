# Mini CRM - Система распределения лидов

Система для автоматического распределения обращений лидов между операторами с учётом их загрузки и компетенций по источникам.

## Структура проекта

```
mini_crm/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI приложение, роутинг
│   ├── database.py             # Конфигурация SQLAlchemy
│   ├── dependencies.py         # Dependency Injection (get_db)
│   │
│   ├── models/                 # SQLAlchemy модели (ORM)
│   │   ├── __init__.py
│   │   ├── operator.py         # Модель оператора
│   │   ├── source.py           # Модель источника
│   │   ├── lead.py             # Модель лида
│   │   ├── appeal.py           # Модель обращения
│   │   └── operator_weight.py  # Модель весов оператора
│   │
│   ├── schemas/                # Pydantic схемы (валидация, сериализация)
│   │   ├── __init__.py
│   │   ├── operator.py
│   │   ├── source.py
│   │   ├── lead.py
│   │   └── appeal.py
│   │
│   ├── repositories/           # Data Access Layer (работа с БД)
│   │   ├── __init__.py
│   │   ├── operator.py         # CRUD операторов
│   │   ├── source.py           # CRUD источников
│   │   ├── lead.py             # CRUD лидов
│   │   └── appeal.py           # CRUD обращений
│   │
│   ├── services/               # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── distribution.py    # Алгоритм распределения
│   │   └── appeal.py          # Бизнес-логика обращений
│   │
│   └── routes/                 # API endpoints (контроллеры)
│       ├── __init__.py
│       ├── operators.py        # /operators/*
│       ├── sources.py          # /sources/*
│       ├── appeals.py          # /appeals/*
│       └── stats.py            # /stats/*
│
├── requirements.txt
├── README.md
└── test_api.py
```

## Архитектура слоёв

### 1. **Models** (SQLAlchemy ORM)
- Описание структуры таблиц БД
- Определение связей между таблицами
- Только структура данных, без бизнес-логики

### 2. **Schemas** (Pydantic)
- Валидация входных данных
- Сериализация выходных данных
- Документация API

### 3. **Repositories** (Data Access Layer)
- CRUD операции с БД
- Все SQL-запросы изолированы здесь
- Возвращают модели SQLAlchemy

### 4. **Services** (Business Logic Layer)
- Бизнес-логика приложения
- Координация между репозиториями
- Алгоритмы (например, распределение)

### 5. **Routes** (API Controllers)
- HTTP эндпоинты
- Валидация запросов через schemas
- Вызов services для обработки
- Возврат ответов

### 6. **Database & Dependencies**
- Конфигурация подключения к БД
- Dependency Injection для сессий

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/BahaGit2002/mini-crm.git
cd mini-crm
```

### 2. Настройка переменных окружения

Скопируйте файл `.env_example` в `.env`:

```bash
cp .env_example .env
```

Отредактируйте `.env` файл и настройте переменные окружения:
- Для локального запуска: `DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/mini_crm_db`
- Для Docker: `DATABASE_URL=postgresql+psycopg2://root:password@postgres:5432/mini_crm_db`

### 3. Локальный запуск

#### Требования
- Python 3.10+
- PostgreSQL
- Poetry (для управления зависимостями)

#### Установка зависимостей

```bash
# Установка Poetry (если не установлен)
curl -sSL https://install.python-poetry.org | python3 -

# Установка зависимостей проекта
poetry install
```

#### Настройка базы данных

1. Создайте базу данных PostgreSQL:
```bash
createdb mini_crm_db
```

2. Примените миграции:
```bash
poetry run alembic upgrade head
```

#### Запуск приложения

```bash
# Активация виртуального окружения Poetry
poetry shell

# Запуск приложения
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Или без активации shell:
```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API будет доступно:
- Приложение: `http://localhost:8000`
- Swagger документация: `http://localhost:8000/docs`
- ReDoc документация: `http://localhost:8000/redoc`

### 4. Запуск с Docker

#### Требования
- Docker
- Docker Compose

#### Запуск

```bash
# Сборка и запуск контейнеров
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

При первом запуске необходимо применить миграции:

```bash
# Выполнение миграций в контейнере
docker-compose exec backend alembic upgrade head
```

#### Остановка

```bash
# Остановка контейнеров
docker-compose down

# Остановка с удалением volumes (удалит данные БД)
docker-compose down -v
```

### 5. Запуск тестов

#### Локальный запуск тестов

```bash
# Запуск всех тестов
poetry run pytest

# Запуск с покрытием кода
poetry run pytest --cov=app --cov-report=html --cov-report=term-missing

# Запуск конкретного теста
poetry run pytest tests/test_models.py

# Запуск с подробным выводом
poetry run pytest -v
```

#### Запуск тестов в Docker

```bash
# Запуск тестов в контейнере
docker-compose exec backend pytest

# С покрытием кода
docker-compose exec backend pytest --cov=app --cov-report=html --cov-report=term-missing
```

Отчет о покрытии кода будет доступен в директории `htmlcov/index.html`

## Модель данных

### Сущности и их ответственность

**Operator (Оператор)**
- Сотрудник, обрабатывающий обращения
- Имеет лимит нагрузки (max_load)
- Может быть активирован/деактивирован

**Source (Источник/Бот)**
- Канал поступления обращений (Telegram, WhatsApp и т.д.)
- Связан с операторами через веса

**OperatorWeight (Вес оператора)**
- Связывает оператора и источник
- Определяет компетенцию/долю трафика
- Используется в алгоритме распределения

**Lead (Лид)**
- Уникальный клиент
- Идентифицируется по external_id
- Может обращаться через разные источники

**Appeal (Обращение)**
- Конкретный факт обращения лида
- Связан с лидом, источником и оператором
- Имеет статус (active/closed)

### Связи

```
Operator 1----* OperatorWeight *----1 Source
   |                                    |
   |                                    |
   *                                    *
Appeal *----1 Lead
```

## Алгоритм распределения

### Компоненты

**DistributionService** (`app/services/distribution.py`)
- Основная логика выбора оператора
- Метод `select_operator(source_id)` возвращает ID оператора

### Процесс распределения

```python
# 1. Получаем настройки весов для источника
weights = db.query(OperatorWeight).filter_by(source_id=source_id).all()

# 2. Фильтруем доступных операторов
for weight in weights:
    if operator.is_active and current_load < max_load:
        available_operators.append(operator)

# 3. Weighted Random Selection
probabilities = [weight / sum_of_weights for weight in weights]
selected = random.choices(operators, weights=probabilities)[0]
```

### Критерии доступности оператора

1. **Активность**: `is_active = True`
2. **Нагрузка**: `current_load < max_load`

Нагрузка = количество обращений со статусом "active"

### Пример

Источник: "Telegram Bot"
- Оператор A: вес 10, нагрузка 2/5 ✅
- Оператор B: вес 30, нагрузка 9/10 ✅
- Оператор C: вес 20, нагрузка 5/5 ❌

Доступны A и B. Суммарный вес: 40
- Вероятность A: 10/40 = 25%
- Вероятность B: 30/40 = 75%

### Идентификация лида

Лиды идентифицируются по `external_id`:
```python
lead = db.query(Lead).filter_by(external_id="tg_user_123").first()
if not lead:
    lead = Lead(external_id="tg_user_123", ...)
```

Один `external_id` = один лид, даже при обращениях через разные источники.

## API Endpoints

### Операторы

```http
POST   /operators/              Создать оператора
GET    /operators/              Список операторов с нагрузкой
GET    /operators/{id}          Получить оператора
PATCH  /operators/{id}          Обновить (активность, лимит)
```

### Источники

```http
POST   /sources/                Создать источник
GET    /sources/                Список источников
GET    /sources/{id}            Получить источник
POST   /sources/{id}/weights    Настроить веса операторов
GET    /sources/{id}/weights    Получить веса
```

### Обращения

```http
POST   /appeals/                Создать обращение
PATCH  /appeals/{id}/close      Закрыть обращение
GET    /appeals/leads           Список лидов
GET    /appeals/leads/{id}/appeals  Обращения лида
```

### Статистика

```http
GET    /stats/distribution          Распределение по источникам
GET    /stats/sources/{id}/operators  Инфо о доступности операторов
```

## Примеры использования

### 1. Создание операторов
```bash
curl -X POST http://localhost:8000/operators/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Анна Иванова",
    "is_active": true,
    "max_load": 5
  }'
```

### 2. Создание источника
```bash
curl -X POST http://localhost:8000/sources/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Telegram Bot",
    "description": "Основной бот компании"
  }'
```

### 3. Настройка весов (25% и 75%)
```bash
curl -X POST http://localhost:8000/sources/1/weights \
  -H "Content-Type: application/json" \
  -d '[
    {"operator_id": 1, "weight": 10},
    {"operator_id": 2, "weight": 30}
  ]'
```

### 4. Создание обращения
```bash
curl -X POST http://localhost:8000/appeals/ \
  -H "Content-Type: application/json" \
  -d '{
    "lead_external_id": "tg_user_12345",
    "source_id": 1,
    "message": "Здравствуйте!",
    "lead_name": "Иван Петров",
    "lead_phone": "+79991234567"
  }'
```

### 5. Просмотр статистики
```bash
curl http://localhost:8000/stats/distribution
```

## Преимущества архитектуры

### Разделение ответственности
- **Models**: структура данных
- **Repositories**: работа с БД
- **Services**: бизнес-логика
- **Routes**: HTTP обработка

### Переиспользование кода
```python
# Repositories можно использовать в разных services
class AppealService:
    def __init__(self, db):
        self.lead_repo = LeadRepository(db)
        self.appeal_repo = AppealRepository(db)
```

### Тестируемость
Каждый слой можно тестировать независимо:
```python
# Тест репозитория (с тестовой БД)
def test_operator_repository():
    repo = OperatorRepository(test_db)
    op = repo.create(OperatorCreate(name="Test"))
    assert op.name == "Test"

# Тест сервиса (с mock репозиториями)
def test_distribution_service(mock_db):
    service = DistributionService(mock_db)
    operator_id = service.select_operator(source_id=1)
    assert operator_id is not None
```

### Масштабируемость
- Легко добавлять новые эндпоинты
- Легко менять алгоритмы в services
- Легко переходить на другую БД

### Читаемость
```python
# Понятно, что делает каждый файл:
app/repositories/operator.py  # CRUD операторов
app/services/distribution.py  # Алгоритм распределения
app/routes/operators.py       # API для операторов
```

## Возможные улучшения

- [ ] Логирование (structlog)
- [ ] Метрики и мониторинг
- [ ] Async SQLAlchemy
- [ ] Кэширование (Redis)
- [ ] Очереди задач (Celery)
- [ ] WebSocket для real-time уведомлений