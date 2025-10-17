"""Formatters for displaying builds and other data."""
from database import Build, Weapon, Module
from localization import get_text
from typing import List
from .constants import TRADER_EMOJIS


async def format_build_card(build: Build, weapon: Weapon, modules: List[Module], language: str = "ru") -> str:
    """Format a build card for display."""
    weapon_name = weapon.name_ru if language == "ru" else weapon.name_en
    
    # Title
    text = get_text("build_card_title", language, weapon=weapon_name)
    
    # Category
    category_key = f"category_{build.category.value}"
    category_name = get_text(category_key, language)
    text += get_text("build_category", language, category=category_name) + "\n"
    
    # Quest name if applicable
    if build.quest_name_ru or build.quest_name_en:
        quest_name = build.quest_name_ru if language == "ru" else build.quest_name_en
        text += get_text("build_quest", language, quest=quest_name) + "\n"
    
    # Build name if applicable
    if build.name_ru or build.name_en:
        build_name = build.name_ru if language == "ru" else build.name_en
        text += f"📝 {build_name}\n"
    
    text += "\n"
    
    # Modules list
    if modules:
        text += get_text("build_modules", language) + "\n"
        for module in modules:
            module_name = module.name_ru if language == "ru" else module.name_en
            trader_emoji = get_trader_emoji(module.trader)
            text += f"  • {module_name}\n"
            text += f"    {trader_emoji} {module.trader} (LL{module.loyalty_level}) - {module.price:,} ₽\n"
    
    text += "\n"
    
    # Total cost
    text += get_text("build_total_cost", language, cost=f"{build.total_cost:,}") + "\n"
    
    # Minimum loyalty level
    text += get_text("build_loyalty", language, level=build.min_loyalty_level) + "\n"
    
    # Planner link
    if build.planner_link:
        text += "\n" + get_text("build_planner", language, link=build.planner_link)
    
    return text


def get_trader_emoji(trader: str) -> str:
    """Get emoji for trader."""
    return TRADER_EMOJIS.get(trader, TRADER_EMOJIS.get(trader.lower(), "💼"))


def format_price(price: int, language: str = "ru") -> str:
    """Format price with proper currency symbol."""
    if language == "ru":
        return f"{price:,} ₽"
    else:
        return f"{price:,} RUB"
