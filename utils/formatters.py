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
    
    # Weapon characteristics
    if weapon.caliber or weapon.ergonomics or weapon.recoil_vertical:
        text += "📊 **" + ("Характеристики оружия" if language == "ru" else "Weapon Stats") + ":**\n"
        if weapon.caliber:
            text += f"  🔸 " + ("Калибр" if language == "ru" else "Caliber") + f": {weapon.caliber}\n"
        if weapon.ergonomics is not None:
            text += f"  🔸 " + ("Эргономика" if language == "ru" else "Ergonomics") + f": {weapon.ergonomics}\n"
        if weapon.recoil_vertical is not None:
            text += f"  🔸 " + ("Вертикальная отдача" if language == "ru" else "Vertical Recoil") + f": {weapon.recoil_vertical}\n"
        if weapon.recoil_horizontal is not None:
            text += f"  🔸 " + ("Горизонтальная отдача" if language == "ru" else "Horizontal Recoil") + f": {weapon.recoil_horizontal}\n"
        if weapon.fire_rate is not None:
            text += f"  🔸 " + ("Скорострельность" if language == "ru" else "Fire Rate") + f": {weapon.fire_rate} RPM\n"
        if weapon.effective_range is not None:
            text += f"  🔸 " + ("Эффективная дальность" if language == "ru" else "Effective Range") + f": {weapon.effective_range}m\n"
        text += "\n"
    
    # Modules list grouped by trader
    if modules:
        text += "🔧 **" + ("Модули и запчасти" if language == "ru" else "Modules & Parts") + ":**\n"
        
        # Group modules by trader
        from collections import defaultdict
        modules_by_trader = defaultdict(list)
        for module in modules:
            modules_by_trader[module.trader].append(module)
        
        # Display modules grouped by trader
        for trader, trader_modules in sorted(modules_by_trader.items()):
            trader_emoji = get_trader_emoji(trader)
            max_ll = max(m.loyalty_level for m in trader_modules)
            text += f"\n{trader_emoji} **{trader}** (" + ("Требуется LL" if language == "ru" else "Required LL") + f" {max_ll})**:**\n"
            
            for module in trader_modules:
                module_name = module.name_ru if language == "ru" else module.name_en
                slot_name = f" [{module.slot_type}]" if module.slot_type else ""
                text += f"  • {module_name}{slot_name}\n"
                text += f"    💰 {module.price:,} ₽ | LL{module.loyalty_level}\n"
        
        text += "\n"
    
    # Total cost
    text += "💵 **" + get_text("build_total_cost", language, cost=f"{build.total_cost:,}") + "**\n"
    
    # Minimum loyalty level
    text += "⭐ " + ("Минимальный уровень лояльности" if language == "ru" else "Minimum loyalty level") + f": **{build.min_loyalty_level}**\n"
    
    # Planner link
    if build.planner_link:
        text += "\n🔗 " + get_text("build_planner", language, link=build.planner_link)
    
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
