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
async def start_search(message: Message, state: FSMContext, db: Database):
    """Start weapon search - show category selection."""
    user = await db.get_or_create_user(message.from_user.id)
    
    text = get_text("select_category", language=user.language)
    keyboard = get_category_selection_keyboard(user.language)
    
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("category:"))
async def show_category_weapons(callback: CallbackQuery, db: Database):
    """Show weapons in selected category."""
    user = await db.get_or_create_user(callback.from_user.id)
    category = callback.data.split(":")[1]
    
    # Get all weapons from database in this category
    all_weapons = await db.get_all_weapons()
    category_weapons = [w for w in all_weapons if w.category.value == category]
    
    if not category_weapons:
        await callback.message.edit_text(get_text("no_weapons_found", language=user.language))
        await callback.answer()
        return
    
    text = get_text("select_weapon", language=user.language)
    keyboard = get_weapon_selection_keyboard(category_weapons, user.language)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "search_by_name")
async def search_by_name_prompt(callback: CallbackQuery, state: FSMContext, db: Database):
    """Prompt user to enter weapon name."""
    user = await db.get_or_create_user(callback.from_user.id)
    
    await state.set_state(SearchStates.waiting_for_weapon_name)
    await callback.message.edit_text(get_text("enter_weapon_name", language=user.language))
    await callback.answer()


@router.message(SearchStates.waiting_for_weapon_name)
async def process_weapon_search(message: Message, state: FSMContext, db: Database):
    """Process weapon search query - supports both Russian and English names."""
    user = await db.get_or_create_user(message.from_user.id)
    query = message.text.strip()
    
    # Search for weapons in both languages
    all_weapons = await db.get_all_weapons()
    
    # Normalize query for better matching
    query_lower = query.lower()
    
    # Search in both Russian and English names
    matching_weapons = []
    for weapon in all_weapons:
        name_ru_lower = weapon.name_ru.lower()
        name_en_lower = weapon.name_en.lower()
        
        if (query_lower in name_ru_lower or 
            query_lower in name_en_lower or
            query_lower.replace('-', '') in name_ru_lower.replace('-', '') or
            query_lower.replace('-', '') in name_en_lower.replace('-', '')):
            matching_weapons.append(weapon)
    
    weapons = matching_weapons
    
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
async def select_weapon(callback: CallbackQuery, db: Database):
    """Handle weapon selection."""
    user = await db.get_or_create_user(callback.from_user.id)
    weapon_id = int(callback.data.split(":")[1])
    
    weapon = await db.get_weapon_by_id(weapon_id)
    if not weapon:
        await callback.answer(get_text("error", user.language))
        return
    
    weapon_name = weapon.name_ru if user.language == "ru" else weapon.name_en
    text = get_text("select_build_type", user.language, weapon=weapon_name)
    keyboard = get_build_type_keyboard(weapon.id, user.language)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
