# 🔄 Руководство по рефакторингу EFT Helper Bot

## Обзор изменений

Проект был полностью рефакторен согласно техническому заданию для создания чистой, модульной архитектуры.

## ✅ Что было сделано

### 1. **Новая архитектура (Layered Architecture)**

```
EFT Helper/
├── main.py                      # ⭐ ЕДИНАЯ точка входа
├── api_clients/                 # 🌐 Централизованные API клиенты
│   ├── __init__.py
│   └── tarkov_api_client.py    # Единый клиент для tarkov.dev
├── services/                    # 💼 Бизнес-логика (новое!)
│   ├── __init__.py
│   ├── weapon_service.py       # Логика работы с оружием
│   ├── build_service.py        # Логика работы со сборками
│   ├── user_service.py         # Логика работы с пользователями
│   └── sync_service.py         # Синхронизация с API
├── handlers/                    # 🎮 Обработчики команд
│   ├── common.py               # Используют services
│   ├── search.py               # Используют services
│   ├── builds.py               # Используют services
│   └── ...
├── database/                    # 💾 Работа с БД
│   ├── models.py
│   ├── db.py
│   └── config.py
└── scripts/                     # 🔧 Вспомогательные скрипты
    └── sync_data.py            # ⭐ Объединённый скрипт синхронизации
```

### 2. **Централизация API**

**Было:**
- Множество прямых вызовов к `tarkov_api.py`
- Кэширование разбросано
- Дублирование кода

**Стало:**
```python
# api_clients/tarkov_api_client.py - ЕДИНСТВЕННЫЙ клиент
class TarkovAPIClient:
    async def get_all_weapons()      # Кэширование 24 часа
    async def get_all_traders()      # Кэширование 24 часа
    async def get_all_mods()         # Кэширование 24 часа
    async def get_market_prices()    # Кэширование 24 часа
```

### 3. **Service Layer (Бизнес-логика)**

**Было:** Handlers напрямую вызывали DB и API

**Стало:**
```python
# Пример из handlers/search.py
async def start_search(message, user_service):
    user = await user_service.get_or_create_user(message.from_user.id)
    # user_service инкапсулирует логику работы с пользователями

# Пример из handlers/builds.py
async def show_random_build(message, build_service):
    build_data = await build_service.get_random_build()
    # build_service возвращает build + weapon + modules
```

### 4. **Удаление дублирования**

#### Удалённые/устаревшие файлы:
- ❌ `utils/tarkov_api.py` → заменён на `api_clients/tarkov_api_client.py`
- ❌ `utils/builds_fetcher.py` → функционал включён в `sync_service.py`
- ❌ `utils/build_calculator.py` → можно удалить (не используется)
- ❌ `scripts/sync_tarkov_data.py` → заменён на `scripts/sync_data.py`
- ❌ `scripts/auto_sync_builds.py` → заменён на `scripts/sync_data.py`
- ❌ `scripts/populate_db.py` → вызывается из `scripts/sync_data.py`

#### Объединённые скрипты:
```bash
# Вместо 3 разных скриптов:
python scripts/sync_data.py  # Единый скрипт для всего
```

### 5. **Dependency Injection**

Middleware автоматически инжектирует сервисы в handlers:

```python
# main.py
@dp.update.outer_middleware()
async def inject_services(handler, event, data):
    data["db"] = self.db
    data["weapon_service"] = self.weapon_service
    data["build_service"] = self.build_service
    data["user_service"] = self.user_service
    data["api_client"] = self.api_client
    return await handler(event, data)
```

## 🚀 Как использовать

### Запуск бота

**Через Poetry (разработка):**
```bash
# Установка зависимостей
poetry install

# Запуск бота
poetry run python main.py
```

**Через Docker (production):**
```bash
# Запуск с docker-compose
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot
```

### Синхронизация данных

```bash
# Через Poetry
poetry run python scripts/sync_data.py

# Через Docker
docker-compose exec bot python scripts/sync_data.py

# Выбор:
# 1. Синхронизация с tarkov.dev API
# 2. Тестовые данные
# 3. Оба варианта
```

## 📋 Правила разработки (ВАЖНО!)

### ❌ ЗАПРЕЩЕНО:

1. **Прямые HTTP запросы из handlers**
   ```python
   # ❌ НЕПРАВИЛЬНО
   async with aiohttp.ClientSession() as session:
       await session.get("https://api.tarkov.dev/...")
   ```

2. **Прямой доступ к DB из handlers**
   ```python
   # ❌ НЕПРАВИЛЬНО
   async def handler(message, db):
       weapons = await db.get_all_weapons()
   ```

3. **Бизнес-логика в handlers**
   ```python
   # ❌ НЕПРАВИЛЬНО
   async def handler(message):
       # 50 строк логики фильтрации, расчётов и т.д.
   ```

### ✅ ПРАВИЛЬНО:

1. **Используйте API Client**
   ```python
   # ✅ ПРАВИЛЬНО
   weapons = await api_client.get_all_weapons()
   ```

2. **Используйте Services**
   ```python
   # ✅ ПРАВИЛЬНО
   async def handler(message, weapon_service):
       weapons = await weapon_service.search_weapons(query)
   ```

3. **Handlers только координация**
   ```python
   # ✅ ПРАВИЛЬНО
   async def handler(message, build_service, user_service):
       user = await user_service.get_or_create_user(message.from_user.id)
       build = await build_service.get_random_build()
       await message.answer(format_build(build, user.language))
   ```

## 📊 Преимущества новой архитектуры

### Для пользователей:
- ✅ Быстрее работает (умное кэширование)
- ✅ Актуальные данные из API
- ✅ Один файл для запуска (`main.py`)

### Для разработчиков:
- ✅ Понятная структура
- ✅ Легко тестировать
- ✅ Нет дублирования
- ✅ Централизованная работа с API
- ✅ Легко добавлять новые фичи

### Для поддержки:
- ✅ Логирование централизовано
- ✅ Обработка ошибок на всех уровнях
- ✅ Легко отследить баги

## 🔄 Миграция существующего кода

### Если вы писали handlers:

**Было:**
```python
async def my_handler(message: Message, db: Database):
    user = await db.get_or_create_user(message.from_user.id)
    weapons = await db.get_all_weapons()
```

**Стало:**
```python
async def my_handler(message: Message, user_service, weapon_service):
    user = await user_service.get_or_create_user(message.from_user.id)
    weapons = await weapon_service.get_weapons_by_category(category)
```

### Если вы использовали API:

**Было:**
```python
from utils.tarkov_api import tarkov_api
weapons = await tarkov_api.get_all_weapons()
```

**Стало:**
```python
# В handler автоматически инжектится api_client
async def handler(message, api_client):
    weapons = await api_client.get_all_weapons()
```

## 🎯 Следующие шаги

1. **Тестирование**: Протестируйте все функции бота
2. **Удаление старого кода**: Удалите помеченные файлы
3. **Обновление документации**: Обновите README.md
4. **Добавление новых фич**: Используйте новую архитектуру

## 📞 Вопросы?

Изучите:
- `services/` - вся бизнес-логика
- `api_clients/tarkov_api_client.py` - работа с API
- `main.py` - точка входа
- `pyproject.toml` - зависимости Poetry
- `docker-compose.yml` - конфигурация Docker

## ✨ Резюме

- **1 точка входа**: `main.py`
- **1 API клиент**: `TarkovAPIClient`
- **1 скрипт синхронизации**: `sync_data.py`
- **Чистая архитектура**: handlers → services → db/api
- **Готово к будущему**: легко расширять и поддерживать
