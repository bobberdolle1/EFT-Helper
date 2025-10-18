# ⚠️ Устаревшие файлы

После рефакторинга следующие файлы больше **НЕ ИСПОЛЬЗУЮТСЯ** и могут быть удалены:

## 🗑️ Удалить эти файлы:

### Утилиты (заменены на services/ и api_clients/)
- [ ] `utils/tarkov_api.py` → использовать `api_clients/tarkov_api_client.py`
- [ ] `utils/builds_fetcher.py` → функционал в `services/sync_service.py`
- [ ] `utils/build_calculator.py` → не используется, можно удалить

### Скрипты (объединены в sync_data.py)
- [ ] `scripts/sync_tarkov_data.py` → использовать `scripts/sync_data.py`
- [ ] `scripts/auto_sync_builds.py` → использовать `scripts/sync_data.py`
- [ ] `scripts/load_meta_builds.py` → устарел
- [ ] `scripts/load_quest_builds.py` → устарел
- [ ] `scripts/migrate_add_weapon_stats.py` → уже выполнена миграция
- [ ] `scripts/run_migration.py` → устарел
- [ ] `scripts/migrate.sql` → устарел

### Вспомогательные скрипты (опционально оставить)
- [ ] `scripts/check_db.py` → можно оставить для отладки
- [ ] `scripts/clean_db.py` → можно оставить для отладки
- [ ] `scripts/migrate_db.py` → можно оставить для миграций

## 📝 Как удалить безопасно:

```bash
# 1. Создайте резервную копию
git commit -am "Backup before cleanup"

# 2. Удалите устаревшие файлы
rm utils/tarkov_api.py
rm utils/builds_fetcher.py
rm utils/build_calculator.py
rm scripts/sync_tarkov_data.py

# 3. Проверьте что бот работает
poetry run python main.py
# или через Docker
docker-compose up

# 4. Зафиксируйте изменения
git commit -am "Removed deprecated files after refactoring"
```

## ⚠️ НЕ удаляйте:

- ✅ `start.py` - можно оставить для обратной совместимости
- ✅ `setup_complete.py` - может быть полезен
- ✅ `scripts/populate_db.py` - используется в `sync_data.py`
- ✅ `scripts/check_db.py` - полезен для отладки
- ✅ `scripts/clean_db.py` - полезен для отладки
- ✅ `pyproject.toml` - конфигурация Poetry
- ✅ `poetry.lock` - зафиксированные версии
- ✅ `docker-compose.yml` - конфигурация Docker
- ✅ `Dockerfile` - образ Docker

## 🔄 Миграция импортов

Если где-то в коде остались старые импорты, замените их:

### Старые импорты:
```python
from utils.tarkov_api import tarkov_api
from utils.builds_fetcher import BuildsFetcher
from utils.build_calculator import BuildCalculator
```

### Новые импорты:
```python
from api_clients import TarkovAPIClient
from services import SyncService, BuildService
```
