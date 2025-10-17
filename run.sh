#!/bin/bash

# ================================
# EFT Helper Bot - Docker Runner
# ================================

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для красивого вывода
print_header() {
    echo ""
    echo "========================================"
    echo "  EFT Helper Bot - Docker Manager"
    echo "========================================"
    echo ""
}

# Проверка наличия Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker не установлен!${NC}"
        echo ""
        echo "Установите Docker:"
        echo "https://docs.docker.com/get-docker/"
        echo ""
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose не установлен!${NC}"
        echo ""
        echo "Установите Docker Compose:"
        echo "https://docs.docker.com/compose/install/"
        echo ""
        exit 1
    fi
}

# Проверка .env файла
check_env() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  Файл .env не найден!${NC}"
        echo ""
        
        if [ -f ".env.example" ]; then
            echo -e "${BLUE}📝 Создаю .env из .env.example...${NC}"
            cp ".env.example" ".env"
            echo -e "${GREEN}✅ Файл .env создан${NC}"
            echo ""
            echo -e "${YELLOW}⚠️  ВАЖНО! Отредактируйте файл .env и укажите:${NC}"
            echo "   - BOT_TOKEN (получите у @BotFather в Telegram)"
            echo "   - ADMIN_IDS (ваши Telegram ID)"
            echo ""
            
            # Открываем редактор
            ${EDITOR:-nano} .env
            
            echo ""
            read -p "Нажмите Enter после настройки..."
        else
            echo -e "${RED}❌ Файл .env.example не найден!${NC}"
            exit 1
        fi
    fi
}

# Создание необходимых директорий
create_dirs() {
    mkdir -p data logs
}

# Функция запуска
start_bot() {
    echo ""
    echo -e "${BLUE}🚀 Запуск бота...${NC}"
    docker-compose up -d
    echo ""
    echo -e "${GREEN}✅ Бот запущен!${NC}"
    echo ""
    echo -e "${BLUE}💡 Используйте './run.sh logs' для просмотра логов${NC}"
}

# Функция остановки
stop_bot() {
    echo ""
    echo -e "${BLUE}⏹️  Остановка бота...${NC}"
    docker-compose down
    echo ""
    echo -e "${GREEN}✅ Бот остановлен!${NC}"
}

# Функция перезапуска
restart_bot() {
    echo ""
    echo -e "${BLUE}🔄 Перезапуск бота...${NC}"
    docker-compose restart
    echo ""
    echo -e "${GREEN}✅ Бот перезапущен!${NC}"
}

# Просмотр логов
show_logs() {
    echo ""
    echo -e "${BLUE}📊 Логи бота (Ctrl+C для выхода):${NC}"
    echo "========================================"
    docker-compose logs -f --tail=100
}

# Статус контейнера
show_status() {
    echo ""
    echo -e "${BLUE}🔍 Статус контейнера:${NC}"
    echo "========================================"
    docker-compose ps
    echo ""
    echo "Детальная информация:"
    docker stats --no-stream eft-helper-bot
    echo ""
}

# Пересборка образа
rebuild_image() {
    echo ""
    echo -e "${BLUE}🏗️  Пересборка образа...${NC}"
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    echo ""
    echo -e "${GREEN}✅ Образ пересобран и запущен!${NC}"
}

# Очистка
clean_all() {
    echo ""
    echo -e "${YELLOW}⚠️  ВНИМАНИЕ! Это удалит все контейнеры и образы проекта!${NC}"
    echo "База данных в папке data/ сохранится."
    echo ""
    read -p "Продолжить? (y/n): " confirm
    
    if [[ $confirm != [yY] ]]; then
        echo "Отменено"
        return
    fi
    
    echo ""
    echo -e "${BLUE}🧹 Очистка...${NC}"
    docker-compose down -v
    docker-compose down --rmi all
    echo ""
    echo -e "${GREEN}✅ Очистка завершена!${NC}"
}

# Вход в контейнер
enter_shell() {
    echo ""
    echo -e "${BLUE}💻 Вход в контейнер...${NC}"
    echo "========================================"
    docker-compose exec eft-helper-bot /bin/bash
}

# Интерактивное меню
show_menu() {
    while true; do
        clear
        print_header
        echo "Выберите действие:"
        echo ""
        echo "[1] 🚀 Запустить бота"
        echo "[2] 🔄 Перезапустить бота"
        echo "[3] ⏹️  Остановить бота"
        echo "[4] 📊 Показать логи"
        echo "[5] 🔍 Статус контейнера"
        echo "[6] 🏗️  Пересобрать образ"
        echo "[7] 🧹 Очистить все (образы + контейнеры)"
        echo "[8] 💻 Войти в контейнер (bash)"
        echo "[9] ❌ Выход"
        echo ""
        read -p "Ваш выбор (1-9): " choice
        
        case $choice in
            1) start_bot; read -p "Нажмите Enter..." ;;
            2) restart_bot; read -p "Нажмите Enter..." ;;
            3) stop_bot; read -p "Нажмите Enter..." ;;
            4) show_logs ;;
            5) show_status; read -p "Нажмите Enter..." ;;
            6) rebuild_image; read -p "Нажмите Enter..." ;;
            7) clean_all; read -p "Нажмите Enter..." ;;
            8) enter_shell ;;
            9) echo ""; echo "👋 До свидания!"; exit 0 ;;
            *) echo ""; echo -e "${RED}❌ Неверный выбор!${NC}"; sleep 2 ;;
        esac
    done
}

# Главная функция
main() {
    check_docker
    check_env
    create_dirs
    
    # Если есть аргументы командной строки
    case "${1:-}" in
        start)
            start_bot
            ;;
        stop)
            stop_bot
            ;;
        restart)
            restart_bot
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        rebuild)
            rebuild_image
            ;;
        clean)
            clean_all
            ;;
        shell)
            enter_shell
            ;;
        *)
            # Если аргументов нет, показываем меню
            show_menu
            ;;
    esac
}

# Запуск
main "$@"
