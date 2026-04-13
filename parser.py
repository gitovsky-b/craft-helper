import re
from models import Recipe

def parse_recipe_line(line: str) -> Recipe | None:
    match = re.match(r'^(.*?)\s*\((\d+)\)\s*-\s*(.*)$', line)
    if not match:
        return None
    name = match.group(1).strip()
    output = int(match.group(2))
    ingredients_part = match.group(3)

    ingredients = {}
    for ing_str in ingredients_part.split(','):
        ing_str = ing_str.strip().rstrip('.')
        parts = ing_str.rsplit(' ', 1)
        if len(parts) == 2 and parts[1].isdigit():
            ing_name = parts[0].strip().lower()
            ing_count = int(parts[1])
            ingredients[ing_name] = ing_count
    return Recipe(id=0, name=name, output_amount=output, ingredients=ingredients)