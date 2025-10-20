"""Central AI assistant service - handles all user messages and voice input."""
import logging
from typing import Optional, Dict
from aiogram.types import Message
from api_clients import TarkovAPIClient
from database import Database
from localization import get_text
from .ai_generation_service import AIGenerationService

logger = logging.getLogger(__name__)


class AIAssistant:
    """Nikita Buyanov AI Assistant - central message handler."""
    
    def __init__(
        self,
        api_client: TarkovAPIClient,
        db: Database,
        ai_generation_service: AIGenerationService
    ):
        self.api = api_client
        self.db = db
        self.ai_gen = ai_generation_service
        self.fallback_enabled = True
    
    async def handle_message(self, message: Message, user_language: str = "ru") -> str:
        """
        Handle incoming text message.
        
        Args:
            message: Telegram message object
            user_language: User's language preference
            
        Returns:
            Response text to send to user
        """
        user_id = message.from_user.id
        user_text = message.text
        
        logger.info(f"AI Assistant handling message from user {user_id}: {user_text[:50]}...")
        
        # Check if Ollama is available
        ollama_available = await self.ai_gen.check_ollama_available()
        
        if not ollama_available:
            logger.warning("Ollama not available, using fallback")
            return await self._fallback_response(user_text, user_id, user_language)
        
        # Try AI generation
        try:
            # Detect if this is a build request
            if self._is_build_request(user_text, user_language):
                build_data = await self.ai_gen.generate_build(
                    user_text,
                    user_id,
                    user_language
                )
                
                if build_data and build_data.get("text"):
                    return build_data["text"]
                else:
                    logger.warning("AI generation returned no result")
                    return await self._fallback_response(user_text, user_id, user_language)
            
            # General conversation/questions
            response = await self._handle_general_query(user_text, user_id, user_language)
            return response
            
        except Exception as e:
            logger.error(f"Error in AI assistant: {e}", exc_info=True)
            return await self._fallback_response(user_text, user_id, user_language)
    
    async def handle_voice(self, message: Message, voice_file_path: str, user_language: str = "ru") -> str:
        """
        Handle incoming voice message.
        
        Args:
            message: Telegram message object
            voice_file_path: Path to downloaded voice file
            user_language: User's language preference
            
        Returns:
            Response text to send to user
        """
        user_id = message.from_user.id
        
        logger.info(f"AI Assistant handling voice message from user {user_id}")
        
        try:
            # Import voice transcriber
            from utils.voice_transcriber import VoiceTranscriber
            
            transcriber = VoiceTranscriber()
            
            # Transcribe voice to text
            transcribed_text = await transcriber.transcribe(voice_file_path, user_language)
            
            if not transcribed_text:
                return get_text("voice_transcription_failed", user_language)
            
            logger.info(f"Transcribed voice: {transcribed_text}")
            
            # Create a mock message object with transcribed text
            class MockMessage:
                def __init__(self, text, from_user):
                    self.text = text
                    self.from_user = from_user
            
            mock_message = MockMessage(transcribed_text, message.from_user)
            
            # Handle as text message
            response = await self.handle_message(mock_message, user_language)
            
            # Prepend transcription
            transcription_prefix = get_text("voice_transcribed", user_language, text=transcribed_text)
            return f"{transcription_prefix}\n\n{response}"
            
        except ImportError:
            logger.error("Voice transcriber not available")
            return get_text("voice_not_supported", user_language)
        except Exception as e:
            logger.error(f"Error handling voice: {e}", exc_info=True)
            return get_text("voice_processing_error", user_language)
    
    def _is_build_request(self, text: str, language: str) -> bool:
        """Check if message is a build request."""
        text_lower = text.lower()
        
        build_keywords_ru = [
            "сборк", "сделай", "собери", "покажи", "нужна", "хочу",
            "построй", "создай", "подбери", "рекомендуй"
        ]
        
        build_keywords_en = [
            "build", "make", "create", "show", "need", "want",
            "recommend", "suggest", "assemble"
        ]
        
        keywords = build_keywords_ru if language == "ru" else build_keywords_en
        
        return any(keyword in text_lower for keyword in keywords)
    
    async def _handle_general_query(self, text: str, user_id: int, language: str) -> str:
        """Handle general questions and conversation."""
        # Check if Ollama is available
        ollama_available = await self.ai_gen.check_ollama_available()
        
        if not ollama_available:
            return get_text("ai_not_available", language)
        
        # Build context for general query
        from .context_builder import ContextBuilder
        context_builder = ContextBuilder(self.api, self.db)
        
        user_context = await context_builder.build_user_context(user_id)
        
        # Create prompt for general conversation
        if language == "ru":
            prompt = f"""Ты — Никита Буянов, главный разработчик Escape from Tarkov.
Отвечай на вопросы игроков дружелюбно и профессионально.

Информация о пользователе:
{user_context}

Вопрос игрока: {text}

Твой ответ:"""
        else:
            prompt = f"""You are Nikita Buyanov, lead developer of Escape from Tarkov.
Answer player questions in a friendly and professional manner.

User information:
{user_context}

Player's question: {text}

Your response:"""
        
        try:
            response = await self.ai_gen._call_ollama(prompt)
            if response:
                return f"🤖 Никита Буянов:\n{response}" if language == "ru" else f"🤖 Nikita Buyanov:\n{response}"
            else:
                return get_text("ai_no_response", language)
        except Exception as e:
            logger.error(f"Error in general query: {e}")
            return get_text("ai_error", language)
    
    async def _fallback_response(self, text: str, user_id: int, language: str) -> str:
        """Fallback response when AI is not available."""
        # Provide helpful response directing to menu options
        fallback_text = get_text("ai_fallback", language)
        
        # Try to provide relevant menu suggestions based on keywords
        text_lower = text.lower()
        
        suggestions = []
        
        if any(kw in text_lower for kw in ["сборк", "build", "оружи", "weapon"]):
            suggestions.append(get_text("suggestion_search_weapon", language))
            suggestions.append(get_text("suggestion_random_build", language))
        
        if any(kw in text_lower for kw in ["квест", "quest", "оружейник", "gunsmith"]):
            suggestions.append(get_text("suggestion_quest_builds", language))
        
        if any(kw in text_lower for kw in ["мета", "meta", "лучш", "best"]):
            suggestions.append(get_text("suggestion_meta_builds", language))
        
        if suggestions:
            suggestions_text = "\n".join(f"• {s}" for s in suggestions)
            return f"{fallback_text}\n\n{get_text('suggestions', language)}:\n{suggestions_text}"
        
        return fallback_text
    
    async def generate_quest_build_response(
        self, 
        quest_name: str, 
        user_id: int, 
        language: str = "ru"
    ) -> str:
        """
        Generate build response for a specific quest.
        
        Args:
            quest_name: Name of the quest
            user_id: Telegram user ID
            language: User's language preference
            
        Returns:
            Formatted response with quest build
        """
        ollama_available = await self.ai_gen.check_ollama_available()
        
        if not ollama_available:
            logger.warning("Ollama not available for quest build")
            # Fallback to existing quest build logic would go here
            return get_text("ai_not_available", language)
        
        try:
            build_data = await self.ai_gen.generate_quest_build(
                quest_name,
                user_id,
                language
            )
            
            if build_data and build_data.get("text"):
                return build_data["text"]
            else:
                return get_text("quest_build_failed", language)
                
        except Exception as e:
            logger.error(f"Error generating quest build: {e}", exc_info=True)
            return get_text("ai_error", language)
    
    async def generate_meta_build_response(
        self,
        weapon_name: Optional[str],
        user_id: int,
        language: str = "ru"
    ) -> str:
        """
        Generate meta build response.
        
        Args:
            weapon_name: Optional specific weapon name
            user_id: Telegram user ID
            language: User's language preference
            
        Returns:
            Formatted response with meta build
        """
        if weapon_name:
            request = get_text("meta_build_request", language, weapon=weapon_name)
        else:
            request = get_text("meta_build_request_general", language)
        
        return await self.handle_message(
            type('obj', (object,), {
                'text': request,
                'from_user': type('obj', (object,), {'id': user_id})()
            })(),
            language
        )
