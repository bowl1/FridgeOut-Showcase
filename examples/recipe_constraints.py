"""Small inventory validator for interviews; no production prompts or diet rules.

Run: python3 -m examples.recipe_constraints
The production app additionally checks schemas, diets, cooking steps and uses
a separate model judge. This example only demonstrates deterministic limits.
"""
from collections import defaultdict
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Food:
    name: str
    quantity: float
    unit: str


@dataclass(frozen=True)
class Recipe:
    name: str
    ingredients: tuple[Food, ...]
    minutes: int


STAPLES = frozenset({'salt', 'black pepper', 'water', 'cooking oil'})


def normalize(value: str) -> str:
    return ' '.join(value.casefold().split())


def quantity_valid(value: float) -> bool:
    return isfinite(value) and value > 0


def validate(recipe: Recipe, inventory: tuple[Food, ...], max_minutes: int) -> list[str]:
    """Aggregate stock and usage by exact normalized food/unit; never convert units."""
    available: dict[tuple[str, str], float] = defaultdict(float)
    for item in inventory:
        if not normalize(item.name) or not normalize(item.unit) or not quantity_valid(item.quantity):
            raise ValueError('Invalid inventory fixture')
        available[(normalize(item.name), normalize(item.unit))] += item.quantity

    failures = []
    if not recipe.ingredients:
        failures.append('No ingredients')
    if recipe.minutes <= 0 or recipe.minutes > max_minutes:
        failures.append('Cooking time outside allowed range')

    used: dict[tuple[str, str], float] = defaultdict(float)
    for item in recipe.ingredients:
        name, unit = normalize(item.name), normalize(item.unit)
        if not name or not unit or not quantity_valid(item.quantity):
            failures.append('Invalid ingredient name, unit or quantity')
            continue
        if name not in STAPLES:
            used[(name, unit)] += item.quantity

    for key, quantity in sorted(used.items()):
        if key not in available:
            failures.append(f'Unavailable food/unit: {key[0]} ({key[1]})')
        elif quantity > available[key] + 1e-6:
            failures.append(f'Cumulative quantity exceeds stock: {key[0]} ({key[1]})')
    return failures


def main() -> None:
    inventory = (Food('mushroom', 150, 'g'),)
    candidates = (
        Recipe('Mushroom sauté', (Food('mushroom', 100, 'g'), Food('cooking oil', 1, 'tsp')), 10),
        Recipe('Overcommitted mushrooms', (Food('mushroom', 100, 'g'), Food('mushroom', 80, 'g')), 10),
        Recipe('Unverified conversion', (Food('mushroom', 1, 'bag'),), 10),
    )
    for recipe in candidates:
        failures = validate(recipe, inventory, max_minutes=15)
        print(f'{recipe.name}: {failures or "passes illustrated constraints (not a semantic judgment)"}')


if __name__ == '__main__':
    main()
