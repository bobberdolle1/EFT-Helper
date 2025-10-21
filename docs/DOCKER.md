# 🐳 Docker - Руководство по развертыванию

> Полное руководство по запуску EFT Helper Bot в Docker контейнере

## 📋 Содержание

- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
- [Использование скриптов](#использование-скриптов)
- [Ручной запуск](#ручной-запуск)
- [Управление контейнером](#управление-контейнером)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Требования

### Обязательно:
- **Docker Desktop** 20.10+ или Docker Engine
- **Docker Compose** 2.0+
- Минимум **512MB** свободной RAM
- Минимум **1GB** свободного места на диске

> 💡 **Полная поддержка AI в Docker!**
> 
> Docker-образ включает:
> - ✅ **faster-whisper** для голосовых сообщений
> - ✅ **Подключение к Ollama** на хосте через `host.docker.internal`
> - ✅ **Все AI-функции**: генерация сборок, текстовый ассистент, голосовой ввод
> - ✅ **Полная локализация** RU/EN
> 
> **Требования для AI:**
> - Ollama должен быть установлен и запущен на хосте: `ollama serve`
> - Модель qwen3:8b должна быть загружена: `ollama pull qwen3:8b`

### Проверка установки:
```bash
docker --version
docker-compose --version
```

Если Docker не установлен:
- **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

---

## 🚀 Быстрый старт

### Windows

1. **Настройте .env файл**
```batch
copy .env.example .env
notepad .env
```
Укажите ваш `BOT_TOKEN` от [@BotFather](https://t.me/BotFather)

2. **Запустите скрипт управления**
```batch
manage.bat
```

3. **Выберите функцию запуска бота из меню**

### Linux/Mac

1. **Сделайте скрипт исполняемым**
```bash
chmod +x run.sh
```

2. **Настройте .env файл**
```bash
cp .env.example .env
nano .env  # или vim, или другой редактор
```
Укажите ваш `BOT_TOKEN` от [@BotFather](https://t.me/BotFather)

3. **Запустите скрипт управления**
```bash
./manage.sh
```

4. **Выберите функцию запуска бота из меню**

---

## 📜 Использование скриптов

### Windows (manage.bat)

```batch
manage.bat
```
Откроется интерактивное меню с функциями:
- Запуск/остановка/перезапуск бота
- Просмотр логов и статуса
- Тестирование API и БД
- Синхронизация данных
- Резервное копирование
- И другие административные функции

> 📖 **Подробнее**: [MANAGEMENT_SCRIPTS.md](MANAGEMENT_SCRIPTS.md)

### Linux/Mac (manage.sh)

```bash
chmod +x manage.sh
./manage.sh
```

Аналогичное интерактивное меню для Linux/Mac систем.

---

## 🔧 Ручной запуск

Если вы предпочитаете использовать Docker напрямую:

### 1. Создайте .env файл
```bash
cp .env.example .env
# Отредактируйте .env и укажите BOT_TOKEN
```

### 2. Запустите бота
```bash
docker-compose up -d
```

### 3. Проверьте статус
```bash
docker-compose ps
```

### 4. Просмотрите логи
```bash
docker-compose logs -f
```

### 5. Остановите бота
```bash
docker-compose down
```

---

## 🛠️ Управление контейнером

### Основные команды

#### Запуск
```bash
docker-compose up -d
```
Флаг `-d` запускает в фоновом режиме (detached mode)

#### Остановка
```bash
docker-compose down
```

#### Перезапуск
```bash
docker-compose restart
```

#### Просмотр логов
```bash
# Последние 100 строк с авто-обновлением
docker-compose logs -f --tail=100

# Все логи
docker-compose logs

# Только последние 50 строк
docker-compose logs --tail=50
```

#### Статус контейнера
```bash
docker-compose ps
```

#### Использование ресурсов
```bash
docker stats eft-helper-bot
```

### Продвинутые команды

#### Пересборка образа
```bash
# Остановить контейнер
docker-compose down

# Пересобрать без кэша
docker-compose build --no-cache

# Запустить заново
docker-compose up -d
```

#### Вход в контейнер
```bash
# Через docker-compose
docker-compose exec eft-helper-bot /bin/bash

# Напрямую через docker
docker exec -it eft-helper-bot /bin/bash
```

#### Полная очистка
```bash
# Остановить и удалить контейнеры + volumes
docker-compose down -v

# Удалить образы
docker-compose down --rmi all

# Очистка неиспользуемых образов
docker system prune -a
```

---

## 📊 Мониторинг

### Проверка работы бота

1. **Проверьте логи на ошибки:**
```bash
docker-compose logs | grep -i error
```

2. **Проверьте состояние контейнера:**
```bash
docker-compose ps
```
Статус должен быть `Up`

3. **Проверьте использование ресурсов:**
```bash
docker stats --no-stream eft-helper-bot
```

4. **Healthcheck:**
```bash
docker inspect --format='{{json .State.Health}}' eft-helper-bot | jq
```

### Настройка логирования

В `docker-compose.yml` уже настроено:
- Максимальный размер файла: 10MB
- Количество файлов: 3
- Формат: JSON

Изменить можно в секции `logging`:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"  # Изменить размер
    max-file: "3"     # Изменить количество файлов
```

---

## 🔄 Обновление бота

### Способ 1: Пересборка образа
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Способ 2: Через скрипт управления
**Windows:**
```batch
manage.bat
# Выбрать соответствующую функцию из меню
```

**Linux/Mac:**
```bash
./manage.sh
# Выбрать соответствующую функцию из меню
```

---

## 💾 Управление данными

### Структура volumes

```yaml
volumes:
  - ./data:/app/data    # База данных SQLite
  - ./logs:/app/logs    # Логи приложения
```

### Бэкап базы данных

**Windows:**
```batch
copy data\eft_helper.db data\eft_helper.db.backup
```

**Linux/Mac:**
```bash
cp data/eft_helper.db data/eft_helper.db.backup
```

### Восстановление базы данных

1. Остановите бота:
```bash
docker-compose down
```

2. Замените файл базы данных:
```bash
cp data/eft_helper.db.backup data/eft_helper.db
```

3. Запустите бота:
```bash
docker-compose up -d
```

---

## ⚙️ Настройка окружения

### Файл .env

```env
# Обязательные параметры
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=123456789,987654321

# Опциональные параметры
# DB_PATH=/app/data/eft_helper.db
# LOG_LEVEL=INFO
```

### Переменные окружения в docker-compose.yml

Можно добавить дополнительные переменные:
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - LOG_LEVEL=DEBUG
  - TZ=Europe/Moscow
```

---

## 🐛 Troubleshooting

### Бот не запускается

**Проблема:** Контейнер постоянно перезапускается

**Решение:**
1. Проверьте логи:
```bash
docker-compose logs --tail=50
```

2. Проверьте .env файл:
```bash
cat .env | grep BOT_TOKEN
```

3. Убедитесь, что токен валидный

---

### База данных пустая

**Проблема:** База данных не инициализируется

**Решение:**
1. Войдите в контейнер:
```bash
docker-compose exec eft-helper-bot /bin/bash
```

2. Запустите скрипт заполнения:
```bash
python scripts/populate_db.py
```

3. Или синхронизируйте с API:
```bash
python scripts/sync_tarkov_data.py
```

---

### Проблемы с сетью

**Проблема:** Бот не может подключиться к Telegram API

**Решение:**
1. Проверьте сетевые настройки Docker:
```bash
docker network ls
docker network inspect bridge
```

2. Проверьте DNS:
```bash
docker-compose exec eft-helper-bot ping -c 4 google.com
```

3. Перезапустите Docker Desktop или Docker daemon

---

### Недостаточно памяти

**Проблема:** OOMKilled в логах

**Решение:**
Увеличьте лимиты в `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 1G  # Увеличить с 512M
```

---

### Права доступа (Linux)

**Проблема:** Permission denied для data/ или logs/

**Решение:**
```bash
sudo chown -R $USER:$USER data logs
chmod -R 755 data logs
```

Или запустите с sudo:
```bash
sudo docker-compose up -d
```

---

## 📝 Полезные команды

### Очистка Docker

```bash
# Удалить неиспользуемые образы
docker image prune -a

# Удалить неиспользуемые контейнеры
docker container prune

# Удалить неиспользуемые volumes
docker volume prune

# Полная очистка системы
docker system prune -a --volumes
```

### Экспорт/Импорт образа

**Экспорт:**
```bash
docker save eft-helper-bot:latest | gzip > eft-helper-bot.tar.gz
```

**Импорт:**
```bash
docker load < eft-helper-bot.tar.gz
```

---

## 🔐 Безопасность

### Рекомендации:

1. **Никогда не коммитьте .env файл** в Git
2. **Используйте .env.example** как шаблон
3. **Регулярно обновляйте** базовый образ Python
4. **Ограничивайте ресурсы** контейнера
5. **Проверяйте логи** на подозрительную активность

### Обновление зависимостей

```bash
# Пересобрать образ с новыми зависимостями
docker-compose build --no-cache --pull
```

---

## 📚 Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## 💡 Советы

1. **Используйте скрипты управления** (`manage.bat` или `manage.sh`) для удобства
2. **Регулярно делайте бэкапы** базы данных
3. **Проверяйте логи** при возникновении проблем
4. **Обновляйте образ** при изменении кода
5. **Используйте `docker-compose`** вместо прямых docker команд

---

**Готово! 🎉**

Теперь ваш EFT Helper Bot работает в Docker контейнере с полной изоляцией и легким управлением!
