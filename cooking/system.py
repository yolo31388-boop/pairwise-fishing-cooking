"""钓鱼与烹饪系统 - 含7个bug"""
import random
from dataclasses import dataclass, field

@dataclass
class Fish:
    fid: str
    name: str
    rarity: str
    size: float

@dataclass
class Recipe:
    rid: str
    name: str
    skill_required: int = 1
    ingredients: dict = field(default_factory=dict)
    buff: dict = field(default_factory=dict)

class CookingSystem:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.fish_spots: dict[str, list] = {}  # spot -> fish list
        self.recipes: dict[str, Recipe] = {}

    def get_fish_at_spot(self, spot: str) -> list:
        # bug1: 所有点出所有鱼
        all_fish = []
        for fishes in self.fish_spots.values():
            all_fish.extend(fishes)
        return all_fish

    def get_fish_success(self, rod_level: int, bait: str, time: str) -> float:
        # bug2: 只看鱼竿
        return min(1.0, rod_level / 100)

    def get_fish_rarity_weights(self) -> dict:
        # bug3: 均匀分布
        return {"common": 1, "rare": 1, "epic": 1, "legendary": 1}

    def can_cook(self, recipe_id: str, skill: int) -> bool:
        # bug4: 无解锁条件
        return recipe_id in self.recipes

    def get_buff_quality(self, ingredients_quality: dict) -> dict:
        # bug5: 固定效果
        return {"atk": 10}

    def get_fishing_interruption(self, nearby_mobs: int) -> float:
        # bug6: 无干扰
        return 0.0

    def process_cooking_failure(self, ingredients: dict, rare_ingredients: list) -> dict:
        # bug7: 材料全消失
        return {}
