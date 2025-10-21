# Настройка голосовых сообщений (Whisper)

## Установка Whisper на хост-машине

Для работы с голосовыми сообщениями используется **OpenAI Whisper**, установленный **локально на хосте** (не в Docker-контейнере).

### Преимущества такого подхода:
- ✅ Модели скачиваются один раз на хост
- ✅ Docker-образ остаётся лёгким (~500 MB вместо ~3-4 GB)
- ✅ Быстрая сборка контейнера
- ✅ Модели переиспользуются между контейнерами

---

## Шаг 1: Установка зависимостей на Windows

### 1.1 Установить FFmpeg

Whisper требует FFmpeg для обработки аудио.

**Через Chocolatey (рекомендуется):**
```powershell
choco install ffmpeg
```

**Или вручную:**
1. Скачать FFmpeg: https://ffmpeg.org/download.html
2. Распаковать в `C:\ffmpeg`
3. Добавить `C:\ffmpeg\bin` в PATH

### 1.2 Установить Whisper

```powershell
pip install openai-whisper
```

### 1.3 Проверить установку

```powershell
python -c "import whisper; print('Whisper installed successfully')"
```

---

## Шаг 2: Скачивание моделей

Whisper использует следующие модели (по возрастанию размера и точности):

| Модель    | Размер | Скорость | Точность |
|-----------|--------|----------|----------|
| `tiny`    | 39 MB  | Самая быстрая | Низкая |
| `base`    | 74 MB  | Быстрая | Средняя |
| `small`   | 244 MB | Средняя | Хорошая |
| `medium`  | 769 MB | Медленная | Отличная |
| `large`   | 1.5 GB | Очень медленная | Наилучшая |

**Рекомендация:** используйте модель `base` или `small` для баланса скорости и качества.

### Скачать модель заранее:

```powershell
python -c "import whisper; whisper.load_model('base')"
```

Модель скачается в `~/.cache/whisper/` (на Windows: `C:\Users\<Username>\.cache\whisper\`)

---

## Шаг 3: Настройка Docker

Docker-контейнер уже настроен на использование Whisper с хоста через volume:

```yaml
# docker-compose.yml
volumes:
  - ~/.cache/whisper:/root/.cache/whisper:ro  # Кэш моделей с хоста
  - /tmp/eft_voice:/tmp/eft_voice  # Временные голосовые файлы
```

**Важно:** На Windows путь `~/.cache/whisper` автоматически преобразуется в `C:\Users\<Username>\.cache\whisper`

---

## Шаг 4: Выбор модели в боте

Модель настраивается в переменной окружения:

```bash
# .env
WHISPER_MODEL=base  # tiny, base, small, medium, large
```

По умолчанию используется `base`.

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

### Ошибка: "Whisper not installed"

**Решение:** Убедитесь, что Whisper установлен **на хост-машине**:
```powershell
pip install openai-whisper
```

### Ошибка: "FFmpeg not found"

**Решение:** Установите FFmpeg и добавьте в PATH:
```powershell
choco install ffmpeg
```

### Модели не загружаются

**Решение:** Проверьте, что volume правильно примонтирован:
```bash
docker-compose exec eft-helper-bot ls -la /root/.cache/whisper
```

Должны быть видны файлы `.pt` моделей.

### Медленная транскрипция

**Решение:** 
1. Используйте более лёгкую модель (`tiny` или `base`)
2. Убедитесь, что используется CPU (не GPU в Docker)

---

## Переключение модели

Чтобы изменить модель:

1. Скачать новую модель на хосте:
```powershell
python -c "import whisper; whisper.load_model('small')"
```

2. Обновить `.env`:
```bash
WHISPER_MODEL=small
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

- Документация Whisper: https://github.com/openai/whisper
- FFmpeg: https://ffmpeg.org/
