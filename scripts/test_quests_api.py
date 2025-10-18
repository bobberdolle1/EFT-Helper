"""Test script to verify quest loading from API."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_clients import TarkovAPIClient


async def test_quests():
    """Test loading quests from API."""
    print("=" * 60)
    print("  Тест загрузки квестов из API")
    print("=" * 60)
    print()
    
    client = TarkovAPIClient()
    
    try:
        print("📡 Загружаю ВСЕ квесты из tarkov.dev API...")
        all_tasks = await client.get_all_tasks()
        
        if not all_tasks:
            print("❌ Не удалось загрузить квесты")
            return
        
        print(f"✅ Загружено всего квестов: {len(all_tasks)}")
        print()
        
        print("🔧 Фильтрую квесты связанные со сборками оружия...")
        build_tasks = await client.get_weapon_build_tasks()
        
        print(f"✅ Найдено квестов со сборками: {len(build_tasks)}")
        print()
        
        # Group by trader
        traders = {}
        for task in build_tasks:
            trader_data = task.get("trader")
            if not trader_data:
                continue
            trader_name = trader_data.get("name", "Unknown")
            if trader_name not in traders:
                traders[trader_name] = []
            traders[trader_name].append(task)
        
        print("📊 Квесты со сборками по торговцам:")
        for trader_name in sorted(traders.keys()):
            print(f"  {trader_name}: {len(traders[trader_name])} квестов")
        print()
        
        # Show all build quests
        print("📜 Все квесты со сборками:")
        for i, task in enumerate(build_tasks, 1):
            name = task.get("name", "Unknown")
            trader_data = task.get("trader", {})
            trader_name = trader_data.get("name", "Unknown") if trader_data else "Unknown"
            level = task.get("minPlayerLevel", "?")
            print(f"  {i}. {name} ({trader_name}, Lvl {level})")
        
        print()
        print("=" * 60)
        print(f"✅ Тест успешно завершен: {len(build_tasks)}/{len(all_tasks)} квестов")
        print("=" * 60)
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_quests())
