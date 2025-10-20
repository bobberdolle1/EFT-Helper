# AI Assistant Setup Guide - "Nikita Buyanov"

**Version:** 5.1  
**Last Updated:** October 21, 2025

## Обзор

В версии 5.1 EFT Helper внедрён локальный AI-ассистент **«Никита Буянов»** на базе модели Qwen3-8B через Ollama. Ассистент заменяет большую часть статичной логики генерации сборок и становится центральным способом взаимодействия с ботом.

## Основные возможности

✅ **Универсальная генерация сборок через LLM**
- Пользовательские запросы: *"Сделай сборку на АК-74М до 300к"*
- Квестовые сборки с точным учётом требований
- Мета-сборки на основе актуальных данных
- Случайные сборки с контекстом

✅ **Поддержка голосового ввода**
- Транскрибация через Whisper
- Автоматическая обработка как текстовых сообщений

✅ **Контекстно-зависимые ответы**
- Актуальные данные из tarkov.dev API
- Учёт уровней лояльности пользователя
- Структурированный вывод с обоснованием

✅ **Отказоустойчивость**
- Автоматический fallback на кнопочный интерфейс при недоступности LLM

---

## Системные требования

### Минимальные требования:
- **CPU:** 4 cores
- **RAM:** 8 GB (для Ollama + Qwen3-8B)
- **Диск:** 10 GB свободного места
- **ОС:** Linux/Windows/macOS с Docker

### Рекомендуемые требования:
- **CPU:** 8+ cores
- **RAM:** 16 GB
- **GPU:** NVIDIA с 8+ GB VRAM (опционально, для ускорения)
- **Диск:** SSD с 20+ GB

---

## Установка и настройка

### Вариант 1: Docker Compose (рекомендуется)

#### Шаг 1: Запуск сервисов

```bash
# Запустить все сервисы (бот + Ollama)
docker-compose up -d

# Проверить статус
docker-compose ps
```

#### Шаг 2: Загрузка модели Qwen3-8B (обязательно!)

Модель **НЕ скачивается автоматически**. Необходимо вручную загрузить:

```bash
# Загрузить модель Qwen3-8B (займет 5-10 минут, ~4.7 GB)
docker exec -it eft-helper-ollama ollama pull qwen3:8b

# Проверить, что модель загружена
docker exec -it eft-helper-ollama ollama list
# Должно быть: qwen3:8b
```

#### Шаг 3: Тестирование

```bash
# Тестовый запрос к модели
docker exec -it eft-helper-ollama ollama run qwen3:8b "Привет"

# Проверить логи бота
docker-compose logs -f eft-helper-bot
# Должно быть: ✅ AI Assistant (Nikita Buyanov) - ONLINE
```

### Вариант 2: Локальная установка (без Docker)

#### Шаг 1: Установка Ollama

**Linux/macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Скачайте установщик с [ollama.com](https://ollama.com/download)

#### Шаг 2: Запуск Ollama

```bash
ollama serve
```

#### Шаг 3: Загрузка модели

```bash
ollama pull qwen3:8b
```

#### Шаг 4: Установка зависимостей Python

```bash
# Установка Poetry (если не установлен)
pip install poetry

# Установка зависимостей
poetry install

# Или через pip
pip install openai-whisper ffmpeg-python
```

#### Шаг 5: Настройка переменных окружения

Создайте или обновите `.env`:

```env
BOT_TOKEN=your_telegram_bot_token_here
OLLAMA_URL=http://localhost:11434
```

#### Шаг 6: Запуск бота

```bash
poetry run python main.py
# или
python main.py
```

---

## Настройка голосового ввода (опционально)

### Установка FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Скачайте с [ffmpeg.org](https://ffmpeg.org/download.html) и добавьте в PATH

### Проверка

```bash
ffmpeg -version
```

---

## Конфигурация

### Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|-----------|----------|----------------------|
| `OLLAMA_URL` | URL Ollama API | `http://localhost:11434` |
| `BOT_TOKEN` | Telegram Bot Token | (обязательно) |

### Параметры модели

В `services/ai_generation_service.py` можно настроить:

```python
"options": {
    "temperature": 0.7,  # Креативность (0.0-1.0)
    "top_p": 0.9,        # Nucleus sampling
    "max_tokens": 2048   # Максимальная длина ответа
}
```

---

## Использование

### Текстовые запросы

Пользователь может писать боту напрямую без использования кнопок:

**После (v5.1):**
```
User: "Привет Никита! Нужна сборка на M4A1, бюджет 400к, 
       хочу хорошую эргономику"

🤖 Никита Буянов:
Вот ваша сборка для M4A1:

1️⃣ **Базовое оружие:** Colt M4A1 (ID: 5447a9cd4bdc2dbd208b4567)
   - Цена: 45,000 ₽
   - Базовая эргономика: 45
   - Базовая отдача: 85
   📍 Peacekeeper L2

2️⃣ **Цевье:**
   а) Geissele Super Modular Rail MK16 — 35,000 ₽ (Эрго: +8)
      📍 Mechanic L3

3️⃣ **Приклад:**
   а) Magpul MOE Stock — 12,000 ₽ (Эрго: +3, Отдача: -5)
      📍 Peacekeeper L2

4️⃣ **Прицел:**
   а) EOTech EXPS3 — 28,000 ₽ (Эрго: +2)
      📍 Skier L3 или Flea Market
...

📊 **Характеристики:**
   - Эргономика: 68
   - Вертикальная отдача: 65

💰 **Итого:** 387,000 ₽

💡 **Обоснование:** Выбрал Geissele цевье для максимальной 
эргономики при сохранении бюджета. Все модули доступны 
у торговцев 2-3 уровня лояльности.
```

### Голосовые сообщения

Пользователь может отправить голосовое сообщение — оно будет автоматически распознано и обработано.

### Кнопочное меню

Все старые функции остаются доступными через кнопки главного меню.

---

## Мониторинг и отладка

### Логи

```bash
# Docker
docker-compose logs -f eft-helper-bot

# Локально
tail -f logs/bot.log
```

### Проверка статуса AI

При запуске бот выводит:
```
✅ AI Assistant (Nikita Buyanov) - ONLINE
```

Или при проблемах:
```
⚠️ AI Assistant - OFFLINE (fallback mode)
```

### Тестирование Ollama

```bash
# Проверка доступности API
curl http://localhost:11434/api/tags

# Тестовый запрос
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:latest",
  "prompt": "Hello",
  "stream": false
}'
```

---

## Troubleshooting

### Проблема: Ollama не запускается

**Решение:**
```bash
# Проверить, что порт 11434 свободен
netstat -tuln | grep 11434

# Перезапустить службу
docker-compose restart ollama

# Посмотреть логи
docker-compose logs ollama
```

### Проблема: Модель не загружена

**Причина:** Модель нужно загружать вручную, она не скачивается автоматически.

**Решение:**
```bash
# Проверить список моделей
docker exec -it eft-helper-ollama ollama list

# Загрузить модель вручную
docker exec -it eft-helper-ollama ollama pull qwen3:8b

# Перезапустить бота после загрузки
docker-compose restart eft-helper-bot
```

### Проблема: AI не отвечает / таймаут

**Причины:**
1. Недостаточно RAM (нужно минимум 8 GB)
2. Модель ещё загружается в память (подождите 30-60 сек)
3. Ollama service недоступен

**Решение:**
```bash
# Проверить использование ресурсов
docker stats

# Увеличить таймаут в ai_generation_service.py
timeout=aiohttp.ClientTimeout(total=120)  # было 60
```

### Проблема: Голосовые сообщения не работают

**Решение:**
1. Проверить установку FFmpeg: `ffmpeg -version`
2. Проверить установку Whisper: `pip show openai-whisper`
3. Посмотреть логи: `tail -f logs/bot.log | grep voice`

### Проблема: Ответы на неправильном языке

**Причина:** Не установлен язык пользователя в БД

**Решение:**
Пользователь должен зайти в Настройки → Выбрать язык

---

## Производительность

### Время ответа

| Сценарий | CPU (4 cores) | CPU (8 cores) | GPU (RTX 3060) |
|----------|---------------|---------------|----------------|
| Простой вопрос | 3-5 сек | 2-3 сек | < 1 сек |
| Генерация сборки | 10-15 сек | 5-8 сек | 2-3 сек |
| Голосовое сообщение | 15-20 сек | 10-12 сек | 5-7 сек |

### Оптимизация

**1. Использование GPU (NVIDIA)**

```bash
# Установка NVIDIA Container Toolkit
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

# Обновить docker-compose.yml для ollama:
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

**2. Использование более легкой модели**

Можно использовать модели меньшего размера:

```bash
# Qwen3-3B (быстрее, меньше памяти)
ollama pull qwen3:3b
```

В `ai_generation_service.py`:
```python
self.model = "qwen3:3b"  # Вместо qwen3:8b
```

**3. Кэширование контекста**

Контекст автоматически кэшируется в `TarkovAPIClient` на 24 часа.

---

## Архитектура

```
User Message/Voice
       ↓
handlers/common.py (message routing)
       ↓
services/ai_assistant.py (central handler)
       ↓
services/ai_generation_service.py (LLM interaction)
       ↓
services/context_builder.py (prepare data)
       ↓
api_clients/tarkov_api_client.py (fetch actual data)
       ↓
Ollama (Qwen2.5-8B) → Generate response
       ↓
Structured output → User
```

---

## Дальнейшее развитие

### Запланированные улучшения:

1. **Голосовые ответы** — синтез речи для ответов бота
2. **Мультимодальность** — анализ скриншотов сборок
3. **Персонализация** — запоминание предпочтений пользователя
4. **Интеграция с калькулятором** — точный расчёт характеристик
5. **Обучение на данных сообщества** — fine-tuning на реальных сборках

---

## Лицензия и авторство

**AI Assistant «Никита Буянов»**  
В честь Никиты Буянова — основателя Battlestate Games и создателя Escape from Tarkov.

Модель: [Qwen3-8B](https://github.com/QwenLM/Qwen) by Alibaba Cloud  
Voice: [OpenAI Whisper](https://github.com/openai/whisper)

---

## Поддержка

Если возникли проблемы:
1. Проверьте логи: `logs/bot.log`
2. Проверьте документацию: `docs/`
3. Создайте issue в GitHub

**Важно:** Не публикуйте свой BOT_TOKEN в логах!
