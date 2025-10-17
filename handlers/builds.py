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
async def show_random_build(message: Message, db: Database):
    """Show random build."""
    user = await db.get_or_create_user(message.from_user.id)
    
    # Show loading message
    loading_msg = await message.answer(get_text("generating_random", user.language))
    
    # Get random build
    build = await db.get_random_build()
    
    if not build:
        await loading_msg.edit_text(get_text("no_builds_found", user.language))
        return
    
    # Format and show build card
    weapon = await db.get_weapon_by_id(build.weapon_id)
    modules = await db.get_modules_by_ids(build.modules)
    
    # Check if weapon exists
    if not weapon:
        error_text = get_text("weapon_not_found", user.language)
        await loading_msg.edit_text(error_text)
        return
    
    build_text = await format_build_card(build, weapon, modules, user.language)
    await loading_msg.edit_text(build_text, parse_mode="Markdown")


@router.message(F.text.in_([get_text("meta_builds", "ru"), get_text("meta_builds", "en")]))
async def show_meta_builds(message: Message, db: Database):
    """Show meta builds."""
    user = await db.get_or_create_user(message.from_user.id)
    
    builds = await db.get_meta_builds()
    
    if not builds:
        await message.answer(get_text("no_meta_builds", user.language))
        return
    
    text = get_text("meta_builds_title", user.language) + "\n" + get_text("meta_builds_desc", user.language)
    keyboard = get_builds_list_keyboard(builds, user.language)
    
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text.in_([get_text("quest_builds", "ru"), get_text("quest_builds", "en")]))
async def show_quest_builds(message: Message, db: Database):
    """Show quest-related builds with full details."""
    from database.quest_builds_data import get_all_quests
    
    user = await db.get_or_create_user(message.from_user.id)
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
    
    for trader, trader_quests in traders.items():
        emoji = {"Mechanic": "🔧", "Prapor": "🔫", "Jaeger": "🌲"}.get(trader, "👤")
        text += f"{emoji} **{trader}:**\n"
        for quest in trader_quests:
            name = quest["name_ru"] if user.language == "ru" else quest["name_en"]
            level = quest.get("level_required", "?")
            weapon = quest.get("weapon", "")
            text += f"  • {name} (Lvl {level}) - {weapon}\n"
        text += "\n"
    
    text += "\n💡 Выберите квест для подробностей" if user.language == "ru" else "\n💡 Select a quest for details"
    
    await message.answer(text, parse_mode="Markdown")


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
