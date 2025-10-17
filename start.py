"""Скрипт автоматического запуска бота с проверками и инициализацией."""
import asyncio
import os
import sys


async def check_env_file():
    """Проверка наличия .env файла."""
    print("🔍 Проверка файла конфигурации...")
    
    if not os.path.exists(".env"):
        print("❌ Файл .env не найден!")
        print("\n📝 Создание .env из .env.example...")
        
        if os.path.exists(".env.example"):
            with open(".env.example", "r", encoding="utf-8") as example:
                content = example.read()
            
            with open(".env", "w", encoding="utf-8") as env:
                env.write(content)
            
            print("✅ Файл .env создан")
            print("\n⚠️  ВНИМАНИЕ! Отредактируйте файл .env и укажите ваш BOT_TOKEN")
            print("   Получите токен у @BotFather в Telegram")
            input("\nНажмите Enter после настройки .env...")
        else:
            print("❌ Файл .env.example не найден!")
            return False
    else:
        print("✅ Файл .env найден")
    
    # Проверка что токен указан
    with open(".env", "r", encoding="utf-8") as f:
        content = f.read()
        if "your_telegram_bot_token_here" in content or "BOT_TOKEN=" not in content:
            print("❌ BOT_TOKEN не настроен в файле .env!")
            print("   Откройте .env и укажите ваш токен от @BotFather")
            return False
    
    return True


async def migrate_database():
    """Миграция базы данных для обновления схемы."""
    import aiosqlite
    import json
    from utils.constants import DEFAULT_TRADER_LEVELS, DEFAULT_DB_PATH
    
    db_path = DEFAULT_DB_PATH
    
    async with aiosqlite.connect(db_path) as db:
        # Проверяем, существует ли колонка trader_levels
        async with db.execute("PRAGMA table_info(users)") as cursor:
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
        
        if "trader_levels" not in column_names:
            print("   📝 Обновление схемы базы данных...")
            
            # Добавляем новую колонку
            await db.execute("ALTER TABLE users ADD COLUMN trader_levels TEXT")
            
            # Устанавливаем значения по умолчанию
            default_trader_levels = json.dumps(DEFAULT_TRADER_LEVELS)
            
            await db.execute(
                "UPDATE users SET trader_levels = ?",
                (default_trader_levels,)
            )
            
            await db.commit()
            print("   ✅ Схема базы данных обновлена")


async def init_database():
    """Инициализация базы данных."""
    print("\n🗄️  Инициализация базы данных...")
    
    from database import Database
    
    db = Database("data/eft_helper.db")
    await db.init_db()
    
    print("✅ База данных инициализирована")
    
    # Выполняем миграцию при необходимости
    await migrate_database()
    
    return db


async def check_database_content(db):
    """Проверка наличия данных в базе."""
    print("\n📊 Проверка содержимого базы данных...")
    
    import aiosqlite
    
    async with aiosqlite.connect(db.db_path) as conn:
        # Проверка наличия оружия
        async with conn.execute("SELECT COUNT(*) FROM weapons") as cursor:
            weapons_count = (await cursor.fetchone())[0]
        
        # Проверка наличия модулей
        async with conn.execute("SELECT COUNT(*) FROM modules") as cursor:
            modules_count = (await cursor.fetchone())[0]
        
        # Проверка наличия сборок
        async with conn.execute("SELECT COUNT(*) FROM builds") as cursor:
            builds_count = (await cursor.fetchone())[0]
        
        # Проверка наличия торговцев
        async with conn.execute("SELECT COUNT(*) FROM traders") as cursor:
            traders_count = (await cursor.fetchone())[0]
    
    print(f"   Оружие: {weapons_count}")
    print(f"   Модули: {modules_count}")
    print(f"   Сборки: {builds_count}")
    print(f"   Торговцы: {traders_count}")
    
    return {
        "weapons": weapons_count,
        "modules": modules_count,
        "builds": builds_count,
        "traders": traders_count
    }


async def populate_sample_data():
    """Заполнение базы тестовыми данными."""
    print("\n📦 Заполнение базы тестовыми данными...")
    print("   (Это может занять некоторое время)")
    
    try:
        # Добавляем путь к scripts в sys.path
        scripts_path = os.path.join(os.path.dirname(__file__), 'scripts')
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        
        # Импортируем и запускаем populate_db
        import populate_db
        await populate_db.main()
        print("✅ Тестовые данные добавлены")
        return True
    except Exception as e:
        print(f"❌ Ошибка при заполнении данных: {e}")
        import traceback
        traceback.print_exc()
        return False


async def sync_from_api():
    """Синхронизация данных с tarkov.dev API."""
    print("\n🌐 Синхронизация с tarkov.dev API...")
    print("   (Это может занять некоторое время)")
    
    try:
        # Добавляем путь к scripts в sys.path
        scripts_path = os.path.join(os.path.dirname(__file__), 'scripts')
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        
        import sync_tarkov_data
        await sync_tarkov_data.main()
        return True
    except Exception as e:
        print(f"⚠️  Ошибка синхронизации с API: {e}")
        print("   Продолжаем с локальными данными...")
        import traceback
        traceback.print_exc()
        return False


async def start_bot():
    """Запуск бота."""
    print("\n🤖 Запуск бота...")
    print("=" * 60)
    
    import logging
    from aiogram import Bot, Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage
    from database.config import settings
    from handlers import common, search, builds, loyalty, tier_list, settings as settings_handler
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Database already initialized
    from database import Database
    db = Database("data/eft_helper.db")
    
    # Initialize bot and dispatcher
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register routers
    dp.include_router(common.router)
    dp.include_router(search.router)
    dp.include_router(builds.router)
    dp.include_router(loyalty.router)
    dp.include_router(tier_list.router)
    dp.include_router(settings_handler.router)
    
    # Middleware to inject db into handlers
    @dp.update.outer_middleware()
    async def db_middleware(handler, event, data):
        data["db"] = db
        return await handler(event, data)
    
    # Global error handler
    @dp.error()
    async def error_handler(event, exception):
        logger.error(f"Error occurred: {exception}", exc_info=True)
        return True
    
    logger.info("Bot starting...")
    
    try:
        # Start polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot stopped")


async def main():
    """Основная функция запуска."""
    print("=" * 60)
    print("  EFT Helper - Автоматический запуск")
    print("=" * 60)
    
    # 1. Проверка .env файла
    if not await check_env_file():
        print("\n❌ Запуск прерван. Настройте .env файл и запустите снова.")
        input("\nНажмите Enter для выхода...")
        return
    
    # 2. Инициализация базы данных
    db = await init_database()
    
    # 3. Проверка содержимого базы
    db_content = await check_database_content(db)
    
    # 4. Если база пустая, автоматически заполнить данными
    if db_content["weapons"] == 0 or db_content["traders"] == 0:
        print("\n⚠️  База данных пуста!")
        print("\n📦 Автоматическое заполнение базы данных...")
        print("   (Используются тестовые данные для быстрого старта)\n")
        
        # Автоматически заполняем тестовыми данными
        success = await populate_sample_data()
        
        if not success:
            print("❌ Не удалось заполнить базу данных.")
            print("   Попробуйте запустить вручную: python populate_db.py")
            input("\nНажмите Enter для выхода...")
            return
        
        print("\n💡 Подсказка: для получения актуальных данных из tarkov.dev API")
        print("   запустите: python sync_tarkov_data.py")
    
    # 5. Финальная проверка
    print("\n✅ Все проверки пройдены!")
    print("=" * 60)
    
    # 6. Запуск бота
    await start_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")
