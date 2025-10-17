"""Автоматическая синхронизация сборок с расчетом характеристик."""
import asyncio
import aiosqlite
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.builds_fetcher import BuildsFetcher
from utils.build_calculator import BuildCalculator
from database import BuildCategory


async def find_or_create_weapon(conn, weapon_name: str):
    """Найти или создать оружие в БД."""
    # Пробуем найти
    async with conn.execute(
        "SELECT id FROM weapons WHERE name_en LIKE ? OR name_ru LIKE ? LIMIT 1",
        (f"%{weapon_name}%", f"%{weapon_name}%")
    ) as cursor:
        result = await cursor.fetchone()
        if result:
            return result[0]
    
    # Создаем новое (базовая запись)
    await conn.execute(
        "INSERT INTO weapons (name_en, name_ru, category, tier_rating, base_price) VALUES (?, ?, ?, ?, ?)",
        (weapon_name, weapon_name, "unknown", "B", 0)
    )
    await conn.commit()
    
    # Получаем ID
    async with conn.execute("SELECT last_insert_rowid()") as cursor:
        result = await cursor.fetchone()
        return result[0] if result else None


async def sync_builds_from_sources():
    """Синхронизация сборок из всех источников."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "eft_helper.db")
    
    print("=" * 60)
    print("  Автоматическая синхронизация сборок")
    print("=" * 60)
    print()
    
    # Загружаем сборки
    fetcher = BuildsFetcher()
    
    try:
        builds = await fetcher.fetch_all_builds()
        
        if not builds:
            print("⚠️  Не удалось загрузить сборки")
            return
        
        print(f"\n📦 Обработка {len(builds)} сборок...")
        print()
        
        async with aiosqlite.connect(db_path) as db:
            added = 0
            updated = 0
            skipped = 0
            
            for build in builds:
                try:
                    weapon_name = build.get('weapon_name', 'Unknown')
                    build_name = build.get('build_name', 'Unnamed')
                    
                    # Найти или создать оружие
                    weapon_id = await find_or_create_weapon(db, weapon_name)
                    
                    if not weapon_id:
                        print(f"  ⚠️  Пропущено: {weapon_name}")
                        skipped += 1
                        continue
                    
                    # Подготовить данные
                    stats = build.get('stats', {})
                    parts = build.get('parts', [])
                    
                    # Рассчитать примерную стоимость
                    estimated_cost = len(parts) * 15000  # Примерная оценка
                    
                    # Определить категорию
                    if build.get('official'):
                        category = BuildCategory.META.value  # Официальные preset'ы - мета
                    else:
                        category = BuildCategory.RANDOM.value
                    
                    # Сформировать описание с характеристиками
                    description_ru = f"""
📊 Характеристики:
• Эргономика: {stats.get('ergonomics', 'N/A')}
• Вертикальная отдача: {stats.get('vertical_recoil', 'N/A')}
• Горизонтальная отдача: {stats.get('horizontal_recoil', 'N/A')}
• MOA: {stats.get('moa', 'N/A')}

🔧 Модулей: {len(parts)}
"""
                    
                    # Проверить, существует ли уже такая сборка
                    async with db.execute(
                        "SELECT id FROM builds WHERE weapon_id = ? AND name_en = ?",
                        (weapon_id, build_name)
                    ) as cursor:
                        existing = await cursor.fetchone()
                    
                    if existing:
                        # Обновить существующую
                        await db.execute(
                            """UPDATE builds SET 
                            total_cost = ?, 
                            modules = ?,
                            planner_link = ?
                            WHERE id = ?""",
                            (estimated_cost, json.dumps([]), build.get('url'), existing[0])
                        )
                        updated += 1
                        status = "🔄"
                    else:
                        # Добавить новую
                        await db.execute(
                            """INSERT INTO builds 
                            (weapon_id, category, name_ru, name_en, total_cost, min_loyalty_level, modules, planner_link)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (weapon_id, category, build_name, build_name, estimated_cost, 2, json.dumps([]), build.get('url'))
                        )
                        added += 1
                        status = "✅"
                    
                    print(f"  {status} {weapon_name}: {build_name}")
                    
                except Exception as e:
                    print(f"  ❌ Ошибка: {e}")
                    skipped += 1
                    continue
            
            await db.commit()
            
            print()
            print("=" * 60)
            print("📊 Статистика синхронизации:")
            print(f"   ✅ Добавлено: {added}")
            print(f"   🔄 Обновлено: {updated}")
            print(f"   ⚠️  Пропущено: {skipped}")
            print(f"   📦 Всего обработано: {len(builds)}")
            print()
            
            # Статистика БД
            async with db.execute("SELECT COUNT(*) FROM builds") as cursor:
                total_builds = (await cursor.fetchone())[0]
            print(f"📈 Всего сборок в БД: {total_builds}")
            print("=" * 60)
    
    finally:
        await fetcher.close()


async def main():
    """Главная функция."""
    try:
        await sync_builds_from_sources()
        print("\n✅ Синхронизация завершена успешно!")
    except Exception as e:
        print(f"\n❌ Ошибка синхронизации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
