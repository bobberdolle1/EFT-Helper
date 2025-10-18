# 🎮 EFT Helper Bot

> Профессиональный Telegram-бот для игроков Escape from Tarkov

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![aiogram 3.15+](https://img.shields.io/badge/aiogram-3.15+-green.svg)](https://github.com/aiogram/aiogram)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> ⚡ **ОБНОВЛЕНО**: Бот был полностью рефакторен! Смотрите [REFACTORING_GUIDE.md](docs/REFACTORING_GUIDE.md) для деталей.

Полнофункциональный Telegram-бот для поиска оружия, сборок и управления билдами в Escape from Tarkov. Чистая модульная архитектура, централизованная работа с API, умный поиск и мультиязычность.

## 🆕 Что нового

- ✅ **Чистая архитектура**: Service Layer + централизованный API клиент
- ✅ **Единая точка входа**: `main.py` для запуска бота
- ✅ **Умное кэширование**: API запросы кэшируются на 24 часа
- ✅ **Нет дублирования**: весь код DRY
- ✅ **Готово к расширению**: легко добавлять новые функции

## ✨ Ключевые возможности

### 🔍 Поиск оружия (ОБНОВЛЕНО)
- **Поиск по категориям**: Быстрый выбор из 7 категорий оружия
- **Мультиязычный поиск**: Ищите по русским или английским названиям ("АС-ВАЛ" или "AS VAL")
- **Умный поиск**: Автоматическое исправление дефисов и пробелов

### 🤝 Сборки по лояльности (ПОЛНОСТЬЮ ПЕРЕРАБОТАНО)
- **Настройка уровней**: Укажите ваши текущие уровни лояльности к 8 торговцам
- **Умная фильтрация**: Бот показывает только доступные вам сборки
- **Сохранение профиля**: Уровни сохраняются в базе данных
- **Быстрое обновление**: Меняйте уровни в любое время

### 📜 Квестовые сборки
- Готовые сборки для выполнения квестов Оружейника
- Требования и альтернативные варианты
- Стоимость и доступность

### ⚔️ Мета-сборки 2025
- Актуальные топовые сборки
- Разделение по категориям оружия
- Статистика и характеристики

### ⭐ Рейтинг оружия
- Tier-листы по категориям (S, A, B, C, D)
- Группировка по типам оружия
- Актуальная мета информация

### 🌐 Интеграция с tarkov.dev API
- Актуальные данные об оружии
- Рыночные цены с Flea Market
- Информация о торговцах
- Автоматическое кэширование

### ⚙️ Двуязычность
- Полная поддержка русского и английского
- Переключение языка в настройках
- Локализация всех интерфейсов

---

## 📋 Требования

- **Python:** 3.9 или выше
- **Poetry:** Менеджер зависимостей (установите через `pip install poetry`)
- **Telegram Bot Token:** Получите у [@BotFather](https://t.me/BotFather)
- **Операционная система:** Windows, Linux, macOS
- **Интернет:** Для работы с API

## 🚀 Быстрый старт

> 📖 Подробнее: [docs/QUICKSTART.md](docs/QUICKSTART.md)

### Способ 1: Docker (рекомендуется для production)

```bash
# 1. Настройте .env файл
cp .env.example .env
# Отредактируйте .env и добавьте BOT_TOKEN

# 2. Запустите через Docker Compose
docker-compose up -d
```

### Способ 2: Poetry (для разработки)

```bash
# 1. Установите зависимости
poetry install

# 2. Запустите бота
poetry run python main.py
```

Скрипт `start.py` автоматически:
- ✅ Проверит наличие `.env` файла и создаст его при необходимости
- ✅ Инициализирует базу данных
- ✅ Предложит заполнить базу тестовыми данными или синхронизировать с tarkov.dev API
- ✅ Запустит бота

**Важно:** При первом запуске укажите ваш Bot Token от [@BotFather](https://t.me/BotFather) в файле `.env`

---

## 📋 Ручная установка

### 1. Клонируйте репозиторий

```bash
git clone <repository-url>
cd "EFT Helper"
```

### 2. Установите зависимости

```bash
poetry install
```

Poetry автоматически создаст виртуальное окружение и установит все зависимости.

### 3. Активируйте окружение (опционально)

```bash
poetry shell
```

### 4. Настройте окружение

Создайте файл `.env` на основе `.env.example`:

```bash
copy .env.example .env
```

Отредактируйте `.env` и добавьте ваш Telegram Bot Token:

```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=123456789,987654321
```

### 5. Заполните базу данных

**Вариант A: Тестовые данные (быстро)**
```bash
poetry run python scripts/populate_db.py
```

**Вариант B: Синхронизация с tarkov.dev API (актуальные данные)**
```bash
poetry run python scripts/sync_tarkov_data.py
```

### 6. Запустите бота

```bash
poetry run python start.py
```

---

## 📁 Структура проекта

```plaintext
EFT Helper/
│
├── 📁 database/              # База данных
│   ├── __init__.py
│   ├── models.py            # Модели данных
│   ├── db.py                # Операции с БД
│   └── config.py            # Конфигурация
│
├── 📁 handlers/              # Обработчики команд
│   ├── common.py            # /start, меню
│   ├── search.py            # Поиск оружия
│   ├── builds.py            # Сборки
│   ├── loyalty.py           # Лояльность
│   ├── tier_list.py         # Рейтинги
│   └── settings.py          # Настройки
│
├── 📁 keyboards/             # Клавиатуры
│   ├── inline.py            # Inline кнопки
│   └── reply.py             # Reply кнопки
│
├── 📁 localization/          # Переводы
│   └── texts.py             # RU/EN тексты
│
├── 📁 utils/                 # Утилиты
│   ├── formatters.py        # Форматирование
│   └── tarkov_api.py        # API клиент
│
├── 📁 scripts/               # Вспомогательные скрипты
│   ├── populate_db.py       # Тестовые данные
│   ├── sync_tarkov_data.py  # Синхронизация API
│   ├── check_db.py          # Проверка БД
│   └── migrate_db.py        # Миграции
│
├── 📁 docs/                  # Документация
│   ├── API_INTEGRATION.md   # API гайд
│   ├── USER_GUIDE.md        # Руководство
│   └── CHANGELOG.md         # История изменений
│
├── 📁 data/                  # Данные (gitignored)
│   └── eft_helper.db        # База данных SQLite
│
├── 📄 start.py               # 🚀 Единственная точка входа
├── 📄 pyproject.toml         # Конфигурация Poetry
├── 📄 poetry.lock            # Зафиксированные версии зависимостей
├── 📄 requirements.txt       # Зависимости (legacy, для совместимости)
├── 📄 .env.example           # Пример конфигурации
├── 📄 .gitignore
└── 📄 README.md              # Документация
```

## 🗄️ Структура базы данных

### Таблицы:

- **weapons** - Оружие (название, категория, tier, цена)
- **modules** - Модули/аттачменты (название, цена, торговец, лояльность)
- **builds** - Сборки оружия (категория, модули, стоимость)
- **quests** - Квесты с требованиями к сборкам
- **traders** - Торговцы (имя, эмодзи)
- **users** - Пользователи бота (язык, избранное)

## 🎮 Использование

### Команды бота:

- `/start` - Запустить бота и открыть главное меню

### Основной функционал

#### 🔍 Поиск оружия
```
1. Выберите категорию или введите название
2. Выберите оружие из списка
3. Выберите тип сборки (Meta/Quest/Random)
4. Получите готовую сборку с модулями и ценами
```

#### 🤝 Настройка лояльности
```
1. Откройте "Сборки по лояльности"
2. Выберите каждого торговца
3. Установите ваш текущий уровень (1-4)
4. Просмотрите доступные сборки
```

#### ⭐ Tier-листы
```
1. Выберите "Лучшее оружие"
2. Выберите tier (S/A/B/C/D)
3. Просмотрите рейтинг по категориям
```

---

## 🔧 Разработка

### Запуск в режиме разработки

```bash
# Установите зависимости (включая dev-зависимости)
poetry install

# Активируйте окружение
poetry shell

# Запустите бота
poetry run python start.py

# Или запустите без активации окружения
poetry run python start.py
```

### Структура базы данных

```sql
-- Оружие
CREATE TABLE weapons (
    id INTEGER PRIMARY KEY,
    name_ru TEXT,
    name_en TEXT,
    category TEXT,
    tier_rating TEXT,
    base_price INTEGER
);

-- Модули
CREATE TABLE modules (
    id INTEGER PRIMARY KEY,
    name_ru TEXT,
    name_en TEXT,
    price INTEGER,
    trader TEXT,
    loyalty_level INTEGER,
    slot_type TEXT
);

-- Сборки
CREATE TABLE builds (
    id INTEGER PRIMARY KEY,
    weapon_id INTEGER,
    category TEXT,
    name_ru TEXT,
    name_en TEXT,
    total_cost INTEGER,
    min_loyalty_level INTEGER,
    modules TEXT,  -- JSON массив ID модулей
    planner_link TEXT
);

-- Пользователи
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    language TEXT,
    favorite_builds TEXT,
    trader_levels TEXT  -- JSON уровней лояльности
);
```

### Добавление новых сборок

```python
from database import Database, BuildCategory
import json

async def add_custom_build():
    db = Database("eft_helper.db")
    
    await db.execute(
        """INSERT INTO builds (weapon_id, category, name_ru, name_en, 
           total_cost, min_loyalty_level, modules, planner_link)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (1, BuildCategory.META.value, "Моя сборка", "My Build",
         150000, 3, json.dumps([1, 2, 3]), "https://link")
    )
```

---

## 🔌 API Интеграция

### Tarkov.dev API
```python
from utils.tarkov_api import tarkov_api

# Получить все оружие
weapons = await tarkov_api.get_all_weapons()

# Получить цены
prices = await tarkov_api.get_market_prices()
```

### Синхронизация данных
```bash
# Загрузить ВСЕ данные из API
poetry run python scripts/sync_tarkov_data.py

# Результат: 150+ оружий, 1000+ модулей
```

Подробнее: [docs/API_INTEGRATION.md](docs/API_INTEGRATION.md)

---

## 📚 Документация

- 📖 [Руководство пользователя](docs/USER_GUIDE.md)
- 🔌 [API Интеграция](docs/API_INTEGRATION.md)
- 📝 [Changelog](CHANGELOG.md)

---

## 🛠️ Использование

### Команды бота:

- `/start` - Запустить бота и открыть главное меню

---

## 📄 Лицензия

MIT License

## 🚧 Roadmapа

Проект разработан для помощи игрокам Escape from Tarkov в изучении и создании оптимальных сборок оружия.

---
