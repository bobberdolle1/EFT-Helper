"""Скрипт миграции базы данных для добавления новых полей."""
import asyncio
import aiosqlite
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def migrate_database():
    """Миграция базы данных с добавлением новых полей."""
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "eft_helper.db")
    
    print("🔄 Начало миграции базы данных...")
    
    async with aiosqlite.connect(db_path) as db:
        migrations_applied = []
        
        # Миграция 1: Добавление trader_levels в users
        async with db.execute("PRAGMA table_info(users)") as cursor:
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
        
        if "trader_levels" not in column_names:
            print("📝 Добавление колонки trader_levels в таблицу users...")
            await db.execute("ALTER TABLE users ADD COLUMN trader_levels TEXT")
            
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
            migrations_applied.append("trader_levels в users")
        
        # Миграция 2: Добавление flea_price в weapons
        async with db.execute("PRAGMA table_info(weapons)") as cursor:
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
        
        if "flea_price" not in column_names:
            print("📝 Добавление колонки flea_price в таблицу weapons...")
            await db.execute("ALTER TABLE weapons ADD COLUMN flea_price INTEGER")
            migrations_applied.append("flea_price в weapons")
        
        # Миграция 3: Добавление flea_price в modules
        async with db.execute("PRAGMA table_info(modules)") as cursor:
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
        
        if "flea_price" not in column_names:
            print("📝 Добавление колонки flea_price в таблицу modules...")
            await db.execute("ALTER TABLE modules ADD COLUMN flea_price INTEGER")
            migrations_applied.append("flea_price в modules")
        
        await db.commit()
        
        if migrations_applied:
            print("\n✅ Миграция завершена успешно!")
            print("   Применены следующие миграции:")
            for migration in migrations_applied:
                print(f"   - {migration}")
        else:
            print("✅ Все миграции уже применены. База данных актуальна.")


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
