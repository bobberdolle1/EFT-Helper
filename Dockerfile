# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем метаданные
LABEL maintainer="EFT Helper Bot"
LABEL description="Telegram bot for Escape from Tarkov players"

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt pyproject.toml ./

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем директорию для базы данных
RUN mkdir -p /app/data

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Открываем порт (если потребуется в будущем для webhook)
EXPOSE 8080

# Запускаем бота
CMD ["python", "start.py"]
