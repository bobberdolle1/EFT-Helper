"""Common handlers for the EFT Helper bot."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from database import Database
from localization import get_text
from keyboards import get_main_menu_keyboard, get_language_selection_keyboard


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, db: Database):
    """Handle /start command."""
    # Check if user exists
    user = await db.get_user(message.from_user.id)
    
    if not user:
        # New user - show language selection
        text = get_text("select_language", "ru")  # Bilingual text
        keyboard = get_language_selection_keyboard()
        await message.answer(text, reply_markup=keyboard)
    else:
        # Existing user - show main menu
        welcome_text = get_text("welcome", user.language)
        keyboard = get_main_menu_keyboard(user.language)
        await message.answer(welcome_text, reply_markup=keyboard)


@router.message(F.text.in_([get_text("main_menu", "ru"), get_text("main_menu", "en")]))
async def show_main_menu(message: Message, user_service):
    """Show main menu."""
    user = await user_service.get_or_create_user(message.from_user.id)
    
    menu_text = get_text("welcome", user.language)
    keyboard = get_main_menu_keyboard(user.language)
    
    await message.answer(menu_text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("lang:"))
async def handle_language_selection(callback: CallbackQuery, db: Database):
    """Handle language selection for new users."""
    # Extract language code
    language = callback.data.split(":")[1]  # "ru" or "en"
    
    # Create user with selected language
    await db.create_user(callback.from_user.id, language=language)
    
    # Send confirmation and show main menu
    welcome_text = get_text("language_selected", language)
    await callback.message.edit_text(welcome_text)
    
    # Show main menu
    menu_text = get_text("welcome", language)
    keyboard = get_main_menu_keyboard(language)
    await callback.message.answer(menu_text, reply_markup=keyboard)
    
    await callback.answer()
