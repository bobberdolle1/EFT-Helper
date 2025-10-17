"""Script to sync weapon and module data from tarkov.dev API."""
import asyncio
import aiosqlite
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.tarkov_api import tarkov_api
from database import Database, WeaponCategory


# Map tarkov.dev categories to our internal categories
CATEGORY_MAPPING = {
    "pistol": WeaponCategory.PISTOL,
    "smg": WeaponCategory.SMG,
    "assault-rifle": WeaponCategory.ASSAULT_RIFLE,
    "assault-carbine": WeaponCategory.ASSAULT_RIFLE,
    "marksman-rifle": WeaponCategory.DMR,
    "sniper-rifle": WeaponCategory.SNIPER,
    "shotgun": WeaponCategory.SHOTGUN,
    "machine-gun": WeaponCategory.LMG,
}

# Tier ratings based on community consensus (can be updated)
TIER_RATINGS = {
    # S-Tier weapons
    "M4A1": "S",
    "HK 416A5": "S",
    "SCAR-L": "S",
    "MCX": "S",
    "SVD": "S",
    
    # A-Tier weapons
    "AK-74N": "A",
    "AK-74M": "A",
    "AKM": "A",
    "MP5": "A",
    "MPX": "A",
    "SR-25": "A",
    
    # B-Tier weapons
    "AK-105": "B",
    "SKS": "B",
    "MP-153": "B",
    "Saiga-12": "B",
    "PP-19-01": "B",
    
    # C-Tier weapons
    "Mosin": "C",
    "VPO-215": "C",
    "TOZ-106": "C",
}


async def sync_weapons_from_api(db: Database):
    """Sync weapons from tarkov.dev API to local database."""
    print("🔄 Загрузка оружия из tarkov.dev API...")
    
    weapons_data = await tarkov_api.get_all_weapons()
    
    if not weapons_data:
        print("❌ Не удалось загрузить оружие из API")
        return 0
    
    print(f"✅ Загружено {len(weapons_data)} оружий из API")
    print("   💾 Добавление в базу данных...")
    
    async with aiosqlite.connect(db.db_path) as conn:
        # Clear existing weapons (optional - comment out to keep existing data)
        # await conn.execute("DELETE FROM weapons")
        
        added_count = 0
        for weapon_data in weapons_data:
            name = weapon_data.get("shortName", weapon_data.get("name", "Unknown"))
            
            # Determine category from types
            category = WeaponCategory.ASSAULT_RIFLE  # Default
            types = weapon_data.get("types", [])
            for weapon_type in types:
                if weapon_type in CATEGORY_MAPPING:
                    category = CATEGORY_MAPPING[weapon_type]
                    break
            
            # Get tier rating
            tier_rating = TIER_RATINGS.get(name, None)
            
            # Get price
            price = weapon_data.get("avg24hPrice", 0) or 0
            
            # For now, use English name for both (we'll need Russian translations later)
            # In production, you'd fetch Russian translations from a localization service
            name_ru = name  # Placeholder
            name_en = name
            
            try:
                await conn.execute(
                    """INSERT OR REPLACE INTO weapons 
                    (name_ru, name_en, category, tier_rating, base_price) 
                    VALUES (?, ?, ?, ?, ?)""",
                    (name_ru, name_en, category.value, tier_rating, price)
                )
                added_count += 1
            except Exception as e:
                print(f"⚠️  Ошибка: {name} - {e}")
        
        await conn.commit()
        print(f"✅ Добавлено {added_count} оружий")
        return added_count


async def sync_attachments_from_api(db: Database):
    """Синхронизация модулей/модификаций из tarkov.dev API."""
    print("🔄 Загрузка модулей из tarkov.dev API...")
    
    # Загружаем модули через более простой запрос
    query = """
    {
        items(limit: 5000, types: mod) {
            id
            name
            shortName
            avg24hPrice
            types
        }
    }
    """
    
    try:
        data = await tarkov_api._make_graphql_request(query)
        all_items = data.get("items", []) if data else []
        
        # Если не получилось, попробуем без фильтра типа
        if not all_items:
            print("   Пробуем альтернативный метод...")
            query2 = """
            {
                items(limit: 3000) {
                    id
                    name
                    shortName
                    avg24hPrice
                    types
                }
            }
            """
            data = await tarkov_api._make_graphql_request(query2)
            if data and "items" in data:
                # Фильтруем только моды
                all_items = [
                    item for item in data["items"]
                    if any(t in ["mods", "suppressor", "sight", "scope", "stock", "grip", "magazine"] 
                           for t in item.get("types", []))
                ]
    except Exception as e:
        print(f"⚠️  Ошибка запроса: {e}")
        all_items = []
    
    if not all_items:
        print("⚠️  Не удалось загрузить модули")
        return 0
    
    print(f"✅ Загружено {len(all_items)} модулей")
    print("   💾 Добавление в базу...")
    
    import aiosqlite
    
    async with aiosqlite.connect(db.db_path) as conn:
        added_count = 0
        seen_ids = set()  # Avoid duplicates
        
        for item in all_items:
            item_id = item.get("id")
            if item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            name = item.get("shortName", item.get("name", "Unknown"))
            price = item.get("avg24hPrice", 0) or 0
            
            # Простой маппинг - можно улучшить
            slot_type = "universal"
            if "sight" in name.lower() or "scope" in name.lower():
                slot_type = "sight"
            elif "stock" in name.lower() or "приклад" in name.lower():
                slot_type = "stock"
            elif "grip" in name.lower() or "рукоят" in name.lower():
                slot_type = "grip"
            elif "suppressor" in name.lower() or "глушител" in name.lower():
                slot_type = "muzzle"
            elif "handguard" in name.lower() or "цевье" in name.lower():
                slot_type = "handguard"
            
            try:
                await conn.execute(
                    """INSERT OR REPLACE INTO modules 
                    (name_ru, name_en, price, trader, loyalty_level, slot_type) 
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (name, name, price, "Mechanic", 2, slot_type)
                )
                added_count += 1
            except Exception as e:
                pass  # Игнорируем ошибки
        
        await conn.commit()
        print(f"✅ Добавлено {added_count} модулей")
        return added_count


async def sync_traders_from_api(db: Database):
    """Синхронизация торговцев из tarkov.dev API."""
    print("🔄 Загрузка торговцев из tarkov.dev API...")
    
    traders_data = await tarkov_api.get_traders()
    
    if not traders_data:
        print("❌ Failed to fetch traders from API")
        return 0
    
    print(f"✅ Загружено {len(traders_data)} торговцев")
    
    trader_emojis = {
        "prapor": "🔫",
        "therapist": "💊",
        "fence": "🗑️",
        "skier": "💼",
        "peacekeeper": "🤝",
        "mechanic": "🔧",
        "ragman": "👕",
        "jaeger": "🌲"
    }
    
    async with aiosqlite.connect(db.db_path) as conn:
        added_count = 0
        for trader_data in traders_data:
            name = trader_data.get("name", "Unknown")
            normalized_name = trader_data.get("normalizedName", name.lower())
            emoji = trader_emojis.get(normalized_name, "💼")
            
            try:
                await conn.execute(
                    "INSERT OR IGNORE INTO traders (name, emoji) VALUES (?, ?)",
                    (name, emoji)
                )
                added_count += 1
            except Exception as e:
                print(f"⚠️  Error adding trader {name}: {e}")
        
        await conn.commit()
        print(f"✅ Добавлено {added_count} торговцев")
        return added_count


async def main():
    """Основная функция для запуска синхронизации."""
    print("=" * 60)
    print("  EFT Helper - Синхронизация с tarkov.dev API")
    print("=" * 60)
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "eft_helper.db")
    db = Database(db_path)
    await db.init_db()
    
    print("\n📊 Начало синхронизации...\n")
    
    traders_count = 0
    weapons_count = 0
    modules_count = 0
    
    # 1. Синхронизация торговцев
    print("👥 Шаг 1/3: Торговцы")
    traders_count = await sync_traders_from_api(db) or 0
    
    print()
    
    # 2. Синхронизация оружия
    print("🔫 Шаг 2/3: Оружие")
    weapons_count = await sync_weapons_from_api(db) or 0
    
    print()
    
    # 3. Синхронизация модулей
    print("🔧 Шаг 3/3: Модули/Модификации")
    modules_count = await sync_attachments_from_api(db) or 0
    
    print("\n" + "=" * 60)
    print("✅ Синхронизация завершена!")
    print("=" * 60)
    
    print("\n📊 Итого загружено:")
    print(f"   • Торговцы: {traders_count}")
    print(f"   • Оружие: {weapons_count}")
    print(f"   • Модули: {modules_count}")
    
    print("\n💡 Примечания:")
    print("   • Русские названия будут добавлены позднее")
    print("   • Сборки нужно создавать вручную или использовать populate_db.py")
    print("   • Данные кэшируются на 24 часа")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
