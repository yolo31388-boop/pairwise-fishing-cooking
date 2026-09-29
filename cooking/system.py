"""钓鱼与烹饪系统"""
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
    prerequisites: list = field(default_factory=list)

# 鱼饵权重：越好的饵加成越显著
BAIT_WEIGHTS = {
    "none": 0.0,
    "basic_bait": 0.10,
    "good_bait": 0.20,
    "premium_bait": 0.35,
}

# 时间段权重：清晨/黄昏是鱼类活跃期
TIME_WEIGHTS = {
    "dawn": 0.15,
    "day": 0.05,
    "dusk": 0.15,
    "night": 0.10,
}

# 稀有度基础权重：传说鱼概率极低
RARITY_WEIGHTS = {
    "common": 70,
    "rare": 22,
    "epic": 7,
    "legendary": 1,
}

# 传说鱼出现需要的天气/时间条件（满足时权重提升，否则维持极低概率）
LEGENDARY_CONDITIONS = {
    "weather": {"storm", "rain"},
    "time": {"dawn", "night"},
}

# 食材品质对食物效果的倍率
QUALITY_MULTIPLIERS = {
    "common": 1.0,
    "uncommon": 1.2,
    "rare": 1.5,
    "epic": 2.0,
    "legendary": 3.0,
    "perfect": 4.0,
}

# 完美食材出极品料理的概率
PERFECT_DISH_CHANCE = 0.3
PERFECT_DISH_BONUS = 1.5

# 每只附近怪物增加的钓鱼被打断概率
INTERRUPTION_PER_MOB = 0.1
MAX_INTERRUPTION = 0.95

# 烹饪失败时普通食材的保留比例
FAILURE_KEEP_RATIO = 0.5


class CookingSystem:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.fish_spots: dict[str, list] = {}  # spot -> fish list
        self.recipes: dict[str, Recipe] = {}
        self.unlocked_recipes: set = set()  # 已完成前置、解锁过的配方

    def get_fish_at_spot(self, spot: str) -> list:
        # 每个钓鱼点有专属鱼群表，不同水域出不同鱼
        return list(self.fish_spots.get(spot, []))

    def get_fish_success(self, rod_level: int, bait: str, time: str) -> float:
        # 成功率 = 鱼竿权重 + 鱼饵权重 + 时间段权重
        rod_weight = min(1.0, rod_level / 100) * 0.5
        bait_weight = BAIT_WEIGHTS.get(bait, 0.0)
        time_weight = TIME_WEIGHTS.get(time, 0.0)
        return max(0.0, min(1.0, rod_weight + bait_weight + time_weight))

    def get_fish_rarity_weights(self, weather: str = None, time: str = None) -> dict:
        # 稀有度按权重分布，传说鱼概率极低且受天气/时间条件影响
        weights = dict(RARITY_WEIGHTS)
        if weather in LEGENDARY_CONDITIONS["weather"] and time in LEGENDARY_CONDITIONS["time"]:
            weights["legendary"] = weights["legendary"] * 5
        return weights

    def can_cook(self, recipe_id: str, skill: int) -> bool:
        # 配方按技能等级和前置配方逐步解锁
        recipe = self.recipes.get(recipe_id)
        if recipe is None:
            return False
        if skill < recipe.skill_required:
            return False
        return all(pre in self.unlocked_recipes for pre in recipe.prerequisites)

    def get_buff_quality(self, ingredients_quality: dict) -> dict:
        # 食物效果按食材品质浮动，完美食材有概率出极品料理
        if not ingredients_quality:
            return {"atk": 10}
        multipliers = [QUALITY_MULTIPLIERS.get(q, 1.0) for q in ingredients_quality.values()]
        avg = sum(multipliers) / len(multipliers)
        atk = 10 * avg
        buff = {"atk": round(atk)}
        if any(q == "perfect" for q in ingredients_quality.values()):
            if self.rng.random() < PERFECT_DISH_CHANCE:
                buff["atk"] = round(atk * PERFECT_DISH_BONUS)
                buff["perfect_dish"] = True
        return buff

    def get_fishing_interruption(self, nearby_mobs: int) -> float:
        # 附近怪物增加钓鱼失败/被打断概率
        return min(MAX_INTERRUPTION, max(0, nearby_mobs) * INTERRUPTION_PER_MOB)

    def process_cooking_failure(self, ingredients: dict, rare_ingredients: list) -> dict:
        # 失败保留部分普通食材，稀有食材有保底全数返还
        kept = {}
        for name, count in ingredients.items():
            if name in rare_ingredients:
                kept[name] = count  # 稀有食材保底
            else:
                kept_count = int(count * FAILURE_KEEP_RATIO)
                if kept_count > 0:
                    kept[name] = kept_count
        for name in rare_ingredients:
            kept.setdefault(name, ingredients.get(name, 1))
        return kept
