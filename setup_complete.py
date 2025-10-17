"""Полная автоматическая настройка EFT Helper бота."""
import asyncio
import aiosqlite
import json
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database, BuildCategory
from database.quest_builds_data import get_all_quests
from database.meta_builds_data import META_BUILDS
from utils.builds_fetcher import BuildsFetcher


async def setup_complete():
    """Полная настройка бота."""
    db_path = os.path.join(os.path.dirname(__file__), "data", "eft_helper.db")
    
    print("=" * 70)
    print("  EFT HELPER BOT - ПОЛНАЯ АВТОМАТИЧЕСКАЯ НАСТРОЙКА")
    print("=" * 70)
    print()
    
    # Шаг 1: Очистка базы данных
    print("🗑️  ШАГ 1/4: Очистка базы данных...")
    async with aiosqlite.connect(db_path) as db:
        await db.execute("DELETE FROM builds")
        
        # Удалить дубликаты оружия
        async with db.execute("SELECT id, name_en FROM weapons ORDER BY id") as cursor:
            weapons = await cursor.fetchall()
        
        seen = set()
        for weapon_id, name in weapons:
            if name in seen:
                await db.execute("DELETE FROM weapons WHERE id = ?", (weapon_id,))
            else:
                seen.add(name)
        
        await db.commit()
    print("   ✅ База данных очищена")
    print()
    
    # Шаг 2: Загрузка квестовых сборок
    print("📜 ШАГ 2/4: Загрузка квестовых сборок...")
    quests = get_all_quests()
    
    async with aiosqlite.connect(db_path) as db:
        await db.execute("DELETE FROM quests")
        
        for quest_id, quest_data in quests.items():
            extra_data = {
                "trader": quest_data.get("trader"),
                "level_required": quest_data.get("level_required"),
                "weapon": quest_data.get("weapon"),
                "requirements": quest_data.get("requirements"),
                "recommended_parts": quest_data.get("recommended_parts", [])
            }
            
            await db.execute(
                """INSERT INTO quests (name_ru, name_en, description_ru, description_en, required_builds)
                   VALUES (?, ?, ?, ?, ?)""",
                (quest_data.get("name_ru"), quest_data.get("name_en"),
                 quest_data.get("description_ru"), quest_data.get("description_en"),
                 json.dumps(extra_data))
            )
        
        await db.commit()
    print(f"   ✅ Загружено {len(quests)} квестов")
    print()
    
    # Шаг 3: Загрузка мета-сборок
    print("⚔️  ШАГ 3/4: Загрузка мета-сборок...")
    
    async def find_weapon_id(conn, weapon_name: str):
        async with conn.execute(
            "SELECT id FROM weapons WHERE name_en LIKE ? OR name_ru LIKE ? LIMIT 1",
            (f"%{weapon_name}%", f"%{weapon_name}%")
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None
    
    async with aiosqlite.connect(db_path) as db:
        added_meta = 0
        
        for weapon_name, builds in META_BUILDS.items():
            weapon_id = await find_weapon_id(db, weapon_name)
            
            if not weapon_id:
                continue
            
            for build_type, build_data in builds.items():
                category = BuildCategory.META.value if build_type == "meta" else BuildCategory.RANDOM.value
                
                await db.execute(
                    """INSERT INTO builds 
                    (weapon_id, category, name_ru, name_en, total_cost, min_loyalty_level, modules, planner_link)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (weapon_id, category, build_data.get("name_ru"), build_data.get("name_en"),
                     build_data.get("estimated_cost", 0), build_data.get("min_loyalty", 1),
                     json.dumps([]), None)
                )
                added_meta += 1
        
        await db.commit()
    print(f"   ✅ Загружено {added_meta} мета-сборок")
    print()
    
    # Шаг 4: Загрузка официальных preset'ов
    print("📦 ШАГ 4/4: Загрузка официальных preset'ов из tarkov.dev...")
    
    fetcher = BuildsFetcher()
    try:
        builds = await fetcher.fetch_from_tarkov_dev_presets()
        
        if builds:
            async with aiosqlite.connect(db_path) as db:
                added_presets = 0
                
                for build in builds[:50]:  # Ограничим 50 самыми популярными
                    weapon_name = build.get('weapon_name', '')
                    weapon_id = await find_weapon_id(db, weapon_name)
                    
                    if not weapon_id:
                        continue
                    
                    stats = build.get('stats', {})
                    cost = len(build.get('parts', [])) * 15000
                    
                    await db.execute(
                        """INSERT INTO builds 
                        (weapon_id, category, name_ru, name_en, total_cost, min_loyalty_level, modules, planner_link)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (weapon_id, BuildCategory.META.value, 
                         build.get('build_name'), build.get('build_name'),
                         cost, 2, json.dumps([]), None)
                    )
                    added_presets += 1
                
                await db.commit()
            print(f"   ✅ Загружено {added_presets} официальных preset'ов")
        else:
            print("   ⚠️  Preset'ы не загружены (возможно проблема с сетью)")
    finally:
        await fetcher.close()
    
    print()
    print("=" * 70)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 70)
    
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT COUNT(*) FROM weapons") as cursor:
            weapons_count = (await cursor.fetchone())[0]
        
        async with db.execute("SELECT COUNT(*) FROM modules") as cursor:
            modules_count = (await cursor.fetchone())[0]
        
        async with db.execute("SELECT COUNT(*) FROM builds") as cursor:
            builds_count = (await cursor.fetchone())[0]
        
        async with db.execute("SELECT COUNT(*) FROM quests") as cursor:
            quests_count = (await cursor.fetchone())[0]
        
        async with db.execute("SELECT COUNT(*) FROM traders") as cursor:
            traders_count = (await cursor.fetchone())[0]
    
    print(f"   🔫 Оружие:    {weapons_count}")
    print(f"   🔧 Модули:    {modules_count}")
    print(f"   📦 Сборки:    {builds_count}")
    print(f"   📜 Квесты:    {quests_count}")
    print(f"   🤝 Торговцы:  {traders_count}")
    print()
    print("=" * 70)
    print()
    print("✅ НАСТРОЙКА ЗАВЕРШЕНА!")
    print()
    print("🚀 Запустите бота командой:")
    print("   python start.py")
    print()
    print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(setup_complete())
    except KeyboardInterrupt:
        print("\n\n⚠️  Настройка прервана пользователем")
    except Exception as e:
        print(f"\n\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
