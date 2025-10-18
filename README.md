# 🎮 EFT Helper Bot

> Профессиональный Telegram-бот для игроков Escape from Tarkov

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![aiogram 3.15+](https://img.shields.io/badge/aiogram-3.15+-green.svg)](https://github.com/aiogram/aiogram)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Полнофункциональный Telegram-бот для игроков Escape from Tarkov. Поиск оружия, готовые сборки, интеграция с tarkov.dev API, мультиязычность и удобное управление через Docker.

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

> 📖 **Полная документация**: [docs/README.md](docs/README.md) | [docs/QUICKSTART.md](docs/QUICKSTART.md)

### 🎯 Способ 1: Management Scripts (рекомендуется)

Используйте удобные скрипты управления с интерактивным меню:

**Windows:**
```cmd
manage.bat
```

**Linux/Mac:**
```bash
chmod +x manage.sh
./manage.sh
```

> 🛠️ **Документация**: [docs/MANAGEMENT_SCRIPTS.md](docs/MANAGEMENT_SCRIPTS.md)

Меню включает все необходимые функции:
- ✅ Запуск/остановка/перезапуск бота
- ✅ Просмотр логов и статуса
- ✅ Тестирование API подключения
- ✅ Резервное копирование БД
- ✅ Пересборка Docker образа
- ✅ Очистка Docker кэша
- ✅ И ещё 12+ функций!

### 🐳 Способ 2: Docker

> 📖 **Подробная документация**: [docs/DOCKER.md](docs/DOCKER.md)

```bash
# 1. Настройте .env файл
cp .env.example .env
# Отредактируйте .env и укажите BOT_TOKEN

# 2. Запустите через Docker Compose
docker-compose up -d

# 3. Проверьте статус
docker-compose ps

# 4. Просмотрите логи
docker-compose logs -f
```

### 🔧 Способ 3: Poetry (для разработки)

```bash
# 1. Установите зависимости
poetry install

# 2. Настройте .env
cp .env.example .env
# Отредактируйте .env и укажите BOT_TOKEN

# 3. Запустите бота
poetry run python main.py
```

**Важно:** Получите Bot Token у [@BotFather](https://t.me/BotFather) и укажите в `.env`

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
├── 📁 api_clients/           # API клиенты
│   └── tarkov_api_client.py # Централизованный клиент tarkov.dev
│
├── 📁 services/              # Бизнес-логика
│   ├── weapon_service.py    # Логика работы с оружием
│   ├── build_service.py     # Логика работы со сборками
│   ├── user_service.py      # Логика работы с пользователями
│   ├── sync_service.py      # Синхронизация с API
│   └── random_build_service.py  # Генерация случайных сборок
│
├── 📁 handlers/              # Обработчики команд
│   ├── common.py            # /start, меню
│   ├── search.py            # Поиск оружия
│   ├── builds.py            # Сборки
│   ├── loyalty.py           # Лояльность торговцев
│   ├── tier_list.py         # Tier-рейтинги
│   └── settings.py          # Настройки языка
│
├── 📁 database/              # База данных
│   ├── models.py            # Модели данных (dataclasses)
│   ├── db.py                # Операции с БД
│   └── config.py            # Конфигурация
│
├── 📁 keyboards/             # Telegram клавиатуры
│   ├── inline.py            # Inline кнопки
│   └── reply.py             # Reply кнопки
│
├── 📁 localization/          # Мультиязычность
│   └── texts.py             # RU/EN тексты
│
├── 📁 utils/                 # Утилиты
│   ├── constants.py         # Константы проекта
│   └── formatters.py        # Форматирование вывода
│
├── 📁 scripts/               # Вспомогательные скрипты
│   ├── sync_data.py         # Синхронизация данных
│   ├── check_db.py          # Проверка БД
│   ├── clean_db.py          # Очистка БД
│   └── migrate_db.py        # Миграции БД
│
├── 📁 docs/                  # Документация
│   ├── README.md            # 📚 Навигация по документации
│   ├── QUICKSTART.md        # Быстрый старт
│   ├── DOCKER.md            # Docker руководство
│   ├── MANAGEMENT_SCRIPTS.md # Скрипты управления
│   ├── ARCHITECTURE.md      # Архитектура проекта
│   ├── API_INTEGRATION.md   # Интеграция с API
│   ├── USER_GUIDE.md        # Руководство пользователя
│   ├── QUICK_COMMANDS.md    # Шпаргалка команд
│   └── CHANGELOG.md         # История изменений
│
├── 📁 data/                  # Данные (gitignored)
│   └── eft_helper.db        # База данных SQLite
│
├── 📁 logs/                  # Логи (gitignored)
│   └── bot.log              # Логи приложения
│
├── 📄 main.py                # 🚀 Точка входа
├── 📄 start.py               # Альтернативная точка входа
├── 📄 manage.bat             # Скрипт управления (Windows)
├── 📄 manage.sh              # Скрипт управления (Linux/Mac)
├── 📄 docker-compose.yml     # Docker Compose конфигурация
├── 📄 Dockerfile             # Docker образ
├── 📄 pyproject.toml         # Конфигурация Poetry
├── 📄 poetry.lock            # Зафиксированные версии
├── 📄 .env.example           # Пример конфигурации
├── 📄 .gitignore             # Git ignore правила
└── 📄 README.md              # Этот файл
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

> 📖 **Полная навигация**: [docs/README.md](docs/README.md)

### Для пользователей:
- 🚀 [Быстрый старт](docs/QUICKSTART.md) - пошаговое руководство по запуску
- 📱 [Руководство пользователя](docs/USER_GUIDE.md) - как использовать бота
- ⚡ [Быстрые команды](docs/QUICK_COMMANDS.md) - шпаргалка

### Для администраторов:
- 🐳 [Docker руководство](docs/DOCKER.md) - развертывание через Docker
- 🛠️ [Скрипты управления](docs/MANAGEMENT_SCRIPTS.md) - manage.bat/manage.sh

### Для разработчиков:
- 🏗️ [Архитектура](docs/ARCHITECTURE.md) - структура проекта
- 🔌 [API интеграция](docs/API_INTEGRATION.md) - работа с tarkov.dev
- 📝 [История изменений](docs/CHANGELOG.md) - changelog

---

## 🤝 Вклад в проект

Проект открыт для вклада! Создавайте issue и pull request'ы.

---

## 📄 Лицензия

MIT License

---

**Сделано с ❤️ для сообщества Escape from Tarkov**
