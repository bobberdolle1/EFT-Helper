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


@router.message(F.text.in_([get_text("truly_random_build", "ru"), get_text("truly_random_build", "en")]))
async def show_truly_random_build(message: Message, user_service, random_build_service):
    """Show truly random build with compatibility checks."""
    user = await user_service.get_or_create_user(message.from_user.id)
    
    # Show loading message
    loading_msg = await message.answer(get_text("generating_truly_random", user.language))
    
    # Generate truly random build
    build_data = await random_build_service.generate_random_build_for_random_weapon()
    
    if not build_data:
        await loading_msg.edit_text(get_text("error", user.language))
        return
    
    # Format build information
    build_text, total_cost = random_build_service.format_build_info(build_data, user.language)
    
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
async def show_quest_builds(message: Message, user_service, api_client):
    """Show quest-related builds with interactive buttons."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    user = await user_service.get_or_create_user(message.from_user.id)
    
    # Show loading message
    loading_msg = await message.answer(get_text("loading_quests", user.language))
    
    # Get only weapon build quests from API
    tasks = await api_client.get_weapon_build_tasks()
    
    if not tasks:
        await loading_msg.edit_text(get_text("no_quest_builds", user.language))
        return
    
    # Group quests by trader
    traders = {}
    for task in tasks:
        trader_data = task.get("trader")
        if not trader_data:
            continue
        trader_name = trader_data.get("name", "Unknown")
        if trader_name not in traders:
            traders[trader_name] = []
        traders[trader_name].append(task)
    
    # Format quest list
    text = f"**{get_text('quest_builds_title', user.language)}**\n\n"
    text += get_text("select_quest", user.language)
    
    # Create inline keyboard with quest buttons
    buttons = []
    trader_emoji = {
        "Prapor": "🔫",
        "Therapist": "💊",
        "Fence": "🤝",
        "Skier": "⛷️",
        "Peacekeeper": "🕊️",
        "Mechanic": "🔧",
        "Ragman": "👔",
        "Jaeger": "🌲",
        "Lightkeeper": "💡"
    }
    
    for trader_name in sorted(traders.keys()):
        trader_tasks = traders[trader_name]
        emoji = trader_emoji.get(trader_name, "👤")
        
        for task in sorted(trader_tasks, key=lambda t: t.get("minPlayerLevel", 0)):
            name = task.get("name", "Unknown Quest")
            level = task.get("minPlayerLevel", "?")
            task_id = task.get("id", "")
            button_text = f"{emoji} {name} (Lvl {level})"
            buttons.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"quest_detail:{task_id}"
            )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await loading_msg.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(F.text.in_([get_text("all_quest_builds", "ru"), get_text("all_quest_builds", "en")]))
async def show_all_quest_builds(message: Message, user_service, api_client):
    """Show all quest builds."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    user = await user_service.get_or_create_user(message.from_user.id)
    
    # Show loading message
    loading_msg = await message.answer(get_text("loading_quests", user.language))
    
    # Get only weapon build quests from API
    tasks = await api_client.get_weapon_build_tasks()
    
    if not tasks:
        await loading_msg.edit_text(get_text("no_quest_builds", user.language))
        return
    
    # Group quests by trader
    traders = {}
    for task in tasks:
        trader_data = task.get("trader")
        if not trader_data:
            continue
        trader_name = trader_data.get("name", "Unknown")
        if trader_name not in traders:
            traders[trader_name] = []
        traders[trader_name].append(task)
    
    # Format quest list
    text = f"**{get_text('all_quest_builds_title', user.language)}**\n\n"
    text += get_text("select_quest", user.language)
    
    # Create inline keyboard with quest buttons
    buttons = []
    trader_emoji = {
        "Prapor": "🔫",
        "Therapist": "💊",
        "Fence": "🤝",
        "Skier": "⛷️",
        "Peacekeeper": "🕊️",
        "Mechanic": "🔧",
        "Ragman": "👔",
        "Jaeger": "🌲",
        "Lightkeeper": "💡"
    }
    
    for trader_name in sorted(traders.keys()):
        trader_tasks = traders[trader_name]
        emoji = trader_emoji.get(trader_name, "👤")
        
        for task in sorted(trader_tasks, key=lambda t: t.get("minPlayerLevel", 0)):
            name = task.get("name", "Unknown Quest")
            level = task.get("minPlayerLevel", "?")
            task_id = task.get("id", "")
            button_text = f"{emoji} {name} (Lvl {level})"
            buttons.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"quest_detail:{task_id}"
            )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await loading_msg.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


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
async def show_quest_detail(callback: CallbackQuery, user_service, api_client, build_service, db: Database):
    """Show quest details and recommended build."""
    from utils.formatters import format_build_card
    
    user = await user_service.get_or_create_user(callback.from_user.id)
    quest_id = callback.data.split(":")[1]
    
    # Get weapon build tasks from API to find the specific one
    tasks = await api_client.get_weapon_build_tasks()
    quest_data = None
    for task in tasks:
        if task.get("id") == quest_id:
            quest_data = task
            break
    
    if not quest_data:
        await callback.answer(get_text("error", user.language))
        return
    
    # Format quest details
    name = quest_data.get("name", "Unknown Quest")
    trader_data = quest_data.get("trader", {})
    trader_name = trader_data.get("name", "Unknown") if trader_data else "Unknown"
    level = quest_data.get("minPlayerLevel", "?")
    experience = quest_data.get("experience", 0)
    map_data = quest_data.get("map")
    map_name = map_data.get("name") if map_data else "Any"
    
    objectives = quest_data.get("objectives", [])
    task_requirements = quest_data.get("taskRequirements", [])
    
    text = f"📜 **{name}**\n\n"
    text += f"**{get_text('quest_trader', user.language)}:** {trader_name}\n"
    text += f"**{get_text('quest_level', user.language)}:** {level}\n"
    text += f"**{get_text('quest_experience', user.language)}:** {experience} XP\n"
    if map_name and map_name != "Any":
        text += f"**{get_text('quest_map', user.language)}:** {map_name}\n"
    text += "\n"
    
    if task_requirements:
        text += f"📋 **{get_text('quest_required_tasks', user.language)}:**\n"
        for req in task_requirements[:5]:  # Limit to 5 requirements
            req_task = req.get("task", {})
            req_name = req_task.get("name", "Unknown")
            text += f"  • {req_name}\n"
        text += "\n"
    
    if objectives:
        text += f"🎯 **{get_text('quest_objectives', user.language)}:**\n"
        for i, obj in enumerate(objectives[:10], 1):  # Limit to 10 objectives
            description = obj.get("description", "No description")
            obj_type = obj.get("type", "")
            optional = obj.get("optional", False)
            optional_mark = f" ({get_text('quest_optional', user.language)})" if optional else ""
            text += f"  {i}. {description}{optional_mark}\n"
        if len(objectives) > 10:
            text += f"  ... {get_text('quest_and_more', user.language)} {len(objectives) - 10} {get_text('quest_more_objectives', user.language)}\n"
        text += "\n"
    
    # Try to find a recommended build for this quest
    # Look for builds with quest_name matching this quest
    quest_builds = await db.get_quest_builds()
    matching_build = None
    
    for build in quest_builds:
        # Check if quest_name in build matches the current quest name
        # Use language-specific quest_name field
        build_quest_name = build.quest_name_ru if user.language == "ru" else build.quest_name_en
        if build_quest_name and (build_quest_name.lower() in name.lower() or name.lower() in build_quest_name.lower()):
            matching_build = build
            break
    
    # If found a matching build, display it
    if matching_build:
        weapon = await db.get_weapon_by_id(matching_build.weapon_id)
        modules = await db.get_modules_by_ids(matching_build.modules)
        
        if weapon:
            text += f"\n🔧 **{get_text('quest_recommended_build', user.language)}:**\n\n"
            build_card = await format_build_card(matching_build, weapon, modules, user.language)
            text += build_card
    
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
