"""Dynamic build generation handler for v3.0."""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import Database, UserBuild
from localization import get_text
from services import BuildGenerator, BuildGeneratorConfig, CompatibilityChecker, TierEvaluator

logger = logging.getLogger(__name__)

router = Router()


class DynamicBuildStates(StatesGroup):
    """States for dynamic build generation."""
    waiting_for_budget = State()
    waiting_for_build_name = State()


# Store temporary build data
temp_build_data = {}


@router.message(F.text.in_([get_text("dynamic_random_build", "ru"), get_text("dynamic_random_build", "en")]))
async def start_dynamic_build(message: Message, user_service, state: FSMContext):
    """Start dynamic build generation process."""
    user = await user_service.get_or_create_user(message.from_user.id)
    
    text = f"**{get_text('dynamic_build_title', user.language)}**\n\n"
    text += get_text("dynamic_build_desc", user.language) + "\n\n"
    text += get_text("enter_budget", user.language)
    
    await state.set_state(DynamicBuildStates.waiting_for_budget)
    await message.answer(text, parse_mode="Markdown")


@router.message(DynamicBuildStates.waiting_for_budget)
async def process_budget(message: Message, user_service, state: FSMContext, api_client):
    """Process budget input and generate build."""
    user = await user_service.get_or_create_user(message.from_user.id)
    
    # Validate budget
    try:
        budget = int(message.text.strip().replace(",", "").replace(" ", ""))
        if budget <= 0:
            raise ValueError()
    except ValueError:
        await message.answer(get_text("invalid_budget", user.language))
        return
    
    # Show loading message
    loading_msg = await message.answer(get_text("generating_build", user.language))
    
    # Initialize services
    compatibility = CompatibilityChecker(api_client)
    tier_eval = TierEvaluator()
    generator = BuildGenerator(api_client, compatibility, tier_eval)
    
    # Get user's trader levels
    trader_levels = user.trader_levels or {
        "prapor": 1, "therapist": 1, "fence": 1, "skier": 1,
        "peacekeeper": 1, "mechanic": 1, "ragman": 1, "jaeger": 1
    }
    
    # Create configuration
    config = BuildGeneratorConfig(
        budget=budget,
        trader_levels=trader_levels,
        use_flea_only=False,
        weapon_type=None,
        prioritize_ergonomics=False,
        prioritize_recoil=True
    )
    
    # Generate build
    try:
        build = await generator.generate_random_build(config, language=user.language)
        
        if not build:
            await loading_msg.edit_text(get_text("error", user.language))
            await state.clear()
            return
        
        # Store build data temporarily
        temp_build_data[user.user_id] = {
            "build": build,
            "budget": budget
        }
        
        # Format build display
        text = await format_generated_build(build, budget, user.language, tier_eval)
        
        # Action buttons
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_text("save_build", user.language),
                    callback_data="save_dynamic_build"
                ),
                InlineKeyboardButton(
                    text=get_text("regenerate_build", user.language),
                    callback_data=f"regenerate_build:{budget}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("back", user.language),
                    callback_data="cancel_build"
                )
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await loading_msg.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error generating build: {e}", exc_info=True)
        await loading_msg.edit_text(get_text("error", user.language))
        await state.clear()


@router.callback_query(F.data.startswith("regenerate_build:"))
async def regenerate_build(callback: CallbackQuery, user_service, api_client):
    """Regenerate a build with the same budget."""
    user = await user_service.get_or_create_user(callback.from_user.id)
    budget = int(callback.data.split(":")[1])
    
    # Show loading message
    await callback.message.edit_text(get_text("generating_build", user.language))
    
    # Initialize services
    compatibility = CompatibilityChecker(api_client)
    tier_eval = TierEvaluator()
    generator = BuildGenerator(api_client, compatibility, tier_eval)
    
    # Get user's trader levels
    trader_levels = user.trader_levels or {
        "prapor": 1, "therapist": 1, "fence": 1, "skier": 1,
        "peacekeeper": 1, "mechanic": 1, "ragman": 1, "jaeger": 1
    }
    
    # Create configuration
    config = BuildGeneratorConfig(
        budget=budget,
        trader_levels=trader_levels,
        use_flea_only=False,
        weapon_type=None,
        prioritize_ergonomics=False,
        prioritize_recoil=True
    )
    
    # Generate build
    try:
        build = await generator.generate_random_build(config, language=user.language)
        
        if not build:
            await callback.message.edit_text(get_text("error", user.language))
            await callback.answer()
            return
        
        # Store build data temporarily
        temp_build_data[user.user_id] = {
            "build": build,
            "budget": budget
        }
        
        # Format build display
        text = await format_generated_build(build, budget, user.language, tier_eval)
        
        # Action buttons
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_text("save_build", user.language),
                    callback_data="save_dynamic_build"
                ),
                InlineKeyboardButton(
                    text=get_text("regenerate_build", user.language),
                    callback_data=f"regenerate_build:{budget}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("back", user.language),
                    callback_data="cancel_build"
                )
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer(get_text("build_generated", user.language))
        
    except Exception as e:
        logger.error(f"Error regenerating build: {e}", exc_info=True)
        await callback.message.edit_text(get_text("error", user.language))
        await callback.answer()


@router.callback_query(F.data == "save_dynamic_build")
async def save_dynamic_build(callback: CallbackQuery, db: Database, user_service, state: FSMContext):
    """Initiate save process for generated build."""
    user = await user_service.get_or_create_user(callback.from_user.id)
    
    # Check if we have build data
    if user.user_id not in temp_build_data:
        await callback.answer(get_text("error", user.language))
        return
    
    # Ask for build name
    text = get_text("enter_build_name", user.language)
    await callback.message.edit_text(text)
    await state.set_state(DynamicBuildStates.waiting_for_build_name)
    await callback.answer()


@router.message(DynamicBuildStates.waiting_for_build_name)
async def save_build_with_name(message: Message, db: Database, user_service, state: FSMContext):
    """Save the build with user-provided name."""
    user = await user_service.get_or_create_user(message.from_user.id)
    build_name = message.text.strip()
    
    if user.user_id not in temp_build_data:
        await message.answer(get_text("error", user.language))
        await state.clear()
        return
    
    build_data = temp_build_data[user.user_id]
    generated_build = build_data["build"]
    
    # Extract module IDs from generated build
    module_ids = [int(mod.get("id", "0").replace("id_", "")) for mod in generated_build.modules.values() if mod.get("id")]
    # Filter out invalid IDs
    module_ids = [mid for mid in module_ids if mid > 0]
    
    # Create UserBuild object
    user_build = UserBuild(
        id=0,  # Will be auto-generated
        user_id=user.user_id,
        weapon_id=0,  # We need to map weapon_id from tarkov.dev ID to our DB ID
        name=build_name,
        modules=module_ids,
        total_cost=generated_build.total_cost,
        tier_rating=generated_build.tier_rating,
        ergonomics=generated_build.ergonomics,
        recoil_vertical=generated_build.recoil_vertical,
        recoil_horizontal=generated_build.recoil_horizontal,
        is_public=False
    )
    
    try:
        # Save to database
        build_id = await db.create_user_build(user_build)
        
        # Clean up temp data
        del temp_build_data[user.user_id]
        
        await message.answer(get_text("build_saved", user.language))
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error saving build: {e}", exc_info=True)
        await message.answer(get_text("error", user.language))
        await state.clear()


@router.callback_query(F.data == "cancel_build")
async def cancel_build(callback: CallbackQuery, user_service, state: FSMContext):
    """Cancel build generation."""
    user = await user_service.get_or_create_user(callback.from_user.id)
    
    # Clean up temp data
    if user.user_id in temp_build_data:
        del temp_build_data[user.user_id]
    
    await callback.message.edit_text(get_text("back", user.language))
    await state.clear()
    await callback.answer()


async def format_generated_build(build, budget: int, language: str, tier_eval: TierEvaluator) -> str:
    """Format generated build for display."""
    text = f"**🎲 {get_text('build_generated', language)}**\n\n"
    text += f"🔫 **{build.weapon_name}**\n"
    text += f"{get_text('build_tier', language, tier=build.tier_rating.value)}\n\n"
    
    # Tier description
    tier_desc = tier_eval.get_tier_description(build.tier_rating, language)
    text += f"{tier_desc}\n\n"
    
    # Budget info
    text += get_text("build_spent", language, cost=build.total_cost, budget=budget) + "\n"
    text += get_text("build_remaining", language, remaining=build.remaining_budget) + "\n\n"
    
    # Stats
    text += f"{get_text('build_stats', language)}\n"
    if build.ergonomics:
        text += get_text("build_ergonomics", language, value=build.ergonomics) + "\n"
    if build.recoil_vertical:
        text += get_text("build_recoil_v", language, value=build.recoil_vertical) + "\n"
    
    # Availability
    if build.available_from:
        sources = ", ".join(build.available_from)
        text += f"\n{get_text('build_available_from', language, sources=sources)}\n"
    
    # Modules
    if build.modules:
        text += f"\n{get_text('build_modules_list', language)}\n"
        count = 0
        for slot_name, module_data in build.modules.items():
            if count >= 10:  # Limit to 10 modules for display
                text += f"  ... и ещё {len(build.modules) - 10} модулей\n"
                break
            module_name = module_data.get("name", slot_name)
            text += f"  • {module_name}\n"
            count += 1
    
    # Improvement suggestions
    suggestions = tier_eval.get_improvement_suggestions(
        tier=build.tier_rating,
        ergonomics=build.ergonomics,
        recoil_vertical=build.recoil_vertical,
        has_sight=any("sight" in s.lower() for s in build.modules.keys()),
        has_stock=any("stock" in s.lower() for s in build.modules.keys()),
        has_grip=any("grip" in s.lower() for s in build.modules.keys()),
        language=language
    )
    
    if suggestions and build.tier_rating.value in ["C", "D"]:
        text += f"\n💡 **{'Рекомендации' if language == 'ru' else 'Suggestions'}:**\n"
        for suggestion in suggestions[:3]:  # Limit to 3 suggestions
            text += f"{suggestion}\n"
    
    return text
