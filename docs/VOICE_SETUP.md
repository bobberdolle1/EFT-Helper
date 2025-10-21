# Настройка голосовых сообщений (Whisper через Ollama)

## Использование Whisper через Ollama

Для работы с голосовыми сообщениями используется **Whisper через Ollama** - унифицированное решение для AI и голосовой транскрибации.

### Преимущества:
- ✅ Один сервис для Qwen3-8B и Whisper (Ollama)
- ✅ Не требуется Python зависимостей
- ✅ Docker-образ остаётся лёгким (~500 MB)
- ✅ Простая установка и обновление моделей
- ✅ Работает на любой версии Python

---

## Шаг 1: Установка Whisper в Ollama

### 1.1 Скачать модель Whisper

```powershell
# Рекомендуется - быстрая и легкая
ollama pull dimavz/whisper-tiny

# Или другие размеры для лучшего качества:
ollama pull dimavz/whisper-base
ollama pull dimavz/whisper-small
```

### 1.2 Проверить установку

```powershell
ollama list
```

Вы должны увидеть `dimavz/whisper-tiny` в списке моделей.

### Размеры моделей:

| Модель    | Размер | Скорость | Качество |
|-----------|--------|----------|----------|
| `tiny`    | ~75 MB | Очень быстро | Базовое |
| `base`    | ~145 MB | Быстро | Хорошее |
| `small`   | ~460 MB | Средне | Отличное |
| `medium`  | ~1.5 GB | Медленно | Превосходное |
| `large`   | ~2.9 GB | Очень медленно | Наилучшее |

**Рекомендация:** `tiny` или `base` для большинства случаев.

---

## Шаг 2: Настройка Docker

Docker-контейнер настроен на использование локального Ollama через `host.docker.internal`:

```yaml
# docker-compose.yml
extra_hosts:
  - "host.docker.internal:host-gateway"

environment:
  - OLLAMA_URL=http://host.docker.internal:11434
```

Никаких дополнительных volumes не требуется!

---

## Шаг 3: Выбор модели в боте

Модель настраивается в переменной окружения:

```bash
# .env
WHISPER_MODEL=tiny  # tiny, base, small, medium, large
```

По умолчанию используется `tiny`.

---

## Тестирование

### 1. Запустите бота:
```bash
docker-compose up -d
```

### 2. Отправьте голосовое сообщение боту

### 3. Проверьте логи:
```bash
docker-compose logs -f eft-helper-bot
```

Вы должны увидеть:
```
Loading Whisper model: base
Whisper model loaded successfully
Transcribing audio file: /tmp/eft_voice/...
Transcription successful: ...
```

---

## Устранение проблем

### Ошибка: "Ollama API error"

**Решение:** Убедитесь, что Ollama запущен:
```powershell
ollama serve
```

### Модель не найдена

**Решение:** Скачайте модель:
```powershell
ollama pull dimavz/whisper-tiny
```

### Проверка доступности

```powershell
curl http://localhost:11434/api/tags
```

Вы должны увидеть список моделей, включая `dimavz/whisper-tiny`.

### Медленная транскрипция

**Решение:** 
1. Используйте более лёгкую модель (`tiny` или `base`)
2. Убедитесь, что используется CPU (не GPU в Docker)

---

## Переключение модели

Чтобы изменить модель:

1. Скачать новую модель:
```powershell
ollama pull dimavz/whisper-base
```

2. Обновить `.env`:
```bash
WHISPER_MODEL=base
```

3. Перезапустить бот:
```bash
docker-compose restart eft-helper-bot
```

---

## Примечания

- **Голосовые сообщения обрабатываются AI-ассистентом Никитой** - транскрибированный текст передаётся как обычное текстовое сообщение
- **Поддерживаются языки:** русский и английский
- **Автоопределение языка:** бот использует язык пользователя из настроек
- **Формат аудио:** Telegram OGG автоматически конвертируется FFmpeg

---

## Дополнительная информация

- Ollama Whisper: https://ollama.com/dimavz/whisper-tiny
- Документация Ollama: https://ollama.com/
- Оригинальный Whisper: https://github.com/openai/whisper
