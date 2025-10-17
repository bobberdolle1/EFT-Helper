"""Автоматическая загрузка сборок с популярных сайтов."""
import aiohttp
import asyncio
from typing import List, Dict, Optional
import json


class BuildsFetcher:
    """Загрузка сборок с внешних источников."""
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self):
        """Получить aiohttp сессию."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Закрыть сессию."""
        if self.session:
            await self.session.close()
    
    async def fetch_from_tarkov_tools(self) -> List[Dict]:
        """
        Загрузить популярные сборки с tarkov-tools.com.
        
        Returns:
            Список сборок в формате:
            {
                'weapon_name': str,
                'build_name': str,
                'parts': List[str],
                'stats': {
                    'ergonomics': float,
                    'recoil': float,
                    'weight': float
                },
                'cost': int,
                'source': 'tarkov-tools.com',
                'url': str
            }
        """
        builds = []
        session = await self._get_session()
        
        # Список популярных оружий для парсинга
        weapons_to_fetch = [
            'ak-74m', 'm4a1', 'hk-416', 'akm', 'sr-25', 
            'as-val', 'vss', 'mp5', 'dvl-10', 'mosin'
        ]
        
        for weapon in weapons_to_fetch:
            try:
                url = f"https://www.tarkov-tools.com/weapon/{weapon}"
                
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Здесь нужен парсинг HTML
                        # Пример структуры (нужно адаптировать под реальный сайт)
                        # soup = BeautifulSoup(html, 'html.parser')
                        # ... парсинг ...
                        
                        print(f"✅ Загружено: {weapon}")
                        await asyncio.sleep(1)  # Пауза между запросами
                    else:
                        print(f"⚠️  Ошибка {response.status} для {weapon}")
            except Exception as e:
                print(f"❌ Ошибка загрузки {weapon}: {e}")
                continue
        
        return builds
    
    async def fetch_from_eft_monster(self) -> List[Dict]:
        """
        Загрузить сборки с eft.monster.
        
        Этот сайт содержит готовые preset'ы оружия.
        """
        builds = []
        session = await self._get_session()
        
        try:
            # API endpoint (если есть) или парсинг страницы
            url = "https://eft.monster/presets"
            
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    # Парсинг данных
                    pass
        except Exception as e:
            print(f"Ошибка загрузки с eft.monster: {e}")
        
        return builds
    
    async def fetch_from_tarkov_dev_presets(self) -> List[Dict]:
        """
        Загрузить дефолтные preset'ы из tarkov.dev API.
        
        Это самый надежный источник - официальные preset'ы из игры.
        """
        builds = []
        
        query = """
        {
            itemsByType(type: preset) {
                id
                name
                shortName
                baseItem {
                    id
                    name
                    shortName
                }
                properties {
                    ... on ItemPropertiesPreset {
                        baseItem {
                            id
                            name
                        }
                        ergonomics
                        recoilVertical
                        recoilHorizontal
                        moa
                    }
                }
                containsItems {
                    item {
                        id
                        name
                        shortName
                    }
                    count
                }
            }
        }
        """
        
        session = await self._get_session()
        
        try:
            async with session.post(
                "https://api.tarkov.dev/graphql",
                json={"query": query},
                timeout=30
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data and "data" in data:
                        presets = data["data"].get("itemsByType", [])
                        
                        for preset in presets:
                            props = preset.get("properties", {})
                            base_item = preset.get("baseItem", {})
                            
                            build = {
                                'weapon_name': base_item.get("name", "Unknown"),
                                'build_name': preset.get("name", "Preset"),
                                'preset_id': preset.get("id"),
                                'parts': [
                                    item.get("item", {}).get("name", "")
                                    for item in preset.get("containsItems", [])
                                ],
                                'stats': {
                                    'ergonomics': props.get("ergonomics", 0),
                                    'vertical_recoil': props.get("recoilVertical", 0),
                                    'horizontal_recoil': props.get("recoilHorizontal", 0),
                                    'moa': props.get("moa", 0)
                                },
                                'source': 'tarkov.dev',
                                'official': True  # Официальные preset'ы из игры
                            }
                            builds.append(build)
                        
                        print(f"✅ Загружено {len(builds)} официальных preset'ов")
                else:
                    print(f"⚠️  Ошибка API: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка загрузки preset'ов: {e}")
        
        return builds
    
    async def fetch_all_builds(self) -> List[Dict]:
        """Загрузить сборки из всех источников."""
        all_builds = []
        
        print("🔄 Загрузка сборок из всех источников...")
        print()
        
        # 1. Официальные preset'ы из tarkov.dev (самый надежный)
        print("📦 Загрузка официальных preset'ов...")
        presets = await self.fetch_from_tarkov_dev_presets()
        all_builds.extend(presets)
        
        # 2. Можно добавить другие источники
        # tarkov_tools = await self.fetch_from_tarkov_tools()
        # all_builds.extend(tarkov_tools)
        
        print()
        print(f"✅ Всего загружено сборок: {len(all_builds)}")
        
        return all_builds


async def test_fetcher():
    """Тестовая функция."""
    fetcher = BuildsFetcher()
    
    try:
        builds = await fetcher.fetch_all_builds()
        
        print("\n📊 Примеры загруженных сборок:")
        for build in builds[:5]:
            print(f"  • {build['weapon_name']}: {build['build_name']}")
    finally:
        await fetcher.close()


if __name__ == "__main__":
    asyncio.run(test_fetcher())
