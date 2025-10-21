"""Context builder for AI assistant - prepares data from tarkov.dev for LLM."""
import logging
from typing import Dict, List, Optional
from api_clients import TarkovAPIClient
from database import Database

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds contextual data for LLM prompts."""
    
    def __init__(self, api_client: TarkovAPIClient, db: Database):
        self.api = api_client
        self.db = db
    
    async def build_weapon_context(self, weapon_id: Optional[str] = None, language: str = "ru") -> str:
        """
        Build context about weapons for LLM.
        
        Args:
            weapon_id: Specific weapon ID to focus on (optional)
            language: Language for names (ru/en)
            
        Returns:
            Formatted string with weapon information
        """
        if weapon_id:
            weapon_data = await self.api.get_weapon_details(weapon_id, lang=language)
            if not weapon_data:
                return ""
            
            return self._format_weapon_details(weapon_data, language)
        
        # Get all weapons for general context (limited to avoid token overflow)
        weapons = await self.api.get_all_weapons(lang=language)
        
        # Group by category and get top weapons per category
        categories = {}
        for weapon in weapons[:50]:  # Limit to 50 weapons
            cat_name = weapon.get("category", {}).get("name", "Unknown")
            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(weapon)
        
        context = "Available weapons by category:\n\n"
        for cat, weaps in categories.items():
            context += f"**{cat}:**\n"
            for w in weaps[:5]:  # Top 5 per category
                price = w.get("avg24hPrice", 0) or 0
                context += f"  - {w.get('name', 'Unknown')} (ID: {w.get('id')}, Price: {price:,} ₽)\n"
            context += "\n"
        
        return context
    
    async def build_modules_context(self, weapon_id: str, language: str = "ru") -> str:
        """
        Build context about available modules for a weapon.
        
        Args:
            weapon_id: Weapon ID to get modules for
            language: Language for names (ru/en)
            
        Returns:
            Formatted string with module information
        """
        weapon_data = await self.api.get_weapon_details(weapon_id, lang=language)
        if not weapon_data:
            return ""
        
        props = weapon_data.get("properties", {})
        slots = props.get("slots", [])
        
        if not slots:
            return "No modification slots available for this weapon."
        
        context = f"Modification slots for {weapon_data.get('name', 'weapon')}:\n\n"
        
        for slot in slots:
            slot_name = slot.get("name", "Unknown slot")
            slot_id = slot.get("nameId", "")
            required = slot.get("required", False)
            
            context += f"**{slot_name}** (ID: {slot_id}, Required: {required}):\n"
            
            filters = slot.get("filters", {})
            allowed_items = filters.get("allowedItems", [])
            
            # List available modules (limit to avoid token overflow)
            for item in allowed_items[:10]:  # Top 10 per slot
                item_name = item.get("name", "Unknown")
                item_price = item.get("avg24hPrice", 0) or 0
                
                # Get mod properties
                item_props = item.get("properties", {})
                ergo = item_props.get("ergonomics", 0)
                recoil_mod = item_props.get("recoilModifier", 0)
                
                stats = []
                if ergo != 0:
                    stats.append(f"Ergo: {ergo:+d}")
                if recoil_mod != 0:
                    stats.append(f"Recoil: {recoil_mod:+d}")
                
                stats_str = f" [{', '.join(stats)}]" if stats else ""
                
                context += f"  - {item_name} ({item_price:,} ₽){stats_str}\n"
            
            if len(allowed_items) > 10:
                context += f"  ... and {len(allowed_items) - 10} more options\n"
            
            context += "\n"
        
        return context
    
    async def build_quest_context(self, quest_name: Optional[str] = None, language: str = "ru") -> str:
        """
        Build context about quests (especially Gunsmith quests).
        
        Args:
            quest_name: Specific quest to focus on (optional)
            language: Language for names (ru/en)
            
        Returns:
            Formatted string with quest information
        """
        quests = await self.api.get_weapon_build_tasks(lang=language)
        
        if not quests:
            return "No quest information available."
        
        if quest_name:
            # Find specific quest
            quest_lower = quest_name.lower()
            matching_quests = [
                q for q in quests
                if quest_lower in q.get("name", "").lower() or
                   quest_lower in q.get("normalizedName", "").lower()
            ]
            
            if matching_quests:
                return self._format_quest_details(matching_quests[0], language)
            return f"Quest '{quest_name}' not found."
        
        # Return all gunsmith quests
        context = "Available weapon build quests:\n\n"
        for quest in quests[:20]:  # Limit to 20 quests
            quest_name = quest.get("name", "Unknown")
            trader = quest.get("trader", {}).get("name", "Unknown")
            level = quest.get("minPlayerLevel", 0)
            
            context += f"**{quest_name}** (Trader: {trader}, Level: {level})\n"
            
            # Add objectives
            objectives = quest.get("objectives", [])
            for obj in objectives[:3]:  # First 3 objectives
                obj_desc = obj.get("description", "")
                if obj_desc:
                    context += f"  - {obj_desc}\n"
            
            context += "\n"
        
        return context
    
    async def build_user_context(self, user_id: int) -> str:
        """
        Build context about user preferences and trader levels.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Formatted string with user information
        """
        user = await self.db.get_user(user_id)
        if not user:
            return "New user (no preferences set)."
        
        context = f"User settings:\n"
        context += f"  - Language: {user.language}\n"
        
        if user.trader_levels:
            context += f"  - Trader Loyalty Levels:\n"
            for trader, level in user.trader_levels.items():
                context += f"    • {trader.capitalize()}: Level {level}\n"
        else:
            context += f"  - Trader levels: Not configured\n"
        
        return context
    
    async def build_market_context(self, language: str = "en") -> str:
        """
        Build context about market prices (limited).
        
        Args:
            language: Language for names (ru/en)
            
        Returns:
            Formatted string with market information
        """
        # This is lightweight - just general info
        return "Market information:\n  - Prices are from Flea Market (24h average)\n  - Trader prices may be lower with loyalty levels\n  - All prices in Rubles (₽)\n"
    
    def _format_weapon_details(self, weapon_data: Dict, language: str) -> str:
        """Format weapon details for context with all available characteristics."""
        name = weapon_data.get("name", "Unknown")
        props = weapon_data.get("properties", {})
        
        details = f"**{name}**\n"
        details += f"ID: {weapon_data.get('id')}\n"
        details += f"Price: {weapon_data.get('avg24hPrice', 0):,} ₽\n"
        
        if props:
            # Core stats
            if props.get("caliber"):
                details += f"Caliber: {props['caliber']}\n"
            if props.get("ergonomics") is not None:
                details += f"Ergonomics: {props['ergonomics']}\n"
            if props.get("recoilVertical") is not None:
                details += f"Vertical Recoil: {props['recoilVertical']}\n"
            if props.get("recoilHorizontal") is not None:
                details += f"Horizontal Recoil: {props['recoilHorizontal']}\n"
            if props.get("fireRate"):
                details += f"Fire Rate: {props['fireRate']} RPM\n"
            
            # Additional characteristics
            if props.get("defaultAmmo"):
                ammo = props['defaultAmmo']
                details += f"Default Ammo: {ammo.get('name', 'Unknown')}\n"
            if props.get("effectiveDistance"):
                details += f"Effective Distance: {props['effectiveDistance']}m\n"
            if props.get("sightingRange"):
                details += f"Sighting Range: {props['sightingRange']}m\n"
            if props.get("convergence") is not None:
                details += f"Convergence: {props['convergence']}\n"
            if props.get("recoilAngle") is not None:
                details += f"Recoil Angle: {props['recoilAngle']}°\n"
            if props.get("recoilDispersion") is not None:
                details += f"Recoil Dispersion: {props['recoilDispersion']}\n"
            if props.get("cameraRecoil") is not None:
                details += f"Camera Recoil: {props['cameraRecoil']}\n"
        
        return details
    
    def _format_quest_details(self, quest: Dict, language: str) -> str:
        """Format quest details for context."""
        name = quest.get("name", "Unknown")
        trader = quest.get("trader", {}).get("name", "Unknown")
        level = quest.get("minPlayerLevel", 0)
        
        context = f"**{name}**\n"
        context += f"  - Trader: {trader}\n"
        context += f"  - Required Level: {level}\n\n"
        context += f"Objectives:\n"
        
        objectives = quest.get("objectives", [])
        for i, obj in enumerate(objectives, 1):
            obj_type = obj.get("type", "")
            obj_desc = obj.get("description", "No description")
            optional = obj.get("optional", False)
            
            opt_marker = " (Optional)" if optional else ""
            context += f"{i}. {obj_desc}{opt_marker}\n"
            
            # Add specific requirements for build objectives
            if "builditem" in obj_type.lower():
                item = obj.get("item", {})
                if item:
                    context += f"   Required item: {item.get('name', 'Unknown')}\n"
                
                attributes = obj.get("attributes", [])
                for attr in attributes:
                    attr_name = attr.get("name", "")
                    req = attr.get("requirement", {})
                    compare = req.get("compareMethod", "")
                    value = req.get("value", "")
                    
                    if attr_name and value:
                        context += f"   - {attr_name}: {compare} {value}\n"
        
        return context
