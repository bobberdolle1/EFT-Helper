# 🚀 Quick Start Guide - EFT Helper Bot

## Обновлённая версия (После рефакторинга)

### ⚡ Вариант A: Docker (Production)

#### 1. Подготовка
```bash
# Создайте .env из примера
cp .env.example .env

# Отредактируйте .env
nano .env  # или любой редактор
# Укажите: BOT_TOKEN=ваш_токен_от_BotFather
```

#### 2. Запуск
```bash
# Соберите и запустите
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot

# Остановка
docker-compose down
```

### ⚡ Вариант B: Poetry (Development)

#### 1. Установите зависимости
```bash
# Poetry установит виртуальное окружение автоматически
poetry install
```

#### 2. Настройте .env
```bash
cp .env.example .env
# Отредактируйте и добавьте BOT_TOKEN
```

#### 3. Запустите бота
```bash
# Через Poetry (рекомендуется)
poetry run python main.py

# Или активируйте окружение и запускайте напрямую
poetry shell
python main.py
```

---

## 📦 Первоначальная настройка данных

### Вариант A: Синхронизация с tarkov.dev API (рекомендуется)

```bash
# Через Poetry
poetry run python scripts/sync_data.py
# Выберите: 1 - Синхронизация с API

# Или через Docker
docker-compose exec bot python scripts/sync_data.py
```

Загрузит:
- ✅ 150+ реальных оружий
- ✅ 1000+ модулей
- ✅ Актуальные цены
- ✅ Информацию о торговцах

### Вариант B: Тестовые данные (быстро)

```bash
# Через Poetry
poetry run python scripts/sync_data.py
# Выберите: 2 - Тестовые данные

# Или через Docker
docker-compose exec bot python scripts/sync_data.py
```

Создаст:
- ✅ 14 оружий
- ✅ 19 модулей
- ✅ 6 готовых сборок
- ✅ 8 торговцев

### Вариант C: Оба варианта

```bash
poetry run python scripts/sync_data.py
# Выберите: 3 - Оба варианта
```

---

## 📁 Новая структура

```
EFT Helper/
├── main.py                    # ⭐ Запускайте отсюда!
├── api_clients/               # 🌐 Централизованные API
│   └── tarkov_api_client.py  
├── services/                  # 💼 Бизнес-логика
│   ├── weapon_service.py
│   ├── build_service.py
│   ├── user_service.py
│   └── sync_service.py
├── handlers/                  # 🎮 Обработчики (обновлены)
├── database/                  # 💾 База данных
└── scripts/
    └── sync_data.py          # 🔄 Единый скрипт синхронизации
```

---

## 🔧 Разработка

### Добавление нового функционала

#### 1. Создайте service (если нужна логика)
```python
# services/my_service.py
class MyService:
    def __init__(self, db, api_client):
        self.db = db
        self.api = api_client
    
    async def do_something(self):
        # Ваша логика
        pass
```

#### 2. Зарегистрируйте в main.py
```python
# main.py
self.my_service = MyService(self.db, self.api_client)

# В middleware
data["my_service"] = self.my_service
```

#### 3. Используйте в handler
```python
# handlers/my_handler.py
@router.message(Command("mycommand"))
async def my_handler(message, my_service):
    result = await my_service.do_something()
    await message.answer(result)
```

---

## 🐛 Отладка

### Проверка базы данных
```bash
# Через Poetry
poetry run python scripts/check_db.py

# Через Docker
docker-compose exec bot python scripts/check_db.py
```

### Очистка базы данных
```bash
poetry run python scripts/clean_db.py
# или
docker-compose exec bot python scripts/clean_db.py
```

### Просмотр логов
```bash
# Логи в консоли и в logs/bot.log
tail -f logs/bot.log
```

---

## ❓ FAQ

### Q: Где старые скрипты?
**A:** Объединены в `scripts/sync_data.py`. См. [docs/DEPRECATED_FILES.md](DEPRECATED_FILES.md) для деталей.

### Q: Как обновить данные из API?
**A:** Запустите `poetry run python scripts/sync_data.py` → выберите вариант 1

### Q: Где вся логика?
**A:** В папке `services/`. Handlers только координируют.

### Q: Можно ли использовать start.py?
**A:** Да, но рекомендуется `main.py` для чистоты.

### Q: Как работает кэширование?
**A:** `TarkovAPIClient` автоматически кэширует на 24 часа.

---

## 📚 Документация

- [REFACTORING_GUIDE.md](REFACTORING_GUIDE.md) - Что изменилось
- [ARCHITECTURE.md](ARCHITECTURE.md) - Архитектура
- [DEPRECATED_FILES.md](DEPRECATED_FILES.md) - Устаревшие файлы
- [../README.md](../README.md) - Полное описание

---

## ✅ Checklist для разработчиков

После рефакторинга:

- [ ] Прочитайте `REFACTORING_GUIDE.md`
- [ ] Удалите устаревшие файлы (см. `DEPRECATED_FILES.md`)
- [ ] Протестируйте все команды бота
- [ ] Обновите свои кастомные handlers (используйте services)
- [ ] Удалите старые импорты `from utils.tarkov_api`

---

## 🎯 Основные правила

1. **НЕ** делайте HTTP запросы напрямую → используйте `api_client`
2. **НЕ** пишите логику в handlers → используйте `services`
3. **НЕ** дублируйте код → создавайте переиспользуемые методы
4. **ВСЕГДА** используйте dependency injection через middleware

---

## 🚀 Готово!

Теперь ваш бот:
- ✅ Чистый и модульный
- ✅ Легко тестируется
- ✅ Готов к расширению
- ✅ Следует лучшим практикам

Запустите `python main.py` и наслаждайтесь! 🎉
