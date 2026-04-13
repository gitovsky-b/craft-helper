from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Recipe:
    id: int
    name: str
    output_amount: int
    ingredients: Dict[str, int] = field(default_factory=dict)

    def format_ingredients(self) -> str:
        return "\n".join(f"• {k.capitalize()}: {v}" for k, v in self.ingredients.items())