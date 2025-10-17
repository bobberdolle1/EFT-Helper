"""Loyalty build handlers for the EFT Helper bot."""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
from localization import get_text
from keyboards import get_builds_list_keyboard
from utils.constants import TRADER_EMOJIS

logger = logging.getLogger(__name__)


router = Router()


@router.message(F.text.in_([get_text("loyalty_builds", "ru"), get_text("loyalty_builds", "en")]))
async def show_loyalty_setup(message: Message, db: Database):
    """Show loyalty level setup interface."""
    user = await db.get_or_create_user(message.from_user.id)
    
    text = get_text("setup_loyalty_levels", language=user.language) + "\n\n"
    text += get_text("current_loyalty_levels", language=user.language) + "\n"
    
    for trader, level in user.trader_levels.items():
        trader_name = get_text(trader, language=user.language)
        text += f"  • {trader_name}: {level}\n"
    
    keyboard = get_loyalty_setup_keyboard(user.language)
    await message.answer(text, reply_markup=keyboard)


def get_loyalty_setup_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """Get keyboard for loyalty level setup."""
    traders = [
        "prapor", "therapist", "fence", "skier",
        "peacekeeper", "mechanic", "ragman", "jaeger"
    ]
    
    buttons = []
    for trader_key in traders:
        emoji = TRADER_EMOJIS.get(trader_key, "💼")
        trader_name = get_text(trader_key, language=language)
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {trader_name}",
            callback_data=f"set_loyalty:{trader_key}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text=get_text("show_available_builds", language=language),
        callback_data="show_loyalty_builds"
    )])
    
    buttons.append([InlineKeyboardButton(
        text=get_text("reset_loyalty_levels", language=language),
        callback_data="reset_loyalty"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data.startswith("set_loyalty:"))
async def select_trader_level(callback: CallbackQuery, db: Database):
    """Handle trader selection for level setting."""
    user = await db.get_or_create_user(callback.from_user.id)
    trader = callback.data.split(":")[1]
    
    trader_name = get_text(trader, language=user.language)
    text = get_text("select_loyalty_level", language=user.language, trader=trader_name)
    
    buttons = []
    for level in range(1, 5):
        buttons.append([InlineKeyboardButton(
            text=get_text("loyalty_level", language=user.language, level=level),
            callback_data=f"update_loyalty:{trader}:{level}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text=get_text("back", language=user.language),
        callback_data="back_to_loyalty_setup"
    )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("update_loyalty:"))
async def update_trader_loyalty(callback: CallbackQuery, db: Database):
    """Update trader loyalty level."""
    user = await db.get_or_create_user(callback.from_user.id)
    parts = callback.data.split(":")
    trader = parts[1]
    level = int(parts[2])
    
    # Update trader level
    user.trader_levels[trader] = level
    await db.update_trader_levels(callback.from_user.id, user.trader_levels)
    
    trader_name = get_text(trader, language=user.language)
    await callback.answer(
        get_text("trader_level_set", language=user.language, trader=trader_name, level=level),
        show_alert=True
    )
    
    # Return to loyalty setup
    text = get_text("setup_loyalty_levels", language=user.language) + "\n\n"
    text += get_text("current_loyalty_levels", language=user.language) + "\n"
    
    for t, l in user.trader_levels.items():
        t_name = get_text(t, language=user.language)
        text += f"  • {t_name}: {l}\n"
    
    keyboard = get_loyalty_setup_keyboard(user.language)
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "show_loyalty_builds")
async def show_available_builds(callback: CallbackQuery, db: Database):
    """Show builds available based on user's trader levels."""
    user = await db.get_or_create_user(callback.from_user.id)
    
    # Get all builds and filter by user's trader levels
    all_weapons = await db.get_all_weapons()
    available_builds = []
    
    for weapon in all_weapons:
        builds = await db.get_builds_by_weapon(weapon.id)
        for build in builds:
            # Check if all modules are available with user's levels
            modules = await db.get_modules_by_ids(build.modules)
            if all(user.trader_levels.get(m.trader.lower(), 1) >= m.loyalty_level for m in modules):
                available_builds.append(build)
    
    if not available_builds:
        text = get_text("no_builds_found", language=user.language)
        await callback.message.edit_text(text)
        await callback.answer()
        return
    
    text = f"📋 {get_text('show_available_builds', language=user.language)}\n\n"
    text += f"Найдено сборок: {len(available_builds)}" if user.language == "ru" else f"Found {len(available_builds)} builds"
    
    keyboard = get_builds_list_keyboard(available_builds[:20], user.language)  # Limit to 20
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "reset_loyalty")
async def reset_loyalty_levels(callback: CallbackQuery, db: Database):
    """Reset all trader loyalty levels to 1."""
    user = await db.get_or_create_user(callback.from_user.id)
    
    default_levels = {trader: 1 for trader in user.trader_levels.keys()}
    await db.update_trader_levels(callback.from_user.id, default_levels)
    
    await callback.answer(get_text("loyalty_levels_saved", language=user.language), show_alert=True)
    
    # Refresh display
    user = await db.get_user(callback.from_user.id)
    text = get_text("setup_loyalty_levels", language=user.language) + "\n\n"
    text += get_text("current_loyalty_levels", language=user.language) + "\n"
    
    for trader, level in user.trader_levels.items():
        trader_name = get_text(trader, language=user.language)
        text += f"  • {trader_name}: {level}\n"
    
    keyboard = get_loyalty_setup_keyboard(user.language)
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "back_to_loyalty_setup")
async def back_to_loyalty_setup(callback: CallbackQuery, db: Database):
    """Go back to loyalty setup screen."""
    user = await db.get_or_create_user(callback.from_user.id)
    
    text = get_text("setup_loyalty_levels", language=user.language) + "\n\n"
    text += get_text("current_loyalty_levels", language=user.language) + "\n"
    
    for trader, level in user.trader_levels.items():
        trader_name = get_text(trader, language=user.language)
        text += f"  • {trader_name}: {level}\n"
    
    keyboard = get_loyalty_setup_keyboard(user.language)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
