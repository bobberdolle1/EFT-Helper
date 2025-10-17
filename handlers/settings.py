"""Settings handlers for the EFT Helper bot."""
from aiogram import Router, F
from aiogram.types import Message
from database import Database
from localization import get_text
from keyboards import get_settings_keyboard, get_main_menu_keyboard


router = Router()


@router.message(F.text.in_([get_text("settings", "ru"), get_text("settings", "en")]))
async def show_settings(message: Message, db: Database):
    """Show settings menu."""
    user = await db.get_or_create_user(message.from_user.id)
    
    current_lang = "🇷🇺 Русский" if user.language == "ru" else "🇬🇧 English"
    text = get_text("settings_title", language=user.language) + "\n\n"
    text += get_text("current_language", language=user.language, language_name=current_lang) + "\n\n"
    text += get_text("change_language", language=user.language)
    
    keyboard = get_settings_keyboard(user.language)
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text.in_([get_text("lang_ru", "ru"), get_text("lang_ru", "en")]))
async def set_language_ru(message: Message, db: Database):
    """Set language to Russian."""
    await db.update_user_language(message.from_user.id, "ru")
    
    text = get_text("language_changed", language="ru", language_name="🇷🇺 Русский")
    keyboard = get_main_menu_keyboard("ru")
    
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text.in_([get_text("lang_en", "ru"), get_text("lang_en", "en")]))
async def set_language_en(message: Message, db: Database):
    """Set language to English."""
    await db.update_user_language(message.from_user.id, "en")
    
    text = get_text("language_changed", language="en", language_name="🇬🇧 English")
    keyboard = get_main_menu_keyboard("en")
    
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text.in_([get_text("back", "ru"), get_text("back", "en")]))
async def back_to_menu(message: Message, db: Database):
    """Go back to main menu."""
    user = await db.get_or_create_user(message.from_user.id)
    
    text = get_text("welcome", user.language)
    keyboard = get_main_menu_keyboard(user.language)
    
    await message.answer(text, reply_markup=keyboard)
