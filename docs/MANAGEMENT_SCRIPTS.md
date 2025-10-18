# 🛠️ Management Scripts Guide

Удобные скрипты для управления EFT Helper Bot через интерактивное меню.

## 📋 Доступные скрипты

### Windows: `manage.bat`
Для запуска в Windows просто дважды кликните на файл или запустите из командной строки:

```cmd
manage.bat
```

### Linux/Mac: `manage.sh`
Для запуска в Linux/Mac сначала сделайте файл исполняемым:

```bash
chmod +x manage.sh
./manage.sh
```

## 🎯 Функции меню

### Основное управление (1-10)

**[1] Start bot (Docker)**
- Запускает бота в Docker контейнере
- Команда: `docker-compose up -d`

**[2] Stop bot**
- Останавливает бота
- Команда: `docker-compose stop`

**[3] Restart bot**
- Перезапускает бота
- Команда: `docker-compose restart`

**[4] View logs (real-time)**
- Показывает логи в реальном времени
- Для выхода нажмите Ctrl+C
- Команда: `docker-compose logs -f`

**[5] View logs (last 50 lines)**
- Показывает последние 50 строк логов
- Команда: `docker-compose logs --tail=50`

**[6] Check status**
- Проверяет статус контейнера и health check
- Команда: `docker-compose ps`

**[7] Rebuild Docker image**
- Пересобирает Docker образ с нуля
- Спрашивает хотите ли вы запустить бота после сборки
- Команды: `docker-compose down` → `docker-compose build --no-cache`

**[8] Update and restart**
- Полный цикл обновления:
  1. Останавливает бота
  2. Пересобирает образ
  3. Запускает бота
- Используйте после изменений в коде

**[9] Stop and remove containers**
- Останавливает и удаляет контейнер
- **Важно:** База данных и логи сохраняются
- Команда: `docker-compose down`

**[10] View resource usage**
- Показывает использование CPU, памяти, сети
- Команда: `docker stats --no-stream eft-helper-bot`

### Утилиты и тесты (11-15)

**[11] Test API connection**
- Тестирует подключение к tarkov.dev API
- Загружает и показывает статистику квестов
- Скрипт: `scripts/test_quests_api.py`

**[12] Reset Telegram webhook**
- Сбрасывает webhook бота
- Используйте при конфликтах polling
- Скрипт: `scripts/reset_webhook.py`

**[13] Backup database**
- Создает резервную копию базы данных
- Сохраняет в `backup/eft_helper_YYYYMMDD_HHMMSS.db`
- Автоматически создает директорию backup

**[14] Run local (Poetry)**
- Запускает бота локально через Poetry
- Автоматически останавливает Docker версию
- Команда: `poetry run python main.py`

**[15] Install dependencies (Poetry)**
- Устанавливает/обновляет зависимости
- Команда: `poetry install`

### Docker утилиты (16-18)

**[16] Clean Docker cache**
- Очищает:
  - Остановленные контейнеры
  - Неиспользуемые сети
  - "Висящие" образы (dangling)
  - Build cache
- Команда: `docker system prune -f`

**[17] View Docker images**
- Показывает все Docker образы проекта
- Команда: `docker images | grep efthelper`

**[18] Shell into container**
- Открывает bash терминал внутри контейнера
- Для отладки и инспекции
- Команда: `docker-compose exec eft-helper-bot bash`

## 📖 Примеры использования

### Первый запуск

1. Запустите скрипт: `manage.bat` (Windows) или `./manage.sh` (Linux/Mac)
2. Выберите **[1]** для запуска бота
3. Выберите **[6]** для проверки статуса
4. Выберите **[4]** для просмотра логов

### Обновление после изменения кода

1. Запустите скрипт
2. Выберите **[8]** - Update and restart
3. Дождитесь завершения сборки
4. Выберите **[4]** для проверки логов

### Отладка проблем

1. Выберите **[6]** - Check status
2. Выберите **[5]** - View logs (last 50 lines)
3. Если нужно - выберите **[18]** для входа в контейнер
4. Если проблема с API - выберите **[11]** для теста

### Резервное копирование

1. Выберите **[13]** - Backup database
2. Файл будет сохранен в `backup/`
3. Можно восстановить скопировав обратно в `data/`

### Очистка Docker

После многих пересборок:
1. Выберите **[16]** - Clean Docker cache
2. Это освободит место на диске
3. При следующей сборке образ будет создан заново

## 🎨 Скриншот меню

```
============================================================
  EFT Helper Bot - Management Menu
============================================================

  [1]  Start bot (Docker)
  [2]  Stop bot
  [3]  Restart bot
  [4]  View logs (real-time)
  [5]  View logs (last 50 lines)
  [6]  Check status
  [7]  Rebuild Docker image
  [8]  Update and restart
  [9]  Stop and remove containers
  [10] View resource usage

  [11] Test API connection
  [12] Reset Telegram webhook
  [13] Backup database
  [14] Run local (Poetry)
  [15] Install dependencies (Poetry)

  [16] Clean Docker cache
  [17] View Docker images
  [18] Shell into container

  [0]  Exit

============================================================
Select option: 
```

## ⚡ Быстрые команды

Если вы знаете номер функции, можно использовать команду напрямую:

### Windows (PowerShell)
```powershell
# Запустить бота
.\manage.bat
# Затем введите: 1

# Просмотр логов
.\manage.bat
# Затем введите: 4
```

### Linux/Mac
```bash
# Запустить бота
./manage.sh
# Затем введите: 1

# Просмотр логов  
./manage.sh
# Затем введите: 4
```

## 🔧 Настройка скриптов

### Добавление своих функций

#### Windows (manage.bat)

1. Добавьте пункт в меню:
```batch
echo   [19] Your custom function
```

2. Добавьте обработчик:
```batch
if "%choice%"=="19" goto custom_function
```

3. Создайте функцию:
```batch
:custom_function
cls
echo Your function here
pause
goto menu
```

#### Linux/Mac (manage.sh)

1. Добавьте пункт в меню в функцию `show_menu()`:
```bash
echo "  [19] Your custom function"
```

2. Добавьте case:
```bash
19) custom_function ;;
```

3. Создайте функцию:
```bash
custom_function() {
    print_header
    echo ""
    print_info "Your function here"
    # Your code
    pause
    show_menu
}
```

## 💡 Tips & Tricks

### 1. Быстрый мониторинг

Держите два терминала открытыми:
- Терминал 1: `manage.bat` → выберите [4] для просмотра логов
- Терминал 2: `manage.bat` → выберите [10] для мониторинга ресурсов

### 2. Регулярное резервное копирование

Создайте задачу в планировщике (Windows Task Scheduler / Cron):
- Windows: создайте .bat файл с автоматическим выбором опции 13
- Linux: добавьте в crontab задачу копирования БД

### 3. Автозапуск при старте системы

#### Windows
1. Win+R → `shell:startup`
2. Создайте ярлык на `manage.bat`
3. В свойствах ярлыка добавьте параметр для автовыбора: `/c "echo 1 | manage.bat"`

#### Linux (systemd)
Создайте service unit для автозапуска Docker Compose.

### 4. Алиасы для быстрого доступа

#### Linux/Mac (~/.bashrc или ~/.zshrc)
```bash
alias eft="cd /path/to/eft-helper && ./manage.sh"
alias eft-start="cd /path/to/eft-helper && docker-compose up -d"
alias eft-logs="cd /path/to/eft-helper && docker-compose logs -f"
alias eft-stop="cd /path/to/eft-helper && docker-compose stop"
```

#### Windows PowerShell (Profile)
```powershell
function eft { cd "C:\path\to\EFT Helper"; .\manage.bat }
function eft-start { cd "C:\path\to\EFT Helper"; docker-compose up -d }
function eft-logs { cd "C:\path\to\EFT Helper"; docker-compose logs -f }
```

## 🆘 Troubleshooting

### "Docker is not running"
- Убедитесь что Docker Desktop запущен
- Windows: проверьте в трее
- Linux: `sudo systemctl start docker`

### "Permission denied" (Linux/Mac)
```bash
chmod +x manage.sh
```

### Скрипт не находит docker-compose
Убедитесь что Docker Compose установлен:
```bash
docker-compose --version
```

### Меню отображается некорректно
- Windows: используйте cmd.exe вместо PowerShell
- Убедитесь что кодировка консоли UTF-8

## 📚 Связанная документация

- [Docker Usage Guide](DOCKER_USAGE.md) - подробное руководство по Docker
- [Quick Start Guide](QUICKSTART.md) - быстрый старт проекта
- [Main README](../README.md) - основная документация

---

**Совет:** Добавьте скрипт в закладки/избранное для быстрого доступа!

