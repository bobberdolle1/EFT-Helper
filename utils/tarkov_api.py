"""Tarkov.dev API integration for EFT Helper bot."""
import asyncio
import aiohttp
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .constants import TARKOV_DEV_API_URL, TARKOV_MARKET_API_URL, API_CACHE_DURATION_HOURS

logger = logging.getLogger(__name__)


class TarkovAPI:
    """Client for multiple Tarkov APIs."""
    
    def __init__(self, market_api_key: Optional[str] = None):
        self.cache = {}
        self.cache_duration = timedelta(hours=API_CACHE_DURATION_HOURS)
        self.market_api_key = market_api_key  # Опционально для tarkov-market.com
        self.tarkov_dev_api = TARKOV_DEV_API_URL
        self.tarkov_market_api = TARKOV_MARKET_API_URL
    
    async def _make_graphql_request(self, query: str) -> Optional[Dict]:
        """Make GraphQL request to tarkov.dev API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.tarkov_dev_api,
                    json={"query": query},
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data")
                    else:
                        logger.warning(f"Tarkov.dev API returned status {response.status}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Tarkov.dev API connection error: {e}")
            return None
        except asyncio.TimeoutError:
            logger.error("Tarkov.dev API request timeout")
            return None
        except Exception as e:
            logger.error(f"Tarkov.dev API unexpected error: {e}", exc_info=True)
            return None
    
    async def _make_rest_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make REST request to tarkov-market.com API."""
        if not self.market_api_key:
            logger.debug("Tarkov-Market API key not configured")
            return None
        
        try:
            headers = {
                "x-api-key": self.market_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.tarkov_market_api}/{endpoint}",
                    headers=headers,
                    params=params or {},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"Tarkov-Market API returned status {response.status}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Tarkov-Market API connection error: {e}")
            return None
        except asyncio.TimeoutError:
            logger.error("Tarkov-Market API request timeout")
            return None
        except Exception as e:
            logger.error(f"Tarkov-Market API unexpected error: {e}", exc_info=True)
            return None
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get("timestamp")
        if not cached_time:
            return False
        
        return datetime.now() - cached_time < self.cache_duration
    
    async def get_all_weapons(self) -> List[Dict]:
        """Get all weapons from tarkov.dev API."""
        cache_key = "all_weapons"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        query = """
        {
            items(types: [gun]) {
                id
                name
                shortName
                normalizedName
                types
                avg24hPrice
                category {
                    id
                    name
                }
                properties {
                    ... on ItemPropertiesWeapon {
                        caliber
                        ergonomics
                        recoilVertical
                        recoilHorizontal
                        fireRate
                    }
                }
            }
        }
        """
        
        data = await self._make_graphql_request(query)
        if data and "items" in data:
            weapons = data["items"]
            self.cache[cache_key] = {
                "data": weapons,
                "timestamp": datetime.now()
            }
            return weapons
        
        return []
    
    async def get_weapon_by_name(self, name: str, language: str = "en") -> Optional[Dict]:
        """Search weapon by name (supports both English and Russian)."""
        all_weapons = await self.get_all_weapons()
        
        # Normalize search query
        search_term = name.lower().strip()
        
        for weapon in all_weapons:
            weapon_name = weapon.get("name", "").lower()
            weapon_short = weapon.get("shortName", "").lower()
            weapon_normalized = weapon.get("normalizedName", "").lower()
            
            if (search_term in weapon_name or 
                search_term in weapon_short or 
                search_term in weapon_normalized):
                return weapon
        
        return None
    
    async def get_traders(self) -> List[Dict]:
        """Get all traders information."""
        cache_key = "traders"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        query = """
        {
            traders {
                id
                name
                normalizedName
                resetTime
                levels {
                    level
                    requiredPlayerLevel
                    requiredReputation
                }
            }
        }
        """
        
        data = await self._make_graphql_request(query)
        if data and "traders" in data:
            traders = data["traders"]
            self.cache[cache_key] = {
                "data": traders,
                "timestamp": datetime.now()
            }
            return traders
        
        return []
    
    async def get_items_by_trader(self, trader_name: str, loyalty_level: int) -> List[Dict]:
        """Get items available from specific trader at loyalty level."""
        query = f"""
        {{
            items(traderName: "{trader_name}", minTraderLevel: {loyalty_level}) {{
                id
                name
                shortName
                types
                avg24hPrice
                sellFor {{
                    vendor {{
                        name
                        normalizedName
                        minTraderLevel
                    }}
                    price
                    currency
                }}
            }}
        }}
        """
        
        data = await self._make_graphql_request(query)
        if data and "items" in data:
            return data["items"]
        
        return []
    
    async def get_weapon_attachments(self, weapon_id: str) -> List[Dict]:
        """Get compatible attachments for a weapon."""
        query = f"""
        {{
            item(id: "{weapon_id}") {{
                id
                name
                properties {{
                    ... on ItemPropertiesWeapon {{
                        slots {{
                            name
                            nameId
                            filters {{
                                allowedItems {{
                                    id
                                    name
                                    shortName
                                    avg24hPrice
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        
        data = await self._make_graphql_request(query)
        if data and "item" in data:
            return data["item"]
        
        return []
    
    async def get_market_prices(self) -> Dict[str, int]:
        """Get current flea market prices for all items."""
        cache_key = "market_prices"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        query = """
        {
            items {
                id
                name
                avg24hPrice
                lastLowPrice
                changeLast48hPercent
            }
        }
        """
        
        data = await self._make_graphql_request(query)
        if data and "items" in data:
            prices = {
                item["id"]: item.get("avg24hPrice", 0) 
                for item in data["items"]
            }
            self.cache[cache_key] = {
                "data": prices,
                "timestamp": datetime.now()
            }
            return prices
        
        return {}
    
    async def search_items(self, search_term: str, item_types: Optional[List[str]] = None) -> List[Dict]:
        """Search items by name and optionally filter by types."""
        types_filter = ""
        if item_types:
            types_str = ", ".join([f'"{t}"' for t in item_types])
            types_filter = f"types: [{types_str}]"
        
        query = f"""
        {{
            items({types_filter}) {{
                id
                name
                shortName
                normalizedName
                types
                avg24hPrice
                category {{
                    name
                }}
            }}
        }}
        """
        
        data = await self._make_graphql_request(query)
        if data and "items" in data:
            items = data["items"]
            
            # Filter by search term
            if search_term:
                search_lower = search_term.lower()
                items = [
                    item for item in items
                    if (search_lower in item.get("name", "").lower() or
                        search_lower in item.get("shortName", "").lower() or
                        search_lower in item.get("normalizedName", "").lower())
                ]
            
            return items
        
        return []


    async def get_all_items_from_market(self) -> List[Dict]:
        """Get all items from Tarkov Market API."""
        cache_key = "market_all_items"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        data = await self._make_rest_request("items/all")
        if data:
            self.cache[cache_key] = {
                "data": data,
                "timestamp": datetime.now()
            }
            return data
        
        return []
    
    async def get_item_price_from_market(self, item_uid: str) -> Optional[Dict]:
        """Get item price from Tarkov Market API."""
        data = await self._make_rest_request(f"item", {"uid": item_uid})
        return data
    
    async def get_all_ammo(self) -> List[Dict]:
        """Get all ammunition from tarkov.dev."""
        cache_key = "all_ammo"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        query = """
        {
            ammo {
                item {
                    id
                    name
                    shortName
                    avg24hPrice
                }
                caliber
                damage
                penetrationPower
                armorDamage
            }
        }
        """
        
        data = await self._make_graphql_request(query)
        if data and "ammo" in data:
            ammo_list = data["ammo"]
            self.cache[cache_key] = {
                "data": ammo_list,
                "timestamp": datetime.now()
            }
            return ammo_list
        
        return []
    
    async def get_all_armor(self) -> List[Dict]:
        """Get all armor from tarkov.dev."""
        cache_key = "all_armor"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        query = """
        {
            items(types: [armor, helmet, armoredRig]) {
                id
                name
                shortName
                avg24hPrice
                properties {
                    ... on ItemPropertiesArmor {
                        class
                        durability
                        material {
                            name
                        }
                        zones
                    }
                }
            }
        }
        """
        
        data = await self._make_graphql_request(query)
        if data and "items" in data:
            armor_list = data["items"]
            self.cache[cache_key] = {
                "data": armor_list,
                "timestamp": datetime.now()
            }
            return armor_list
        
        return []


# Global API instance
tarkov_api = TarkovAPI()
