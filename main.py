import sys
import os
import sqlite3
import json
import re
from pathlib import Path

# ---------- Утилиты для ресурсов ----------
def resource_path(relative_path):
    """Возвращает абсолютный путь к ресурсу (работает в dev и в PyInstaller)."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

# ---------- Работа с БД ----------
def get_db_path():
    home = Path.home()
    db_dir = home / ".craft_helper"
    db_dir.mkdir(exist_ok=True)
    return str(db_dir / "craft.db")

DB_NAME = get_db_path()

def parse_recipe_line(line: str):
    """Парсит строку рецепта вида 'Доска (4) - дерево 2'."""
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
    return name, output, ingredients

def init_tables():
    """Создаёт таблицы в БД, если их ещё нет."""
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

def import_from_resources():
    """Импортирует рецепты и ингредиенты из вшитых файлов."""
    recipes_path = resource_path(os.path.join("assets", "recipes.txt"))
    easy_path = resource_path(os.path.join("assets", "easy_ingredients.txt"))

    print("📁 Импорт начальных данных...")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    recipes_cnt = 0
    if os.path.exists(recipes_path):
        with open(recipes_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parsed = parse_recipe_line(line)
                if parsed:
                    name, output, ing = parsed
                    try:
                        c.execute(
                            "INSERT OR IGNORE INTO recipes (name, output_amount, ingredients_json) VALUES (?, ?, ?)",
                            (name, output, json.dumps(ing, ensure_ascii=False))
                        )
                        if c.rowcount > 0:
                            recipes_cnt += 1
                    except Exception as e:
                        print(f"Ошибка импорта рецепта '{name}': {e}")

    easy_cnt = 0
    if os.path.exists(easy_path):
        with open(easy_path, 'r', encoding='utf-8') as f:
            for line in f:
                name = line.strip().lower()
                if name and not name.startswith('#'):
                    try:
                        c.execute("INSERT OR IGNORE INTO easy_ingredients (name) VALUES (?)", (name,))
                        if c.rowcount > 0:
                            easy_cnt += 1
                    except Exception as e:
                        print(f"Ошибка импорта ингредиента '{name}': {e}")

    conn.commit()
    conn.close()
    print(f"✅ Импортировано рецептов: {recipes_cnt}, ингредиентов: {easy_cnt}")

def ensure_database_ready():
    """Проверяет готовность БД, при необходимости инициализирует и наполняет."""
    init_tables()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM recipes")
    count = c.fetchone()[0]
    conn.close()

    if count == 0:
        print("📭 База пуста — автоматический импорт...")
        import_from_resources()
    else:
        print(f"✅ База данных готова (рецептов: {count})")

# ---------- Точка входа ----------
if __name__ == "__main__":
    ensure_database_ready()
    from gui import CraftApp
    app = CraftApp()
    app.mainloop()