"""Load quest builds from quest_builds_data.py into database."""
import asyncio
import aiosqlite
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.quest_builds_data import get_all_quests


async def load_quests_to_db():
    """Load all quest builds into database."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "eft_helper.db")
    
    print("=" * 60)
    print("  Загрузка квестовых сборок в БД")
    print("=" * 60)
    print()
    
    quests = get_all_quests()
    
    async with aiosqlite.connect(db_path) as db:
        # Clear existing quests
        await db.execute("DELETE FROM quests")
        
        added = 0
        for quest_id, quest_data in quests.items():
            name_ru = quest_data.get("name_ru")
            name_en = quest_data.get("name_en")
            desc_ru = quest_data.get("description_ru")
            desc_en = quest_data.get("description_en")
            
            # Store additional data as JSON
            extra_data = {
                "trader": quest_data.get("trader"),
                "level_required": quest_data.get("level_required"),
                "weapon": quest_data.get("weapon"),
                "requirements": quest_data.get("requirements"),
                "recommended_parts": quest_data.get("recommended_parts", []),
                "recommended_weapons": quest_data.get("recommended_weapons", [])
            }
            
            await db.execute(
                """INSERT INTO quests (name_ru, name_en, description_ru, description_en, required_builds)
                   VALUES (?, ?, ?, ?, ?)""",
                (name_ru, name_en, desc_ru, desc_en, json.dumps(extra_data))
            )
            added += 1
            print(f"  ✅ {name_ru}")
        
        await db.commit()
        
        print()
        print(f"📊 Добавлено квестов: {added}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(load_quests_to_db())
