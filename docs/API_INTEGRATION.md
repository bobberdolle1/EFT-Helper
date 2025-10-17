# API Интеграция

## Обзор

EFT Helper использует несколько API для получения актуальных данных об игре Escape from Tarkov:

## 🌐 Доступные API

### 1. Tarkov.dev GraphQL API
**URL:** `https://api.tarkov.dev/graphql`
**Тип:** GraphQL
**Требуется ключ:** Нет

**Возможности:**
- ✅ Получение всех оружий и их характеристик
- ✅ Список торговцев и их уровни лояльности
- ✅ Информация о модулях и модификациях
- ✅ Рыночные цены с Flea Market
- ✅ Данные о патронах и броне
- ✅ Совместимые модули для оружия

**Пример использования:**
```python
from utils.tarkov_api import tarkov_api

# Получить все оружие
weapons = await tarkov_api.get_all_weapons()

# Получить торговцев
traders = await tarkov_api.get_traders()

# Получить рыночные цены
prices = await tarkov_api.get_market_prices()
```

### 2. Tarkov Market API
**URL:** `https://api.tarkov-market.com/api/v1`
**Тип:** REST
**Требуется ключ:** Да (опционально)

**Возможности:**
- 📊 Актуальные рыночные цены
- 📈 Статистика цен за период
- 🔍 Поиск предметов
- 💰 История сделок

**Получение API ключа:**
1. Зарегистрируйтесь на https://tarkov-market.com
2. Получите бесплатный API ключ в профиле
3. Добавьте в `.env`: `TARKOV_MARKET_KEY=ваш_ключ`

**Пример использования:**
```python
from utils.tarkov_api import TarkovAPI

# Инициализация с ключом
api = TarkovAPI(market_api_key="ваш_ключ")

# Получить все предметы
items = await api.get_all_items_from_market()

# Получить цену предмета
price = await api.get_item_price_from_market("item_uid")
```

## 📝 Кэширование

Все данные кэшируются на **24 часа** для снижения нагрузки на API и ускорения работы бота.

```python
# Кэш автоматически проверяется при каждом запросе
weapons = await tarkov_api.get_all_weapons()  # Первый раз - запрос к API
weapons = await tarkov_api.get_all_weapons()  # Второй раз - из кэша
```

## 🔄 Синхронизация данных

### Автоматическая синхронизация
При первом запуске бота через `start.py` данные загружаются автоматически.

### Ручная синхронизация
```bash
# Загрузить ВСЕ данные из tarkov.dev
poetry run python scripts/sync_tarkov_data.py

# Заполнить тестовыми данными
poetry run python scripts/populate_db.py
```

## 📊 Структура данных

### Оружие
```python
{
    "id": "weapon_id",
    "name": "M4A1",
    "shortName": "M4A1",
    "category": "assault_rifle",
    "avg24hPrice": 65000,
    "properties": {
        "caliber": "5.56x45mm",
        "ergonomics": 45,
        "recoilVertical": 85,
        "fireRate": 800
    }
}
```

### Модули
```python
{
    "id": "module_id",
    "name": "Daniel Defense RIS II",
    "shortName": "RIS II",
    "avg24hPrice": 45000,
    "types": ["mod"]
}
```

### Торговцы
```python
{
    "id": "trader_id",
    "name": "Mechanic",
    "levels": [
        {
            "level": 1,
            "requiredPlayerLevel": 10,
            "requiredReputation": 0
        }
    ]
}
```

## ⚠️ Ограничения

### Tarkov.dev
- **Rate Limit:** Нет жесткого лимита, но рекомендуется кэширование
- **Доступность:** 99% uptime
- **Задержка:** ~200-500ms на запрос

### Tarkov Market
- **Rate Limit:** 100 запросов/минуту (бесплатный тарифf)
- **Требуется регистрация:** Да
- **API ключ обновляется:** Каждые 30 дней

## 🔮 Будущие интеграции

Планируется добавить:
- 🎯 **tarkov-tools.com** - готовые билды и рекомендации
- 🗺️ **tarkov-ballistics** - расчет урона и пробития
- 📱 **Battle Buddy API** - мобильные данные
- 🏪 **Tarkov Database** - русские переводы

## 🐛 Обработка ошибок

```python
try:
    weapons = await tarkov_api.get_all_weapons()
    if not weapons:
        print("API недоступен, используем кэш")
except Exception as e:
    print(f"Ошибка API: {e}")
    # Fallback к локальным данным
```

## 📚 Дополнительные ресурсы

- [Tarkov.dev Documentation](https://tarkov.dev/api/)
- [Tarkov Market API Docs](https://tarkov-market.com/dev/api)
- [GraphQL Playground](https://api.tarkov.dev/graphql)
