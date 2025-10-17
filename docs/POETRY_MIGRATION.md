# 📦 Миграция с pip на Poetry

## Что изменилось?

Проект EFT Helper теперь использует **Poetry** для управления зависимостями вместо традиционного pip + requirements.txt.

### Преимущества Poetry:

✅ **Автоматическое управление виртуальным окружением**  
✅ **Детерминированные зависимости** через `poetry.lock`  
✅ **Лучшее разрешение конфликтов** зависимостей  
✅ **Удобное управление dev-зависимостями**  
✅ **Встроенная система сборки пакетов**  
✅ **Современный стандарт Python (PEP 518)**

---

## 🚀 Быстрая миграция

### Шаг 1: Установите Poetry

```bash
pip install poetry
```

Или используйте официальный установщик:

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

**Linux/macOS:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Шаг 2: Удалите старое виртуальное окружение (опционально)

```bash
# Windows
rmdir /s venv

# Linux/macOS
rm -rf venv
```

### Шаг 3: Установите зависимости через Poetry

```bash
poetry install
```

Poetry автоматически:
- Создаст новое виртуальное окружение
- Установит все зависимости из `pyproject.toml`
- Создаст файл `poetry.lock` с фиксированными версиями

### Шаг 4: Запустите проект

```bash
poetry run python start.py
```

Или активируйте окружение:

```bash
poetry shell
python start.py
```

---

## 📝 Сравнение команд

| Задача | pip | Poetry |
|--------|-----|--------|
| Установка зависимостей | `pip install -r requirements.txt` | `poetry install` |
| Добавление пакета | `pip install package` + ручное добавление в requirements.txt | `poetry add package` |
| Удаление пакета | `pip uninstall package` + ручное удаление из requirements.txt | `poetry remove package` |
| Обновление пакета | `pip install --upgrade package` | `poetry update package` |
| Запуск скрипта | `python script.py` | `poetry run python script.py` |
| Активация окружения | `venv\Scripts\activate` (Windows)<br>`source venv/bin/activate` (Linux/macOS) | `poetry shell` |
| Dev-зависимости | Нет встроенной поддержки | `poetry add --group dev package` |

---

## 🔄 Обновленные команды проекта

### Запуск бота

**Старый способ (pip):**
```bash
python start.py
```

**Новый способ (Poetry):**
```bash
poetry run python start.py
# или
poetry shell
python start.py
```

### Скрипты

**Старый способ:**
```bash
python scripts/sync_tarkov_data.py
python scripts/populate_db.py
python setup_complete.py
```

**Новый способ:**
```bash
poetry run python scripts/sync_tarkov_data.py
poetry run python scripts/populate_db.py
poetry run python setup_complete.py
```

---

## 🛠️ Управление зависимостями

### Добавление новой зависимости

**Старый способ:**
```bash
pip install aiofiles
echo "aiofiles==23.2.1" >> requirements.txt
```

**Новый способ:**
```bash
poetry add aiofiles
```

Poetry автоматически:
- Установит пакет
- Добавит в `pyproject.toml`
- Обновит `poetry.lock`

### Добавление dev-зависимости

```bash
poetry add --group dev pytest
poetry add --group dev black
```

### Обновление зависимостей

```bash
# Обновить одну зависимость
poetry update aiogram

# Обновить все зависимости
poetry update
```

### Просмотр установленных пакетов

```bash
poetry show

# С подробной информацией
poetry show --tree
```

---

## 📂 Структура файлов

### Было (pip):
```
EFT Helper/
├── requirements.txt       # Список зависимостей
├── venv/                  # Виртуальное окружение
└── ...
```

### Стало (Poetry):
```
EFT Helper/
├── pyproject.toml         # Конфигурация проекта и зависимости
├── poetry.lock            # Зафиксированные версии (генерируется автоматически)
├── requirements.txt       # Оставлен для обратной совместимости
├── .venv/                 # Виртуальное окружение Poetry (в .gitignore)
└── ...
```

---

## ⚙️ Конфигурация Poetry

### Где хранится виртуальное окружение?

По умолчанию Poetry создает окружение в:
- Windows: `%USERPROFILE%\AppData\Local\pypoetry\Cache\virtualenvs\`
- Linux/macOS: `~/.cache/pypoetry/virtualenvs/`

### Создать окружение в папке проекта (.venv)

```bash
poetry config virtualenvs.in-project true
poetry install
```

### Использовать конкретную версию Python

```bash
poetry env use python3.11
```

### Список окружений

```bash
poetry env list
```

---

## 🔧 Решение проблем

### Poetry не найден после установки

Добавьте Poetry в PATH:

**Windows:**
```powershell
$Env:Path += ";$Env:APPDATA\Python\Scripts"
```

**Linux/macOS:**
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Конфликты зависимостей

```bash
# Очистить кэш
poetry cache clear pypi --all

# Пересоздать lock файл
poetry lock --no-update

# Переустановить зависимости
poetry install
```

### Медленная установка

```bash
# Использовать параллельную установку
poetry config installer.max-workers 10

# Или отключить keyring (может ускорить на Windows)
poetry config keyring.enabled false
```

### Проблемы с существующим venv

```bash
# Удалите старое окружение
poetry env remove python

# Создайте новое
poetry install
```

---

## 🔄 Обратная совместимость

### Я все еще хочу использовать pip

`requirements.txt` сохранен для обратной совместимости. Вы можете продолжать использовать:

```bash
pip install -r requirements.txt
python start.py
```

Но рекомендуем перейти на Poetry для лучшего опыта разработки.

### Генерация requirements.txt из Poetry

Если вам нужен актуальный `requirements.txt`:

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

---

## 📚 Дополнительные ресурсы

- [Официальная документация Poetry](https://python-poetry.org/docs/)
- [Poetry GitHub](https://github.com/python-poetry/poetry)
- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)

---

## ❓ Часто задаваемые вопросы

### Нужно ли удалять requirements.txt?

Нет, файл оставлен для совместимости. Основной файл теперь - `pyproject.toml`.

### Можно ли использовать pip и Poetry одновременно?

Технически да, но не рекомендуется. Выберите один инструмент.

### Как добавить новую зависимость?

```bash
poetry add package-name
```

### Как откатиться на pip?

Просто используйте старые команды:
```bash
pip install -r requirements.txt
python start.py
```

### Poetry создает окружение каждый раз заново?

Нет, Poetry использует существующее окружение если оно есть.

---

## ✅ Чеклист миграции

- [ ] Установил Poetry (`pip install poetry`)
- [ ] Удалил старое venv (опционально)
- [ ] Выполнил `poetry install`
- [ ] Проверил работу: `poetry run python start.py`
- [ ] Обновил скрипты/CI для использования `poetry run`
- [ ] Добавил `poetry.lock` в git (если нужен детерминизм)

---

**Готово!** 🎉 Теперь вы используете современный менеджер зависимостей Poetry!
