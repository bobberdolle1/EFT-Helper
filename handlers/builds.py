"""Build handlers for the EFT Helper bot."""
import logging
import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database import Database, BuildCategory
from localization import get_text
from keyboards import get_builds_list_keyboard
from utils.formatters import format_build_card

logger = logging.getLogger(__name__)


router = Router()


@router.message(F.text.in_([get_text("random_build", "ru"), get_text("random_build", "en")]))
async def show_random_build(message: Message, user_service, build_service):
    """Show random build."""
    user = await user_service.get_or_create_user(message.from_user.id)
    
    # Show loading message
    loading_msg = await message.answer(get_text("generating_random", user.language))
    
    # Get random build using service
    build_data = await build_service.get_random_build()
    
    if not build_data:
        await loading_msg.edit_text(get_text("no_builds_found", user.language))
        return
    
    build = build_data["build"]
    weapon = build_data["weapon"]
    modules = build_data["modules"]
    
    # Check if weapon exists
    if not weapon:
        error_text = get_text("weapon_not_found", user.language)
        await loading_msg.edit_text(error_text)
        return
    
    build_text = await format_build_card(build, weapon, modules, user.language)
    await loading_msg.edit_text(build_text, parse_mode="Markdown")


@router.message(F.text.in_([get_text("meta_builds", "ru"), get_text("meta_builds", "en")]))
async def show_meta_builds(message: Message, user_service, build_service):
    """Show meta builds."""
    user = await user_service.get_or_create_user(message.from_user.id)
    
    builds_data = await build_service.get_meta_builds()
    builds = [bd["build"] for bd in builds_data]
    
    if not builds:
        await message.answer(get_text("no_meta_builds", user.language))
        return
    
    text = get_text("meta_builds_title", user.language) + "\n" + get_text("meta_builds_desc", user.language)
    keyboard = get_builds_list_keyboard(builds, user.language)
    
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text.in_([get_text("quest_builds", "ru"), get_text("quest_builds", "en")]))
async def show_quest_builds(message: Message, user_service):
    """Show quest-related builds with interactive buttons."""
    from database.quest_builds_data import get_all_quests
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    user = await user_service.get_or_create_user(message.from_user.id)
    quests = get_all_quests()
    
    if not quests:
        await message.answer(get_text("no_quest_builds", user.language))
        return
    
    # Group quests by trader
    traders = {}
    for quest_id, quest_data in quests.items():
        trader = quest_data.get("trader", "Unknown")
        if trader not in traders:
            traders[trader] = []
        traders[trader].append({"id": quest_id, **quest_data})
    
    # Format quest list
    text = "📜 **Квестовые сборки**\n\n" if user.language == "ru" else "📜 **Quest Builds**\n\n"
    text += "Выберите квест для просмотра рекомендуемой сборки:" if user.language == "ru" else "Select a quest to view recommended build:"
    
    # Create inline keyboard with quest buttons
    buttons = []
    for trader, trader_quests in sorted(traders.items()):
        emoji = {"Mechanic": "🔧", "Prapor": "🔫", "Jaeger": "🌲"}.get(trader, "👤")
        # Add trader header (non-clickable)
        for quest in trader_quests:
            name = quest["name_ru"] if user.language == "ru" else quest["name_en"]
            level = quest.get("level_required", "?")
            button_text = f"{emoji} {name} (Lvl {level})"
            buttons.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"quest_detail:{quest['id']}"
            )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(F.text.in_([get_text("all_quest_builds", "ru"), get_text("all_quest_builds", "en")]))
async def show_all_quest_builds(message: Message, db: Database):
    """Show all quest builds."""
    user = await db.get_or_create_user(message.from_user.id)
    
    builds = await db.get_quest_builds()
    
    if not builds:
        await message.answer(get_text("no_quest_builds", user.language))
        return
    
    text = get_text("quest_builds_list", user.language)
    keyboard = get_builds_list_keyboard(builds, user.language)
    
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("build:"))
async def show_build_by_type(callback: CallbackQuery, db: Database):
    """Show build by type and weapon."""
    user = await db.get_or_create_user(callback.from_user.id)
    parts = callback.data.split(":")
    build_type = parts[1]
    weapon_id = int(parts[2])
    
    # Get builds by weapon and category
    category_map = {
        "random": None,
        "meta": BuildCategory.META,
        "quest": BuildCategory.QUEST,
        "loyalty": BuildCategory.LOYALTY
    }
    
    category = category_map.get(build_type)
    builds = await db.get_builds_by_weapon(weapon_id, category)
    
    if not builds:
        await callback.message.edit_text(get_text("no_builds_found", user.language))
        await callback.answer()
        return
    
    # If random, pick one
    if build_type == "random":
        build = random.choice(builds) if builds else None
    else:
        build = builds[0] if builds else None
    
    if not build:
        await callback.message.edit_text(get_text("no_builds_found", user.language))
        await callback.answer()
        return
    
    # Format and show build card
    weapon = await db.get_weapon_by_id(build.weapon_id)
    modules = await db.get_modules_by_ids(build.modules)
    
    # Check if weapon exists
    if not weapon:
        error_text = get_text("weapon_not_found", user.language)
        await callback.message.edit_text(error_text)
        await callback.answer()
        return
    
    build_text = await format_build_card(build, weapon, modules, user.language)
    await callback.message.edit_text(build_text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("quest_detail:"))
async def show_quest_detail(callback: CallbackQuery, db: Database):
    """Show quest details and recommended build."""
    from database.quest_builds_data import get_quest_by_id
    
    user = await db.get_or_create_user(callback.from_user.id)
    quest_id = callback.data.split(":")[1]
    
    quest_data = get_quest_by_id(quest_id)
    
    if not quest_data:
        await callback.answer(get_text("error", user.language))
        return
    
    # Format quest details
    name = quest_data.get("name_ru") if user.language == "ru" else quest_data.get("name_en")
    description = quest_data.get("description_ru") if user.language == "ru" else quest_data.get("description_en")
    trader = quest_data.get("trader", "Unknown")
    level = quest_data.get("level_required", "?")
    weapon = quest_data.get("weapon", "")
    requirements = quest_data.get("requirements", {})
    recommended_parts = quest_data.get("recommended_parts", [])
    recommended_weapons = quest_data.get("recommended_weapons", [])
    
    text = f"📜 **{name}**\n\n"
    text += f"**{get_text('trader' if user.language == 'en' else 'trader', user.language) if False else ('Торговец' if user.language == 'ru' else 'Trader')}:** {trader}\n"
    text += f"**{('Требуемый уровень' if user.language == 'ru' else 'Required Level')}:** {level}\n\n"
    text += f"📋 **{('Описание' if user.language == 'ru' else 'Description')}:**\n{description}\n\n"
    
    if weapon:
        text += f"🔫 **{('Оружие' if user.language == 'ru' else 'Weapon')}:** {weapon}\n\n"
    
    if recommended_weapons:
        text += f"🎯 **{('Рекомендуемые оружия' if user.language == 'ru' else 'Recommended Weapons')}:**\n"
        for w in recommended_weapons:
            text += f"  • {w}\n"
        text += "\n"
    
    if requirements:
        text += f"✅ **{('Требования' if user.language == 'ru' else 'Requirements')}:**\n"
        for req_key, req_value in requirements.items():
            req_name = req_key.replace('_', ' ').title()
            text += f"  • {req_name}: {req_value}\n"
        text += "\n"
    
    if recommended_parts:
        text += f"🔧 **{('Рекомендуемые модули' if user.language == 'ru' else 'Recommended Parts')}:**\n"
        for part in recommended_parts:
            text += f"  • {part}\n"
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("show_build:"))
async def show_specific_build(callback: CallbackQuery, db: Database):
    """Show specific build by ID."""
    user = await db.get_or_create_user(callback.from_user.id)
    build_id = int(callback.data.split(":")[1])
    
    build = await db.get_build_by_id(build_id)
    
    if not build:
        await callback.answer(get_text("error", user.language))
        return
    
    # Format and show build card
    weapon = await db.get_weapon_by_id(build.weapon_id)
    modules = await db.get_modules_by_ids(build.modules)
    
    # Check if weapon exists
    if not weapon:
        error_text = get_text("weapon_not_found", user.language)
        await callback.message.edit_text(error_text)
        await callback.answer()
        return
    
    build_text = await format_build_card(build, weapon, modules, user.language)
    await callback.message.edit_text(build_text, parse_mode="Markdown")
    await callback.answer()
