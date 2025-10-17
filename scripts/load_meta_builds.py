"""Загрузка мета-сборок в базу данных."""
import asyncio
import aiosqlite
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.meta_builds_data import META_BUILDS
from database import BuildCategory


async def find_weapon_id(conn, weapon_name: str):
    """Найти ID оружия по имени."""
    # Пробуем точное совпадение
    async with conn.execute(
        "SELECT id FROM weapons WHERE name_en = ? OR name_ru = ?",
        (weapon_name, weapon_name)
    ) as cursor:
        result = await cursor.fetchone()
        if result:
            return result[0]
    
    # Пробуем частичное совпадение
    search_pattern = f"%{weapon_name}%"
    async with conn.execute(
        "SELECT id FROM weapons WHERE name_en LIKE ? OR name_ru LIKE ? LIMIT 1",
        (search_pattern, search_pattern)
    ) as cursor:
        result = await cursor.fetchone()
        if result:
            return result[0]
    
    return None


async def load_meta_builds():
    """Загрузить мета-сборки в БД."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "eft_helper.db")
    
    print("=" * 60)
    print("  Загрузка мета-сборок в БД")
    print("=" * 60)
    print()
    
    async with aiosqlite.connect(db_path) as db:
        added = 0
        skipped = 0
        
        for weapon_name, builds in META_BUILDS.items():
            # Найти ID оружия
            weapon_id = await find_weapon_id(db, weapon_name)
            
            if not weapon_id:
                print(f"  ⚠️  Оружие не найдено: {weapon_name}")
                skipped += len(builds)
                continue
            
            for build_type, build_data in builds.items():
                name_ru = build_data.get("name_ru")
                name_en = build_data.get("name_en")
                description_ru = build_data.get("description_ru", "")
                description_en = build_data.get("description_en", "")
                parts = build_data.get("parts", [])
                cost = build_data.get("estimated_cost", 0)
                min_loyalty = build_data.get("min_loyalty", 1)
                
                # Определить категорию
                if build_type == "meta":
                    category = BuildCategory.META.value
                elif build_type == "budget":
                    category = BuildCategory.RANDOM.value  # Используем RANDOM для бюджетных
                else:
                    category = BuildCategory.META.value
                
                # Сохранить части как JSON (пока без привязки к модулям)
                modules_json = json.dumps([])  # Пустой массив, т.к. нет ID модулей
                
                # Добавить сборку
                await db.execute(
                    """INSERT INTO builds 
                    (weapon_id, category, name_ru, name_en, total_cost, min_loyalty_level, modules, planner_link)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (weapon_id, category, name_ru, name_en, cost, min_loyalty, modules_json, None)
                )
                
                added += 1
                print(f"  ✅ {weapon_name}: {name_ru}")
        
        await db.commit()
        
        print()
        print(f"📊 Статистика:")
        print(f"   • Добавлено сборок: {added}")
        print(f"   • Пропущено: {skipped}")
        print()
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(load_meta_builds())
