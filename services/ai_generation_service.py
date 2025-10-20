"""AI-powered build generation service using Qwen3-8B via Ollama."""
import logging
import json
import re
from typing import Dict, List, Optional, Tuple
from api_clients import TarkovAPIClient
from database import Database
from .context_builder import ContextBuilder

logger = logging.getLogger(__name__)


class AIGenerationService:
    """Service for AI-powered weapon build generation."""
    
    def __init__(
        self, 
        api_client: TarkovAPIClient,
        db: Database,
        ollama_url: str = "http://localhost:11434"
    ):
        self.api = api_client
        self.db = db
        self.context_builder = ContextBuilder(api_client, db)
        self.ollama_url = ollama_url
        self.model = "qwen3:8b"  # Using Qwen3-8B as specified in technical requirements
    
    async def generate_build(
        self,
        user_request: str,
        user_id: int,
        language: str = "ru"
    ) -> Optional[Dict]:
        """
        Generate weapon build based on user request using LLM.
        
        Args:
            user_request: User's natural language request
            user_id: Telegram user ID
            language: User's language (ru/en)
            
        Returns:
            Dict with build information or None if generation failed
        """
        try:
            # Parse user intent
            intent = await self._parse_intent(user_request, language)
            
            # Build context
            context = await self._build_generation_context(intent, user_id, language)
            
            # Generate build via LLM
            prompt = self._create_build_prompt(user_request, context, language)
            
            response = await self._call_ollama(prompt)
            if not response:
                logger.warning("No response from Ollama")
                return None
            
            # Parse response into structured build
            build_data = self._parse_build_response(response, language)
            
            return build_data
            
        except Exception as e:
            logger.error(f"Error generating build: {e}", exc_info=True)
            return None
    
    async def generate_quest_build(
        self,
        quest_name: str,
        user_id: int,
        language: str = "ru"
    ) -> Optional[Dict]:
        """
        Generate build specifically for a quest.
        
        Args:
            quest_name: Name of the quest
            user_id: Telegram user ID
            language: User's language (ru/en)
            
        Returns:
            Dict with build information or None if generation failed
        """
        try:
            # Get quest details
            quest_context = await self.context_builder.build_quest_context(quest_name, language)
            user_context = await self.context_builder.build_user_context(user_id)
            
            prompt = self._create_quest_build_prompt(quest_name, quest_context, user_context, language)
            
            response = await self._call_ollama(prompt)
            if not response:
                return None
            
            build_data = self._parse_build_response(response, language)
            build_data["quest_name"] = quest_name
            
            return build_data
            
        except Exception as e:
            logger.error(f"Error generating quest build: {e}", exc_info=True)
            return None
    
    async def _parse_intent(self, user_request: str, language: str) -> Dict:
        """Parse user intent from request."""
        intent = {
            "type": "custom",  # custom, quest, meta, random
            "weapon_name": None,
            "budget": None,
            "preferences": []
        }
        
        request_lower = user_request.lower()
        
        # Detect quest requests
        quest_keywords = ["квест", "quest", "оружейник", "gunsmith", "механик", "mechanic"]
        if any(kw in request_lower for kw in quest_keywords):
            intent["type"] = "quest"
        
        # Detect meta requests
        meta_keywords = ["мета", "meta", "лучш", "best", "топ", "top"]
        if any(kw in request_lower for kw in meta_keywords):
            intent["type"] = "meta"
        
        # Extract budget
        budget_pattern = r'(\d+)\s*[кkк]?(?:\s*руб|₽)?'
        budget_matches = re.findall(budget_pattern, request_lower)
        if budget_matches:
            budget_str = budget_matches[0]
            budget_value = int(budget_str)
            # Handle 'k' suffix
            if 'k' in request_lower or 'к' in request_lower:
                budget_value *= 1000
            intent["budget"] = budget_value
        
        # Extract weapon name (simple heuristic)
        weapon_keywords = [
            "ак", "ak", "м4", "m4", "мр", "mp", "свд", "svd", "вал", "val", 
            "вск", "vsk", "впо", "vpo", "сайга", "saiga", "вепрь", "vepr"
        ]
        for keyword in weapon_keywords:
            if keyword in request_lower:
                # Try to extract weapon name around keyword
                words = user_request.split()
                for word in words:
                    if keyword in word.lower():
                        intent["weapon_name"] = word
                        break
        
        # Extract preferences
        if "эргономика" in request_lower or "ergonomic" in request_lower or "ergo" in request_lower:
            intent["preferences"].append("ergonomics")
        if "отдача" in request_lower or "recoil" in request_lower:
            intent["preferences"].append("recoil")
        if "прицел" in request_lower or "sight" in request_lower or "scope" in request_lower:
            intent["preferences"].append("sight")
        
        return intent
    
    async def _build_generation_context(
        self, 
        intent: Dict, 
        user_id: int, 
        language: str
    ) -> str:
        """Build context for LLM based on intent."""
        context_parts = []
        
        # User context
        user_ctx = await self.context_builder.build_user_context(user_id)
        context_parts.append(user_ctx)
        
        # Weapon context
        if intent.get("weapon_name"):
            # Search for specific weapon
            weapons = await self.api.search_items(intent["weapon_name"], item_types=["gun"])
            if weapons:
                weapon = weapons[0]
                weapon_ctx = await self.context_builder.build_weapon_context(weapon["id"], language)
                context_parts.append(weapon_ctx)
                
                # Module context
                module_ctx = await self.context_builder.build_modules_context(weapon["id"], language)
                context_parts.append(module_ctx)
        else:
            # General weapon context
            weapon_ctx = await self.context_builder.build_weapon_context(None, language)
            context_parts.append(weapon_ctx)
        
        # Quest context if needed
        if intent["type"] == "quest":
            quest_ctx = await self.context_builder.build_quest_context(None, language)
            context_parts.append(quest_ctx)
        
        return "\n\n---\n\n".join(context_parts)
    
    def _create_build_prompt(self, user_request: str, context: str, language: str) -> str:
        """Create prompt for LLM build generation."""
        if language == "ru":
            system_prompt = """Ты — Никита Буянов, главный разработчик Escape from Tarkov и эксперт по игре. 
Твоя задача — помогать игрокам создавать оптимальные сборки оружия на основе актуальных данных из tarkov.dev.

ВАЖНЫЕ ПРАВИЛА:
1. Всегда используй ТОЛЬКО данные из предоставленного контекста (ID оружия, модулей, цены)
2. Генерируй сборки с учётом совместимости слотов (каждый модуль должен подходить к своему слоту)
3. Учитывай бюджет пользователя (если указан)
4. Структурируй ответ иерархически: базовое оружие → каждый слот → модули → характеристики
5. Добавляй короткое обоснование выбора модулей
6. Указывай итоговую стоимость и доступность (торговцы/барахолка)

ФОРМАТ ОТВЕТА:
🤖 Никита Буянов:
Вот ваша сборка для [ОРУЖИЕ]:

1️⃣ **Базовое оружие:** [НАЗВАНИЕ] (ID: [ID])
   - Цена: [ЦЕНА] ₽
   - Базовая эргономика: [ЗНАЧЕНИЕ]
   - Базовая отдача: [ЗНАЧЕНИЕ]
   📍 [ТОРГОВЕЦ] L[УРОВЕНЬ]

2️⃣ **[СЛОТ 1]:**
   а) [МОДУЛЬ] — [ЦЕНА] ₽ (Эргономика: +X, Отдача: -Y)
      📍 [ТОРГОВЕЦ] L[УРОВЕНЬ] или Flea Market

3️⃣ **[СЛОТ 2]:**
   а) [МОДУЛЬ] — [ЦЕНА] ₽
      📍 [ТОРГОВЕЦ] L[УРОВЕНЬ] или Flea Market

...

📊 **Характеристики:**
   - Эргономика: [ИТОГ]
   - Вертикальная отдача: [ИТОГ]
   - Горизонтальная отдача: [ИТОГ]

💰 **Итого:** [СУММА] ₽

💡 **Обоснование:** [1-2 предложения почему выбраны эти модули]
"""
        else:
            system_prompt = """You are Nikita Buyanov, lead developer of Escape from Tarkov and game expert.
Your task is to help players create optimal weapon builds based on actual data from tarkov.dev.

IMPORTANT RULES:
1. ONLY use data from provided context (weapon IDs, module IDs, prices)
2. Generate builds considering slot compatibility (each module must fit its slot)
3. Consider user's budget (if specified)
4. Structure response hierarchically: base weapon → each slot → modules → stats
5. Add brief reasoning for module choices
6. Include total cost and availability (traders/flea)

RESPONSE FORMAT:
🤖 Nikita Buyanov:
Here's your build for [WEAPON]:

1️⃣ **Base weapon:** [NAME] (ID: [ID])
   - Price: [PRICE] ₽
   - Base ergonomics: [VALUE]
   - Base recoil: [VALUE]
   📍 [TRADER] L[LEVEL]

2️⃣ **[SLOT 1]:**
   a) [MODULE] — [PRICE] ₽ (Ergonomics: +X, Recoil: -Y)
      📍 [TRADER] L[LEVEL] or Flea Market

3️⃣ **[SLOT 2]:**
   a) [MODULE] — [PRICE] ₽
      📍 [TRADER] L[LEVEL] or Flea Market

...

📊 **Stats:**
   - Ergonomics: [TOTAL]
   - Vertical recoil: [TOTAL]
   - Horizontal recoil: [TOTAL]

💰 **Total:** [SUM] ₽

💡 **Reasoning:** [1-2 sentences why these modules were chosen]
"""
        
        prompt = f"""{system_prompt}

ДАННЫЕ ИЗ TARKOV.DEV:
{context}

ЗАПРОС ПОЛЬЗОВАТЕЛЯ:
{user_request}

Сгенерируй сборку на основе этих данных:"""
        
        return prompt
    
    def _create_quest_build_prompt(
        self, 
        quest_name: str, 
        quest_context: str, 
        user_context: str,
        language: str
    ) -> str:
        """Create prompt specifically for quest builds."""
        if language == "ru":
            prompt = f"""Ты — Никита Буянов, эксперт по квестам Escape from Tarkov.
Создай сборку для квеста "{quest_name}".

ВАЖНО: Сборка должна ТОЧНО соответствовать требованиям квеста (конкретные модули, характеристики).

ИНФОРМАЦИЯ О КВЕСТЕ:
{quest_context}

{user_context}

Создай сборку, которая выполнит все требования квеста:"""
        else:
            prompt = f"""You are Nikita Buyanov, expert on Escape from Tarkov quests.
Create a build for quest "{quest_name}".

IMPORTANT: Build must EXACTLY match quest requirements (specific modules, stats).

QUEST INFORMATION:
{quest_context}

{user_context}

Create a build that fulfills all quest requirements:"""
        
        return prompt
    
    async def _call_ollama(self, prompt: str) -> Optional[str]:
        """Call Ollama API to generate response."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 2048
                    }
                }
                
                async with session.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status != 200:
                        logger.error(f"Ollama API error: {response.status}")
                        return None
                    
                    result = await response.json()
                    return result.get("response", "")
        
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}", exc_info=True)
            return None
    
    def _parse_build_response(self, response: str, language: str) -> Dict:
        """Parse LLM response into structured build data."""
        build_data = {
            "text": response,
            "weapon": None,
            "modules": [],
            "stats": {},
            "total_cost": None,
            "reasoning": None
        }
        
        try:
            # Extract weapon name
            weapon_pattern = r"(?:Base weapon|Базовое оружие):\s*\*\*([^\*]+)\*\*"
            weapon_match = re.search(weapon_pattern, response, re.IGNORECASE)
            if weapon_match:
                build_data["weapon"] = weapon_match.group(1).strip()
            
            # Extract total cost
            cost_pattern = r"(?:Total|Итого):\s*([0-9,]+)\s*₽"
            cost_match = re.search(cost_pattern, response)
            if cost_match:
                cost_str = cost_match.group(1).replace(",", "")
                build_data["total_cost"] = int(cost_str)
            
            # Extract stats
            ergo_pattern = r"(?:Ergonomics|Эргономика):\s*([0-9]+)"
            ergo_match = re.search(ergo_pattern, response)
            if ergo_match:
                build_data["stats"]["ergonomics"] = int(ergo_match.group(1))
            
            recoil_v_pattern = r"(?:Vertical recoil|Вертикальная отдача):\s*([0-9]+)"
            recoil_v_match = re.search(recoil_v_pattern, response)
            if recoil_v_match:
                build_data["stats"]["recoil_vertical"] = int(recoil_v_match.group(1))
            
            # Extract reasoning
            reasoning_pattern = r"(?:Reasoning|Обоснование):\s*(.+?)(?:\n\n|$)"
            reasoning_match = re.search(reasoning_pattern, response, re.DOTALL)
            if reasoning_match:
                build_data["reasoning"] = reasoning_match.group(1).strip()
        
        except Exception as e:
            logger.error(f"Error parsing build response: {e}")
        
        return build_data
    
    async def check_ollama_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ollama_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False
