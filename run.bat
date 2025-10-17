@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

:: ================================
:: EFT Helper Bot - Docker Runner
:: ================================

echo.
echo ========================================
echo   EFT Helper Bot - Docker Manager
echo ========================================
echo.

:: Проверка наличия Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker не установлен!
    echo.
    echo Установите Docker Desktop:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

:: Проверка наличия .env файла
if not exist ".env" (
    echo ⚠️  Файл .env не найден!
    echo.
    if exist ".env.example" (
        echo 📝 Создаю .env из .env.example...
        copy ".env.example" ".env" > nul
        echo ✅ Файл .env создан
        echo.
        echo ⚠️  ВАЖНО! Отредактируйте файл .env и укажите:
        echo    - BOT_TOKEN (получите у @BotFather в Telegram)
        echo    - ADMIN_IDS (ваши Telegram ID)
        echo.
        notepad .env
        echo.
        echo Нажмите любую клавишу после настройки...
        pause > nul
    ) else (
        echo ❌ Файл .env.example не найден!
        pause
        exit /b 1
    )
)

:: Создаем необходимые директории
if not exist "data" mkdir data
if not exist "logs" mkdir logs

:: Меню выбора действия
:menu
cls
echo.
echo ========================================
echo   EFT Helper Bot - Docker Manager
echo ========================================
echo.
echo Выберите действие:
echo.
echo [1] 🚀 Запустить бота
echo [2] 🔄 Перезапустить бота
echo [3] ⏹️  Остановить бота
echo [4] 📊 Показать логи
echo [5] 🔍 Статус контейнера
echo [6] 🏗️  Пересобрать образ
echo [7] 🧹 Очистить все (образы + контейнеры)
echo [8] 💻 Войти в контейнер (bash)
echo [9] ❌ Выход
echo.
set /p choice="Ваш выбор (1-9): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto restart
if "%choice%"=="3" goto stop
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto status
if "%choice%"=="6" goto rebuild
if "%choice%"=="7" goto clean
if "%choice%"=="8" goto shell
if "%choice%"=="9" goto end

echo.
echo ❌ Неверный выбор!
timeout /t 2 > nul
goto menu

:start
echo.
echo 🚀 Запуск бота...
docker-compose up -d
echo.
echo ✅ Бот запущен!
echo.
echo 💡 Используйте опцию [4] для просмотра логов
timeout /t 3 > nul
goto menu

:restart
echo.
echo 🔄 Перезапуск бота...
docker-compose restart
echo.
echo ✅ Бот перезапущен!
timeout /t 2 > nul
goto menu

:stop
echo.
echo ⏹️  Остановка бота...
docker-compose down
echo.
echo ✅ Бот остановлен!
timeout /t 2 > nul
goto menu

:logs
echo.
echo 📊 Логи бота (Ctrl+C для выхода):
echo ========================================
docker-compose logs -f --tail=100
goto menu

:status
echo.
echo 🔍 Статус контейнера:
echo ========================================
docker-compose ps
echo.
echo Детальная информация:
docker stats --no-stream eft-helper-bot
echo.
pause
goto menu

:rebuild
echo.
echo 🏗️  Пересборка образа...
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo.
echo ✅ Образ пересобран и запущен!
timeout /t 3 > nul
goto menu

:clean
echo.
echo ⚠️  ВНИМАНИЕ! Это удалит все контейнеры и образы проекта!
echo База данных в папке data/ сохранится.
echo.
set /p confirm="Продолжить? (y/n): "
if /i not "%confirm%"=="y" goto menu

echo.
echo 🧹 Очистка...
docker-compose down -v
docker-compose down --rmi all
echo.
echo ✅ Очистка завершена!
timeout /t 2 > nul
goto menu

:shell
echo.
echo 💻 Вход в контейнер...
echo ========================================
docker-compose exec eft-helper-bot /bin/bash
goto menu

:end
echo.
echo 👋 До свидания!
timeout /t 1 > nul
exit /b 0
