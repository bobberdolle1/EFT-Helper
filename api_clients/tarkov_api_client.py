"""Unified Tarkov API client with caching."""
import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TarkovAPIClient:
    """
    Centralized client for tarkov.dev API.
    All external API calls MUST go through this client.
    """
    
    def __init__(self, api_url: str = "https://api.tarkov.dev/graphql", cache_duration_hours: int = 24):
        self.api_url = api_url
        self.cache = {}
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get("timestamp")
        if not cached_time:
            return False
        
        return datetime.now() - cached_time < self.cache_duration
    
    def _get_cached(self, cache_key: str) -> Optional[any]:
        """Get data from cache if valid."""
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        return None
    
    def _set_cache(self, cache_key: str, data: any):
        """Store data in cache."""
        self.cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    async def _make_graphql_request(self, query: str) -> Optional[Dict]:
        """Make GraphQL request to tarkov.dev API."""
        try:
            session = await self._get_session()
            async with session.post(
                self.api_url,
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
    
    async def get_all_weapons(self) -> List[Dict]:
        """
        Get all weapons from tarkov.dev API.
        Result is cached for 24 hours.
        """
        cache_key = "all_weapons"
        cached = self._get_cached(cache_key)
        if cached is not None:
            logger.debug("Returning cached weapons data")
            return cached
        
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
            self._set_cache(cache_key, weapons)
            logger.info(f"Fetched {len(weapons)} weapons from API")
            return weapons
        
        return []
    
    async def get_all_traders(self) -> List[Dict]:
        """Get all traders information."""
        cache_key = "traders"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
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
            self._set_cache(cache_key, traders)
            logger.info(f"Fetched {len(traders)} traders from API")
            return traders
        
        return []
    
    async def get_all_mods(self) -> List[Dict]:
        """Get all weapon modifications."""
        cache_key = "all_mods"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        query = """
        {
            items(limit: 5000, types: [mods, suppressor, sight, scope, stock, grip, magazine]) {
                id
                name
                shortName
                avg24hPrice
                types
                sellFor {
                    vendor {
                        name
                        normalizedName
                        minTraderLevel
                    }
                    price
                    currency
                }
            }
        }
        """
        
        data = await self._make_graphql_request(query)
        if data and "items" in data:
            mods = data["items"]
            self._set_cache(cache_key, mods)
            logger.info(f"Fetched {len(mods)} mods from API")
            return mods
        
        return []
    
    async def get_market_prices(self) -> Dict[str, int]:
        """Get current flea market prices for all items."""
        cache_key = "market_prices"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        query = """
        {
            items {
                id
                name
                avg24hPrice
                lastLowPrice
            }
        }
        """
        
        data = await self._make_graphql_request(query)
        if data and "items" in data:
            prices = {
                item["id"]: item.get("avg24hPrice", 0) 
                for item in data["items"]
            }
            self._set_cache(cache_key, prices)
            logger.info(f"Fetched prices for {len(prices)} items from API")
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
    
    def clear_cache(self):
        """Clear all cached data."""
        self.cache.clear()
        logger.info("API cache cleared")
