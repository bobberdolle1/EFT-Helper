"""Build-related business logic."""
import logging
import random
from typing import List, Optional
from database import Database, Build, BuildCategory, Module, Weapon
from api_clients import TarkovAPIClient

logger = logging.getLogger(__name__)


class BuildService:
    """Service for weapon build operations."""
    
    def __init__(self, db: Database, api_client: TarkovAPIClient):
        self.db = db
        self.api = api_client
    
    async def get_build_with_details(self, build_id: int) -> Optional[dict]:
        """
        Get build with weapon and modules details.
        
        Returns:
            Dictionary with build, weapon, and modules data
        """
        build = await self.db.get_build_by_id(build_id)
        if not build:
            return None
        
        weapon = await self.db.get_weapon_by_id(build.weapon_id)
        modules = await self.db.get_modules_by_ids(build.modules)
        
        return {
            "build": build,
            "weapon": weapon,
            "modules": modules
        }
    
    async def get_builds_for_weapon(
        self, 
        weapon_id: int, 
        category: Optional[BuildCategory] = None
    ) -> List[dict]:
        """
        Get all builds for a weapon with full details.
        
        Args:
            weapon_id: Weapon ID
            category: Optional filter by build category
            
        Returns:
            List of builds with weapon and modules
        """
        builds = await self.db.get_builds_by_weapon(weapon_id, category)
        
        result = []
        for build in builds:
            weapon = await self.db.get_weapon_by_id(build.weapon_id)
            modules = await self.db.get_modules_by_ids(build.modules)
            result.append({
                "build": build,
                "weapon": weapon,
                "modules": modules
            })
        
        return result
    
    async def get_random_build(self) -> Optional[dict]:
        """Get a random build with details."""
        build = await self.db.get_random_build()
        if not build:
            return None
        
        weapon = await self.db.get_weapon_by_id(build.weapon_id)
        modules = await self.db.get_modules_by_ids(build.modules)
        
        return {
            "build": build,
            "weapon": weapon,
            "modules": modules
        }
    
    async def get_meta_builds(self) -> List[dict]:
        """Get all meta builds with details."""
        builds = await self.db.get_meta_builds()
        
        result = []
        for build in builds:
            weapon = await self.db.get_weapon_by_id(build.weapon_id)
            modules = await self.db.get_modules_by_ids(build.modules)
            result.append({
                "build": build,
                "weapon": weapon,
                "modules": modules
            })
        
        return result
    
    async def get_quest_builds(self) -> List[dict]:
        """Get all quest builds with details."""
        builds = await self.db.get_quest_builds()
        
        result = []
        for build in builds:
            weapon = await self.db.get_weapon_by_id(build.weapon_id)
            modules = await self.db.get_modules_by_ids(build.modules)
            result.append({
                "build": build,
                "weapon": weapon,
                "modules": modules
            })
        
        return result
    
    async def get_builds_by_loyalty(
        self, 
        trader_levels: dict
    ) -> List[dict]:
        """
        Get builds available based on user's trader loyalty levels.
        
        Args:
            trader_levels: Dictionary of trader loyalty levels
            
        Returns:
            List of available builds
        """
        all_builds = await self.db.get_meta_builds()
        available_builds = []
        
        for build in all_builds:
            modules = await self.db.get_modules_by_ids(build.modules)
            
            # Check if all modules are available at user's loyalty levels
            is_available = True
            for module in modules:
                trader_name_lower = module.trader.lower()
                user_level = trader_levels.get(trader_name_lower, 1)
                
                if module.loyalty_level > user_level:
                    is_available = False
                    break
            
            if is_available:
                weapon = await self.db.get_weapon_by_id(build.weapon_id)
                available_builds.append({
                    "build": build,
                    "weapon": weapon,
                    "modules": modules
                })
        
        return available_builds
    
    async def calculate_build_cost(self, module_ids: List[int]) -> int:
        """Calculate total cost of a build."""
        modules = await self.db.get_modules_by_ids(module_ids)
        return sum(m.price for m in modules)
