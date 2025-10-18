"""Search handlers for the EFT Helper bot."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import Database, BuildCategory, WeaponCategory
from localization import get_text
from keyboards import (
    get_weapon_selection_keyboard,
    get_build_type_keyboard
)


router = Router()


class SearchStates(StatesGroup):
    """States for weapon search."""
    waiting_for_weapon_name = State()


def get_category_selection_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """Get weapon category selection keyboard."""
    categories = [
        ("category_pistols", WeaponCategory.PISTOL),
        ("category_smg", WeaponCategory.SMG),
        ("category_assault_rifles", WeaponCategory.ASSAULT_RIFLE),
        ("category_dmr", WeaponCategory.DMR),
        ("category_sniper_rifles", WeaponCategory.SNIPER),
        ("category_shotguns", WeaponCategory.SHOTGUN),
        ("category_lmg", WeaponCategory.LMG)
    ]
    
    buttons = []
    for text_key, category in categories:
        buttons.append([InlineKeyboardButton(
            text=get_text(text_key, language=language),
            callback_data=f"category:{category.value}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text=get_text("search_by_name", language=language),
        callback_data="search_by_name"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text.in_([get_text("search_weapon", "ru"), get_text("search_weapon", "en")]))
async def start_search(message: Message, state: FSMContext, user_service):
    """Start weapon search - show category selection."""
    user = await user_service.get_or_create_user(message.from_user.id)
    
    text = get_text("select_category", language=user.language)
    keyboard = get_category_selection_keyboard(user.language)
    
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("category:"))
async def show_category_weapons(callback: CallbackQuery, user_service, weapon_service):
    """Show weapons in selected category."""
    user = await user_service.get_or_create_user(callback.from_user.id)
    category = callback.data.split(":")[1]
    
    # Get all weapons from service in this category
    from database import WeaponCategory
    category_enum = WeaponCategory(category)
    category_weapons = await weapon_service.get_weapons_by_category(category_enum)
    
    if not category_weapons:
        await callback.message.edit_text(get_text("no_weapons_found", language=user.language))
        await callback.answer()
        return
    
    text = get_text("select_weapon", language=user.language)
    keyboard = get_weapon_selection_keyboard(category_weapons, user.language)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "search_by_name")
async def search_by_name_prompt(callback: CallbackQuery, state: FSMContext, user_service):
    """Prompt user to enter weapon name."""
    user = await user_service.get_or_create_user(callback.from_user.id)
    
    await state.set_state(SearchStates.waiting_for_weapon_name)
    await callback.message.edit_text(get_text("enter_weapon_name", language=user.language))
    await callback.answer()


@router.message(SearchStates.waiting_for_weapon_name)
async def process_weapon_search(message: Message, state: FSMContext, user_service, weapon_service):
    """Process weapon search query - supports both Russian and English names."""
    user = await user_service.get_or_create_user(message.from_user.id)
    query = message.text.strip()
    
    # Search for weapons using service
    weapons = await weapon_service.search_weapons(query, user.language)
    
    if not weapons:
        await message.answer(get_text("weapon_not_found", user.language))
        return
    
    if len(weapons) == 1:
        # If only one weapon found, show build types directly
        weapon = weapons[0]
        weapon_name = weapon.name_ru if user.language == "ru" else weapon.name_en
        text = get_text("select_build_type", user.language, weapon=weapon_name)
        keyboard = get_build_type_keyboard(weapon.id, user.language)
        await message.answer(text, reply_markup=keyboard)
    else:
        # Show weapon selection
        text = get_text("select_weapon", user.language)
        keyboard = get_weapon_selection_keyboard(weapons, user.language)
        await message.answer(text, reply_markup=keyboard)
    
    await state.clear()


@router.callback_query(F.data.startswith("weapon:"))
async def select_weapon(callback: CallbackQuery, user_service, weapon_service):
    """Handle weapon selection."""
    user = await user_service.get_or_create_user(callback.from_user.id)
    weapon_id = int(callback.data.split(":")[1])
    
    weapon = await weapon_service.get_weapon_by_id(weapon_id)
    if not weapon:
        await callback.answer(get_text("error", user.language))
        return
    
    weapon_name = weapon.name_ru if user.language == "ru" else weapon.name_en
    text = get_text("select_build_type", user.language, weapon=weapon_name)
    keyboard = get_build_type_keyboard(weapon.id, user.language)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
