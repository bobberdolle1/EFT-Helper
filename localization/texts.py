"""Localization texts for the EFT Helper bot."""

TEXTS = {
    "ru": {
        # Main menu
        "main_menu": "🏠 Главное меню",
        "search_weapon": "🔍 Поиск оружия",
        "all_quest_builds": "📜 Все квестовые сборки",
        "random_build": "🎲 Случайная сборка",
        "meta_builds": "⚔️ Мета-сборки",
        "loyalty_builds": "🤝 Сборки по лояльности торговцев",
        "best_weapons": "⭐ Лучшее оружие",
        "settings": "⚙️ Настройки",
        
        # Welcome message
        "welcome": "👋 Добро пожаловать в EFT Helper!\n\nЭтот бот поможет вам подобрать оптимальные сборки оружия для Escape from Tarkov.\n\nВыберите действие из меню ниже:",
        
        # Search
        "enter_weapon_name": "🔍 Введите название оружия для поиска:\n\nНапример: AK-74N, MP-153, M4A1",
        "weapon_not_found": "❌ Оружие не найдено. Попробуйте другой запрос.",
        "select_weapon": "Выберите оружие:",
        "no_weapons_found": "❌ Оружие не найдено в базе данных.",
        
        # Build filters
        "select_build_type": "Выберите тип сборки для {weapon}:",
        "random_build_btn": "🎲 Случайная",
        "meta_build_btn": "⚔️ Мета",
        "quest_build_btn": "📜 Квестовая",
        "loyalty_build_btn": "🤝 По лояльности",
        
        # Build display
        "build_card_title": "🔫 {weapon}\n",
        "build_category": "📂 Категория: {category}",
        "build_quest": "📜 Квест: {quest}",
        "build_modules": "🔧 Модули:",
        "build_total_cost": "💰 Общая стоимость: {cost} ₽",
        "build_loyalty": "🤝 Минимальная лояльность: {level}",
        "build_planner": "🔗 [Открыть в планировщике]({link})",
        "no_builds_found": "❌ Сборки не найдены для этого оружия.",
        
        # Quest builds
        "quest_builds_list": "📜 Квестовые сборки\n\nВыберите квест:",
        "no_quest_builds": "❌ Квестовые сборки не найдены.",
        "quest_description": "📝 {description}",
        "loading_quests": "⏳ Загружаю квесты...",
        "quest_builds_title": "📜 Квестовые сборки",
        "all_quest_builds_title": "📜 Все квестовые сборки",
        "select_quest": "Выберите квест для просмотра информации:",
        "quest_trader": "Торговец",
        "quest_level": "Требуемый уровень",
        "quest_experience": "Опыт",
        "quest_map": "Карта",
        "quest_required_tasks": "Требуемые квесты",
        "quest_objectives": "Цели",
        "quest_optional": "опц.",
        "quest_and_more": "и ещё",
        "quest_more_objectives": "целей",
        "quest_recommended_build": "Рекомендуемая сборка",
        
        # Random build
        "random_build_title": "🎲 Случайная сборка",
        "generating_random": "🎲 Генерирую случайную сборку...",
        "truly_random_build": "🎰 Рандомная сборка",
        "generating_truly_random": "🎰 Генерирую по-настоящему рандомную сборку...",
        "truly_random_build_title": "🎰 Рандомная сборка",
        
        # Meta builds
        "meta_builds_title": "⚔️ Мета-сборки 2025",
        "meta_builds_desc": "Актуальные топовые сборки по категориям:",
        "no_meta_builds": "❌ Мета-сборки не найдены.",
        
        # Loyalty builds
        "select_trader": "🤝 Выберите торговца:",
        "select_loyalty_level": "Выберите уровень лояльности для {trader}:",
        "loyalty_level": "Уровень {level}",
        "no_loyalty_builds": "❌ Нет доступных сборок для {trader} (уровень {level}).",
        "setup_loyalty_levels": "🤝 Настройка уровней лояльности\n\nУкажите ваши текущие уровни лояльности к торговцам. Это позволит боту показывать только доступные вам сборки.",
        "current_loyalty_levels": "Текущие уровни лояльности:",
        "trader_level_set": "✅ Уровень лояльности к {trader} установлен: {level}",
        "loyalty_levels_saved": "✅ Уровни лояльности сохранены!",
        "show_available_builds": "📋 Показать доступные сборки",
        "reset_loyalty_levels": "🔄 Сбросить уровни",
        
        # Best weapons
        "best_weapons_title": "⭐ Лучшее оружие по категориям",
        "tier_s": "🏆 S-Tier (Лучшие)",
        "tier_a": "🥇 A-Tier (Отличные)",
        "tier_b": "🥈 B-Tier (Хорошие)",
        "tier_c": "🥉 C-Tier (Средние)",
        "tier_d": "📊 D-Tier (Слабые)",
        "no_tier_weapons": "❌ Оружие не найдено для этого уровня.",
        
        # Settings
        "settings_title": "⚙️ Настройки",
        "current_language": "Текущий язык: {language_name}",
        "change_language": "Изменить язык:",
        "language_changed": "✅ Язык изменен на: {language_name}",
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        
        # Traders
        "prapor": "Прапор",
        "therapist": "Терапевт",
        "fence": "Барахольщик",
        "skier": "Лыжник",
        "peacekeeper": "Миротворец",
        "mechanic": "Механик",
        "ragman": "Барыга",
        "jaeger": "Егерь",
        "lightkeeper": "Смотритель",
        # Trader names mapping (for API responses)
        "trader_prapor": "Прапор",
        "trader_therapist": "Терапевт",
        "trader_fence": "Барахольщик",
        "trader_skier": "Лыжник",
        "trader_peacekeeper": "Миротворец",
        "trader_mechanic": "Механик",
        "trader_ragman": "Барыга",
        "trader_jaeger": "Егерь",
        "trader_lightkeeper": "Смотритель",
        
        # Categories
        "assault_rifle": "Штурмовая винтовка",
        "smg": "Пистолет-пулемет",
        "sniper": "Снайперская винтовка",
        "dmr": "Марксманская винтовка",
        "shotgun": "Дробовик",
        "pistol": "Пистолет",
        "lmg": "Ручной пулемет",
        
        # Build categories
        "category_random": "Случайная",
        "category_meta": "Мета",
        "category_quest": "Квестовая",
        "category_loyalty": "По лояльности",
        
        # Weapon categories
        "select_category": "Выберите категорию оружия:",
        "category_pistols": "🔫 Пистолеты",
        "category_smg": "🔫 Пистолеты-пулемёты",
        "category_assault_rifles": "🔫 Штурмовые винтовки",
        "category_dmr": "🔫 Марксманские винтовки",
        "category_sniper_rifles": "🔫 Снайперские винтовки",
        "category_shotguns": "🔫 Дробовики",
        "category_lmg": "🔫 Пулемёты",
        "search_by_name": "🔍 Поиск по названию",
        
        # Common
        "back": "◀️ Назад",
        "main_menu_btn": "🏠 Главное меню",
        "error": "❌ Произошла ошибка. Попробуйте снова.",
    },
    "en": {
        # Main menu
        "main_menu": "🏠 Main Menu",
        "search_weapon": "🔍 Search Weapon",
        "all_quest_builds": "📜 All Quest Builds",
        "random_build": "🎲 Random Build",
        "meta_builds": "⚔️ Meta Builds",
        "loyalty_builds": "🤝 Loyalty Builds",
        "best_weapons": "⭐ Best Weapons",
        "settings": "⚙️ Settings",
        
        # Welcome message
        "welcome": "👋 Welcome to EFT Helper!\n\nThis bot will help you find optimal weapon builds for Escape from Tarkov.\n\nChoose an action from the menu below:",
        
        # Search
        "enter_weapon_name": "🔍 Enter weapon name to search:\n\nFor example: AK-74N, MP-153, M4A1",
        "weapon_not_found": "❌ Weapon not found. Try another query.",
        "select_weapon": "Select weapon:",
        "no_weapons_found": "❌ No weapons found in database.",
        
        # Build filters
        "select_build_type": "Select build type for {weapon}:",
        "random_build_btn": "🎲 Random",
        "meta_build_btn": "⚔️ Meta",
        "quest_build_btn": "📜 Quest",
        "loyalty_build_btn": "🤝 By Loyalty",
        
        # Build display
        "build_card_title": "🔫 {weapon}\n",
        "build_category": "📂 Category: {category}",
        "build_quest": "📜 Quest: {quest}",
        "build_modules": "🔧 Modules:",
        "build_total_cost": "💰 Total Cost: {cost} ₽",
        "build_loyalty": "🤝 Minimum Loyalty: {level}",
        "build_planner": "🔗 [Open in Planner]({link})",
        "no_builds_found": "❌ No builds found for this weapon.",
        
        # Quest builds
        "quest_builds_list": "📜 Quest Builds\n\nSelect a quest:",
        "no_quest_builds": "❌ No quest builds found.",
        "quest_description": "📝 {description}",
        "loading_quests": "⏳ Loading quests...",
        "quest_builds_title": "📜 Quest Builds",
        "all_quest_builds_title": "📜 All Quest Builds",
        "select_quest": "Select a quest to view information:",
        "quest_trader": "Trader",
        "quest_level": "Required Level",
        "quest_experience": "Experience",
        "quest_map": "Map",
        "quest_required_tasks": "Required Tasks",
        "quest_objectives": "Objectives",
        "quest_optional": "opt.",
        "quest_and_more": "and",
        "quest_more_objectives": "more objectives",
        "quest_recommended_build": "Recommended Build",
        
        # Random build
        "random_build_title": "🎲 Random Build",
        "generating_random": "🎲 Generating random build...",
        "truly_random_build": "🎰 True Random Build",
        "generating_truly_random": "🎰 Generating truly random build...",
        "truly_random_build_title": "🎰 True Random Build",
        
        # Meta builds
        "meta_builds_title": "⚔️ Meta Builds 2025",
        "meta_builds_desc": "Current top builds by category:",
        "no_meta_builds": "❌ No meta builds found.",
        
        # Loyalty builds
        "select_trader": "🤝 Select a trader:",
        "select_loyalty_level": "Select loyalty level for {trader}:",
        "loyalty_level": "Level {level}",
        "no_loyalty_builds": "❌ No available builds for {trader} (level {level}).",
        "setup_loyalty_levels": "🤝 Loyalty Levels Setup\n\nSet your current trader loyalty levels. This will allow the bot to show only builds available to you.",
        "current_loyalty_levels": "Current loyalty levels:",
        "trader_level_set": "✅ Loyalty level for {trader} set to: {level}",
        "loyalty_levels_saved": "✅ Loyalty levels saved!",
        "show_available_builds": "📋 Show Available Builds",
        "reset_loyalty_levels": "🔄 Reset Levels",
        
        # Best weapons
        "best_weapons_title": "⭐ Best Weapons by Category",
        "tier_s": "🏆 S-Tier (Best)",
        "tier_a": "🥇 A-Tier (Excellent)",
        "tier_b": "🥈 B-Tier (Good)",
        "tier_c": "🥉 C-Tier (Average)",
        "tier_d": "📊 D-Tier (Weak)",
        "no_tier_weapons": "❌ No weapons found for this tier.",
        
        # Settings
        "settings_title": "⚙️ Settings",
        "current_language": "Current language: {language_name}",
        "change_language": "Change language:",
        "language_changed": "✅ Language changed to: {language_name}",
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        
        # Traders
        "prapor": "Prapor",
        "therapist": "Therapist",
        "fence": "Fence",
        "skier": "Skier",
        "peacekeeper": "Peacekeeper",
        "mechanic": "Mechanic",
        "ragman": "Ragman",
        "jaeger": "Jaeger",
        "lightkeeper": "Lightkeeper",
        # Trader names mapping (for API responses)
        "trader_prapor": "Prapor",
        "trader_therapist": "Therapist",
        "trader_fence": "Fence",
        "trader_skier": "Skier",
        "trader_peacekeeper": "Peacekeeper",
        "trader_mechanic": "Mechanic",
        "trader_ragman": "Ragman",
        "trader_jaeger": "Jaeger",
        "trader_lightkeeper": "Lightkeeper",
        
        # Categories
        "assault_rifle": "Assault Rifle",
        "smg": "Submachine Gun",
        "sniper": "Sniper Rifle",
        "dmr": "Designated Marksman Rifle",
        "shotgun": "Shotgun",
        "pistol": "Pistol",
        "lmg": "Light Machine Gun",
        
        # Build categories
        "category_random": "Random",
        "category_meta": "Meta",
        "category_quest": "Quest",
        "category_loyalty": "By Loyalty",
        
        # Weapon categories
        "select_category": "Select weapon category:",
        "category_pistols": "🔫 Pistols",
        "category_smg": "🔫 Submachine Guns",
        "category_assault_rifles": "🔫 Assault Rifles",
        "category_dmr": "🔫 Marksman Rifles",
        "category_sniper_rifles": "🔫 Sniper Rifles",
        "category_shotguns": "🔫 Shotguns",
        "category_lmg": "🔫 Machine Guns",
        "search_by_name": "🔍 Search by Name",
        
        # Common
        "back": "◀️ Back",
        "main_menu_btn": "🏠 Main Menu",
        "error": "❌ An error occurred. Please try again.",
    }
}


def get_text(key: str, language: str = "ru", **kwargs) -> str:
    """Get localized text by key."""
    text = TEXTS.get(language, TEXTS["ru"]).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
