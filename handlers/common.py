"""Common handlers for the EFT Helper bot."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from database import Database
from localization import get_text
from keyboards import get_main_menu_keyboard


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, db: Database):
    """Handle /start command."""
    user = await db.get_or_create_user(message.from_user.id)
    
    welcome_text = get_text("welcome", user.language)
    keyboard = get_main_menu_keyboard(user.language)
    
    await message.answer(welcome_text, reply_markup=keyboard)


@router.message(F.text.in_([get_text("main_menu", "ru"), get_text("main_menu", "en")]))
async def show_main_menu(message: Message, db: Database):
    """Show main menu."""
    user = await db.get_or_create_user(message.from_user.id)
    
    menu_text = get_text("welcome", user.language)
    keyboard = get_main_menu_keyboard(user.language)
    
    await message.answer(menu_text, reply_markup=keyboard)
