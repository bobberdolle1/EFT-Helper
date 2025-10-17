"""Расчет характеристик сборок оружия."""
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class BuildStats:
    """Характеристики сборки."""
    ergonomics: float
    vertical_recoil: float
    horizontal_recoil: float
    weight: float
    accuracy: float
    effective_distance: int
    fire_rate: int
    moa: float
    
    @property
    def recoil_sum(self) -> float:
        """Общая отдача."""
        return self.vertical_recoil + self.horizontal_recoil


class BuildCalculator:
    """Калькулятор характеристик сборок."""
    
    def __init__(self, weapon_data: Dict, modules_data: List[Dict]):
        """
        Args:
            weapon_data: Данные базового оружия из API
            modules_data: Список установленных модулей из API
        """
        self.weapon = weapon_data
        self.modules = modules_data
    
    def calculate_stats(self) -> BuildStats:
        """Рассчитать все характеристики сборки."""
        # Базовые характеристики оружия
        base_props = self.weapon.get("properties", {})
        
        ergonomics = base_props.get("ergonomics", 0)
        vertical_recoil = base_props.get("recoilVertical", 100)
        horizontal_recoil = base_props.get("recoilHorizontal", 100)
        weight = base_props.get("weight", 0) / 1000  # Конвертируем в кг
        accuracy = 100.0
        fire_rate = base_props.get("fireRate", 0)
        moa = base_props.get("centerOfImpact", 0)
        effective_distance = base_props.get("effectiveDistance", 0)
        
        # Применяем модификаторы от модулей
        for module in self.modules:
            mod_props = module.get("properties", {})
            
            # Эргономика
            ergo_modifier = mod_props.get("ergonomics", 0)
            ergonomics += ergo_modifier
            
            # Отдача
            recoil_modifier = mod_props.get("recoilModifier", 0)
            if recoil_modifier != 0:
                # Процентный модификатор
                vertical_recoil *= (1 + recoil_modifier / 100)
                horizontal_recoil *= (1 + recoil_modifier / 100)
            
            # Вес
            module_weight = mod_props.get("weight", 0) / 1000
            weight += module_weight
            
            # Точность
            accuracy_modifier = mod_props.get("accuracy", 0)
            accuracy += accuracy_modifier
        
        return BuildStats(
            ergonomics=round(ergonomics, 1),
            vertical_recoil=round(vertical_recoil, 0),
            horizontal_recoil=round(horizontal_recoil, 0),
            weight=round(weight, 2),
            accuracy=round(accuracy, 1),
            effective_distance=effective_distance,
            fire_rate=fire_rate,
            moa=round(moa, 2)
        )
    
    def get_tier_rating(self) -> str:
        """Определить tier рейтинг сборки на основе характеристик."""
        stats = self.calculate_stats()
        
        # Логика оценки (можно настроить)
        score = 0
        
        # Эргономика (0-100)
        if stats.ergonomics >= 70:
            score += 3
        elif stats.ergonomics >= 50:
            score += 2
        elif stats.ergonomics >= 30:
            score += 1
        
        # Отдача (чем меньше, тем лучше)
        if stats.recoil_sum <= 60:
            score += 3
        elif stats.recoil_sum <= 100:
            score += 2
        elif stats.recoil_sum <= 150:
            score += 1
        
        # Вес (чем легче, тем лучше для эргономики)
        if stats.weight <= 3.5:
            score += 1
        
        # Определяем tier
        if score >= 6:
            return "S"
        elif score >= 4:
            return "A"
        elif score >= 2:
            return "B"
        elif score >= 1:
            return "C"
        else:
            return "D"
    
    def format_stats_text(self, language: str = "ru") -> str:
        """Отформатировать характеристики для вывода."""
        stats = self.calculate_stats()
        tier = self.get_tier_rating()
        
        if language == "ru":
            text = f"""
📊 **Характеристики сборки** (Tier: {tier})

🎯 **Эргономика:** {stats.ergonomics}
📉 **Вертикальная отдача:** {stats.vertical_recoil}
📉 **Горизонтальная отдача:** {stats.horizontal_recoil}
🔢 **Сумма отдачи:** {stats.recoil_sum}
⚖️ **Вес:** {stats.weight} кг
🎯 **Точность:** {stats.accuracy}%
📏 **MOA:** {stats.moa}
🔫 **Скорострельность:** {stats.fire_rate} в/мин
📍 **Эффективная дистанция:** {stats.effective_distance}м
"""
        else:
            text = f"""
📊 **Build Stats** (Tier: {tier})

🎯 **Ergonomics:** {stats.ergonomics}
📉 **Vertical Recoil:** {stats.vertical_recoil}
📉 **Horizontal Recoil:** {stats.horizontal_recoil}
🔢 **Recoil Sum:** {stats.recoil_sum}
⚖️ **Weight:** {stats.weight} kg
🎯 **Accuracy:** {stats.accuracy}%
📏 **MOA:** {stats.moa}
🔫 **Fire Rate:** {stats.fire_rate} RPM
📍 **Effective Distance:** {stats.effective_distance}m
"""
        return text.strip()


async def calculate_build_from_api(weapon_id: str, module_ids: List[str], tarkov_api) -> Optional[BuildStats]:
    """
    Рассчитать характеристики сборки используя данные из API.
    
    Args:
        weapon_id: ID оружия из tarkov.dev
        module_ids: Список ID модулей
        tarkov_api: Экземпляр TarkovAPI
    
    Returns:
        BuildStats или None если не удалось получить данные
    """
    # Получить данные оружия
    weapon_data = await tarkov_api.get_item_by_id(weapon_id)
    if not weapon_data:
        return None
    
    # Получить данные модулей
    modules_data = []
    for module_id in module_ids:
        module = await tarkov_api.get_item_by_id(module_id)
        if module:
            modules_data.append(module)
    
    # Рассчитать характеристики
    calculator = BuildCalculator(weapon_data, modules_data)
    return calculator.calculate_stats()
