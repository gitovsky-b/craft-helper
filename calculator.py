from typing import Dict, Set
from models import Recipe

def expand_recipe(
    recipe: Recipe,
    required_servings: int,
    all_recipes: Dict[str, Recipe],
    visited: Set[str] = None
) -> Dict[str, int]:
    if visited is None:
        visited = set()
    result = {}
    if recipe.name.lower() in visited:
        raise ValueError(f"Циклическая зависимость: {recipe.name}")
    visited.add(recipe.name.lower())

    crafts = (required_servings + recipe.output_amount - 1) // recipe.output_amount

    for ing_name, amount_per_craft in recipe.ingredients.items():
        total_needed = amount_per_craft * crafts
        if ing_name.lower() in all_recipes:
            sub_recipe = all_recipes[ing_name.lower()]
            sub_map = expand_recipe(sub_recipe, total_needed, all_recipes, visited.copy())
            for k, v in sub_map.items():
                result[k] = result.get(k, 0) + v
        else:
            result[ing_name] = result.get(ing_name, 0) + total_needed

    visited.remove(recipe.name.lower())
    return result

def max_crafts_by_ingredient(recipe: Recipe, ingredient: str, available: int) -> int:
    need = recipe.ingredients.get(ingredient.lower())
    if not need:
        return 0
    return available // need