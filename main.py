"""
Main entry point for EFT Helper Telegram Bot.
Единственная точка входа для бота - следуйте техническому заданию.
"""
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database import Database
from api_clients import TarkovAPIClient
from services import WeaponService, BuildService, UserService, SyncService
from handlers import common, search, builds, loyalty, tier_list, settings

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class BotApplication:
    """Main bot application class."""
    
    def __init__(self):
        # Configuration
        self.bot_token = os.getenv("BOT_TOKEN")
        if not self.bot_token or self.bot_token == "your_telegram_bot_token_here":
            raise ValueError("BOT_TOKEN not configured in .env file")
        
        # Database
        self.db = Database("data/eft_helper.db")
        
        # API Client (centralized)
        self.api_client = TarkovAPIClient()
        
        # Services (business logic layer)
        self.weapon_service = WeaponService(self.db, self.api_client)
        self.build_service = BuildService(self.db, self.api_client)
        self.user_service = UserService(self.db)
        self.sync_service = SyncService(self.db, self.api_client)
        
        # Bot and Dispatcher
        self.bot = Bot(token=self.bot_token)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
    
    async def setup(self):
        """Initialize database and prepare bot."""
        logger.info("Initializing database...")
        await self.db.init_db()
        
        # Check if database needs initial population
        async with self.db.db_path as _:
            pass  # Database is ready
        
        logger.info("Database initialized successfully")
    
    def register_handlers(self):
        """Register all bot handlers."""
        self.dp.include_router(common.router)
        self.dp.include_router(search.router)
        self.dp.include_router(builds.router)
        self.dp.include_router(loyalty.router)
        self.dp.include_router(tier_list.router)
        self.dp.include_router(settings.router)
        
        logger.info("Handlers registered")
    
    def register_middleware(self):
        """Register middleware to inject dependencies."""
        @self.dp.update.outer_middleware()
        async def inject_services(handler, event, data):
            """Inject services into handlers."""
            data["db"] = self.db
            data["weapon_service"] = self.weapon_service
            data["build_service"] = self.build_service
            data["user_service"] = self.user_service
            data["api_client"] = self.api_client
            return await handler(event, data)
        
        @self.dp.error()
        async def error_handler(event, exception):
            """Global error handler."""
            logger.error(f"Error occurred: {exception}", exc_info=True)
            return True
        
        logger.info("Middleware registered")
    
    async def start(self):
        """Start the bot."""
        await self.setup()
        self.register_handlers()
        self.register_middleware()
        
        logger.info("=" * 60)
        logger.info("  EFT Helper Bot Started")
        logger.info("=" * 60)
        
        try:
            await self.dp.start_polling(
                self.bot,
                allowed_updates=self.dp.resolve_used_update_types()
            )
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Shutting down bot...")
        await self.bot.session.close()
        await self.api_client.close()
        logger.info("Bot stopped")


async def main():
    """Main function."""
    try:
        app = BotApplication()
        await app.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Run bot
    asyncio.run(main())
