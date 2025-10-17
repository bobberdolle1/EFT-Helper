"""Скрипт миграции базы данных для добавления новых полей."""
import asyncio
import aiosqlite
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def migrate_database():
    """Миграция базы данных с добавлением поля trader_levels."""
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "eft_helper.db")
    
    print("🔄 Начало миграции базы данных...")
    
    async with aiosqlite.connect(db_path) as db:
        # Проверяем, существует ли колонка trader_levels
        async with db.execute("PRAGMA table_info(users)") as cursor:
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
        
        if "trader_levels" in column_names:
            print("✅ Колонка trader_levels уже существует. Миграция не требуется.")
            return
        
        print("📝 Добавление колонки trader_levels в таблицу users...")
        
        # Добавляем новую колонку
        await db.execute("ALTER TABLE users ADD COLUMN trader_levels TEXT")
        
        # Устанавливаем значения по умолчанию для существующих пользователей
        default_trader_levels = json.dumps({
            "prapor": 1,
            "therapist": 1,
            "fence": 1,
            "skier": 1,
            "peacekeeper": 1,
            "mechanic": 1,
            "ragman": 1,
            "jaeger": 1
        })
        
        await db.execute(
            "UPDATE users SET trader_levels = ?",
            (default_trader_levels,)
        )
        
        await db.commit()
        
        print("✅ Миграция завершена успешно!")
        print("   - Добавлена колонка trader_levels")
        print("   - Установлены значения по умолчанию (все торговцы уровень 1)")


async def main():
    """Главная функция."""
    print("=" * 60)
    print("  EFT Helper - Миграция базы данных")
    print("=" * 60)
    print()
    
    try:
        await migrate_database()
    except Exception as e:
        print(f"❌ Ошибка при миграции: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    asyncio.run(main())
