"""钓鱼与烹饪系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cooking.system import CookingSystem, Fish, Recipe

class TestFishSpotDistribution:
    def test_different_spots_have_different_fish(self):
        cs = CookingSystem()
        cs.fish_spots = {"river": [Fish("f1", "carp", "common", 1.0)], "ocean": [Fish("f2", "tuna", "rare", 5.0)]}
        river_fish = cs.get_fish_at_spot("river")
        ocean_fish = cs.get_fish_at_spot("ocean")
        assert river_fish != ocean_fish  # bug1: 一样

class TestBaitEffect:
    def test_better_bait_improves_success(self):
        cs = CookingSystem()
        r1 = cs.get_fish_success(50, "none", "day")
        r2 = cs.get_fish_success(50, "premium_bait", "day")
        assert r2 > r1  # bug2: 一样

class TestRarityWeights:
    def test_legendary_fish_rare(self):
        cs = CookingSystem()
        weights = cs.get_fish_rarity_weights()
        assert weights["legendary"] < weights["common"]  # bug3: 一样

class TestRecipeUnlock:
    def test_recipe_requires_skill(self):
        cs = CookingSystem()
        cs.recipes["r1"] = Recipe("r1", "sushi", skill_required=50)
        assert cs.can_cook("r1", 10) == False  # bug4: True
        assert cs.can_cook("r1", 60) == True

class TestBuffQuality:
    def test_better_ingredients_give_better_buff(self):
        cs = CookingSystem()
        b1 = cs.get_buff_quality({"fish": "common"})
        b2 = cs.get_buff_quality({"fish": "legendary"})
        assert b2["atk"] > b1["atk"]  # bug5: 都是10

class TestFishingInterruption:
    def test_mobs_increase_interruption(self):
        cs = CookingSystem()
        c0 = cs.get_fishing_interruption(0)
        c5 = cs.get_fishing_interruption(5)
        assert c5 > c0  # bug6: 都是0

class TestCookingFailureRefund:
    def test_failure_preserves_rare_ingredients(self):
        cs = CookingSystem()
        result = cs.process_cooking_failure({"fish": 1}, ["golden_fish"])
        assert "golden_fish" in result  # bug7: 空
