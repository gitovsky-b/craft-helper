import sqlite3
import json
from pathlib import Path
from typing import List, Optional
from models import Recipe

def get_db_path():
    home = Path.home()
    db_dir = home / ".craft_helper"
    db_dir.mkdir(exist_ok=True)
    return str(db_dir / "craft.db")

DB_NAME = get_db_path()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS recipes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE,
                  output_amount INTEGER,
                  ingredients_json TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS easy_ingredients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE)''')
    conn.commit()
    conn.close()

def get_all_recipes() -> List[Recipe]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, output_amount, ingredients_json FROM recipes ORDER BY name")
    rows = c.fetchall()
    recipes = []
    for row in rows:
        ingredients = json.loads(row[3])
        recipes.append(Recipe(id=row[0], name=row[1], output_amount=row[2], ingredients=ingredients))
    conn.close()
    return recipes

def get_recipe_by_id(recipe_id: int) -> Optional[Recipe]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, output_amount, ingredients_json FROM recipes WHERE id=?", (recipe_id,))
    row = c.fetchone()
    conn.close()
    if row:
        ingredients = json.loads(row[3])
        return Recipe(id=row[0], name=row[1], output_amount=row[2], ingredients=ingredients)
    return None

def add_recipe(recipe: Recipe):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO recipes (name, output_amount, ingredients_json) VALUES (?, ?, ?)",
              (recipe.name, recipe.output_amount, json.dumps(recipe.ingredients, ensure_ascii=False)))
    conn.commit()
    conn.close()

def update_recipe(recipe: Recipe):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE recipes SET name=?, output_amount=?, ingredients_json=? WHERE id=?",
              (recipe.name, recipe.output_amount, json.dumps(recipe.ingredients, ensure_ascii=False), recipe.id))
    conn.commit()
    conn.close()

def delete_recipe(recipe_id: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
    conn.commit()
    conn.close()

def get_easy_ingredients() -> List[str]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name FROM easy_ingredients ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def add_easy_ingredient(name: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO easy_ingredients (name) VALUES (?)", (name.lower(),))
    conn.commit()
    conn.close()

def delete_easy_ingredient(name: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM easy_ingredients WHERE name=?", (name.lower(),))
    conn.commit()
    conn.close()