"""Service for synchronizing data from tarkov.dev API to database."""
import logging
import aiosqlite
from typing import Dict, List
from database import Database, WeaponCategory
from api_clients import TarkovAPIClient

logger = logging.getLogger(__name__)


# Map tarkov.dev categories to internal categories
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

# Tier ratings (can be customized)
TIER_RATINGS = {
    # S-Tier weapons
    "M4A1": "S", "HK 416A5": "S", "SCAR-L": "S", "MCX": "S", "SVD": "S",
    # A-Tier weapons
    "AK-74N": "A", "AK-74M": "A", "AKM": "A", "MP5": "A", "MPX": "A", "SR-25": "A",
    # B-Tier weapons
    "AK-105": "B", "SKS": "B", "MP-153": "B", "Saiga-12": "B", "PP-19-01": "B",
    # C-Tier weapons
    "Mosin": "C", "VPO-215": "C", "TOZ-106": "C",
}

TRADER_EMOJIS = {
    "prapor": "🔫", "therapist": "💊", "fence": "🗑️", "skier": "💼",
    "peacekeeper": "🤝", "mechanic": "🔧", "ragman": "👕", "jaeger": "🌲"
}


class SyncService:
    """Service for syncing data from tarkov.dev API to local database."""
    
    def __init__(self, db: Database, api_client: TarkovAPIClient):
        self.db = db
        self.api = api_client
    
    async def sync_traders(self) -> int:
        """Sync traders from API to database."""
        logger.info("Syncing traders from tarkov.dev API...")
        
        traders_data = await self.api.get_all_traders()
        if not traders_data:
            logger.warning("No traders data received from API")
            return 0
        
        async with aiosqlite.connect(self.db.db_path) as conn:
            added_count = 0
            for trader_data in traders_data:
                name = trader_data.get("name", "Unknown")
                normalized_name = trader_data.get("normalizedName", name.lower())
                emoji = TRADER_EMOJIS.get(normalized_name, "💼")
                
                try:
                    await conn.execute(
                        "INSERT OR IGNORE INTO traders (name, emoji) VALUES (?, ?)",
                        (name, emoji)
                    )
                    added_count += 1
                except Exception as e:
                    logger.error(f"Error adding trader {name}: {e}")
            
            await conn.commit()
            logger.info(f"Synced {added_count} traders")
            return added_count
    
    async def sync_weapons(self) -> int:
        """Sync weapons from API to database."""
        logger.info("Syncing weapons from tarkov.dev API...")
        
        weapons_data = await self.api.get_all_weapons()
        if not weapons_data:
            logger.warning("No weapons data received from API")
            return 0
        
        async with aiosqlite.connect(self.db.db_path) as conn:
            added_count = 0
            for weapon_data in weapons_data:
                name = weapon_data.get("shortName", weapon_data.get("name", "Unknown"))
                
                # Determine category
                category = WeaponCategory.ASSAULT_RIFLE  # Default
                types = weapon_data.get("types", [])
                for weapon_type in types:
                    if weapon_type in CATEGORY_MAPPING:
                        category = CATEGORY_MAPPING[weapon_type]
                        break
                
                tier_rating = TIER_RATINGS.get(name, None)
                price = weapon_data.get("avg24hPrice", 0) or 0
                
                # Extract properties
                properties = weapon_data.get("properties", {})
                caliber = properties.get("caliber", None)
                ergonomics = properties.get("ergonomics", None)
                recoil_vertical = properties.get("recoilVertical", None)
                recoil_horizontal = properties.get("recoilHorizontal", None)
                fire_rate = properties.get("fireRate", None)
                
                # Calculate effective range based on caliber
                effective_range = self._calculate_effective_range(caliber)
                
                try:
                    await conn.execute(
                        """INSERT OR REPLACE INTO weapons 
                        (name_ru, name_en, category, tier_rating, base_price,
                         caliber, ergonomics, recoil_vertical, recoil_horizontal, fire_rate, effective_range) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (name, name, category.value, tier_rating, price,
                         caliber, ergonomics, recoil_vertical, recoil_horizontal, fire_rate, effective_range)
                    )
                    added_count += 1
                except Exception as e:
                    logger.error(f"Error adding weapon {name}: {e}")
            
            await conn.commit()
            logger.info(f"Synced {added_count} weapons")
            return added_count
    
    async def sync_modules(self) -> int:
        """Sync weapon modules/attachments from API to database."""
        logger.info("Syncing modules from tarkov.dev API...")
        
        mods_data = await self.api.get_all_mods()
        if not mods_data:
            logger.warning("No mods data received from API")
            return 0
        
        async with aiosqlite.connect(self.db.db_path) as conn:
            added_count = 0
            seen_ids = set()
            
            for mod in mods_data:
                mod_id = mod.get("id")
                if mod_id in seen_ids:
                    continue
                seen_ids.add(mod_id)
                
                name = mod.get("shortName", mod.get("name", "Unknown"))
                price = mod.get("avg24hPrice", 0) or 0
                
                # Determine slot type
                slot_type = self._determine_slot_type(name, mod.get("types", []))
                
                # Get trader info from sellFor
                trader = "Mechanic"
                loyalty_level = 2
                sell_for = mod.get("sellFor", [])
                if sell_for:
                    for sale in sell_for:
                        vendor = sale.get("vendor", {})
                        if vendor:
                            trader = vendor.get("name", "Mechanic")
                            loyalty_level = vendor.get("minTraderLevel", 2)
                            break
                
                try:
                    await conn.execute(
                        """INSERT OR REPLACE INTO modules 
                        (name_ru, name_en, price, trader, loyalty_level, slot_type) 
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (name, name, price, trader, loyalty_level, slot_type)
                    )
                    added_count += 1
                except Exception as e:
                    logger.debug(f"Error adding module {name}: {e}")
            
            await conn.commit()
            logger.info(f"Synced {added_count} modules")
            return added_count
    
    async def sync_all(self) -> Dict[str, int]:
        """
        Sync all data from tarkov.dev API.
        
        Returns:
            Dictionary with counts of synced items
        """
        logger.info("Starting full sync from tarkov.dev API...")
        
        results = {
            "traders": 0,
            "weapons": 0,
            "modules": 0
        }
        
        # Sync in order: traders -> weapons -> modules
        results["traders"] = await self.sync_traders()
        results["weapons"] = await self.sync_weapons()
        results["modules"] = await self.sync_modules()
        
        logger.info(f"Full sync completed: {results}")
        return results
    
    def _calculate_effective_range(self, caliber: Optional[str]) -> Optional[int]:
        """Calculate effective range based on caliber."""
        if not caliber:
            return None
        
        caliber_lower = caliber.lower()
        
        if any(x in caliber_lower for x in ["7.62x54", "7.62x51", ".308", "12.7x108"]):
            return 800  # Sniper calibers
        elif any(x in caliber_lower for x in ["5.56x45", "5.45x39", "7.62x39"]):
            return 400  # Rifle calibers
        elif any(x in caliber_lower for x in ["9x19", "9x18", ".45", "9x21"]):
            return 100  # Pistol calibers
        elif "12ga" in caliber_lower or "20ga" in caliber_lower:
            return 50   # Shotgun
        
        return None
    
    def _determine_slot_type(self, name: str, types: List[str]) -> str:
        """Determine module slot type from name and types."""
        name_lower = name.lower()
        
        if "sight" in name_lower or "scope" in name_lower or any(t in types for t in ["sight", "scope"]):
            return "sight"
        elif "stock" in name_lower or "приклад" in name_lower or "stock" in types:
            return "stock"
        elif "grip" in name_lower or "рукоят" in name_lower or "grip" in types:
            return "grip"
        elif "suppressor" in name_lower or "глушител" in name_lower or "suppressor" in types:
            return "muzzle"
        elif "handguard" in name_lower or "цевье" in name_lower:
            return "handguard"
        elif "magazine" in name_lower or "mag" in name_lower or "magazine" in types:
            return "magazine"
        
        return "universal"
