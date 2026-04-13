#!/usr/bin/env python3
"""
Скрипт для первичного наполнения базы данных рецептами и ингредиентами.
"""
import sqlite3
import json
import os
from pathlib import Path
import re

# === Конфигурация ===
DB_NAME = str(Path.home() / ".craft_helper" / "craft.db")
RECIPES_FILE = "assets/recipes.txt"
EASY_INGREDIENTS_FILE = "assets/easy_ingredients.txt"

def parse_recipe_line(line: str):
    """Парсит строку вида 'Доска (4) - дерево 2'."""
    match = re.match(r'^(.*?)\s*\((\d+)\)\s*-\s*(.*)$', line)
    if not match:
        print(f"    ❌ Не совпадает с шаблоном: '{line}'")
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
        else:
            print(f"    ⚠️  Не удалось распарсить ингредиент: '{ing_str}'")
    return name, output, ingredients

def init_database():
    """Создаёт таблицы, если их нет."""
    db_dir = Path.home() / ".craft_helper"
    db_dir.mkdir(exist_ok=True)
    
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

def import_recipes(file_path: str):
    """Импортирует рецепты из текстового файла."""
    print(f"\n📄 Чтение файла: {file_path}")
    print(f"   Абсолютный путь: {os.path.abspath(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return 0
    
    print(f"✅ Файл найден, размер: {os.path.getsize(file_path)} байт")
    
    # Покажем первые несколько строк файла
    print("\n📝 Первые 5 строк файла:")
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            print(f"   {i+1}: {repr(line.strip())}")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    count = 0
    line_num = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_num += 1
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parsed = parse_recipe_line(line)
            if parsed:
                name, output, ingredients = parsed
                try:
                    c.execute(
                        "INSERT OR IGNORE INTO recipes (name, output_amount, ingredients_json) VALUES (?, ?, ?)",
                        (name, output, json.dumps(ingredients, ensure_ascii=False))
                    )
                    if c.rowcount > 0:
                        count += 1
                        print(f"   ✅ Строка {line_num}: {name} ({output})")
                    else:
                        print(f"   ⚠️  Строка {line_num}: {name} уже существует")
                except Exception as e:
                    print(f"   ❌ Строка {line_num}: ошибка SQL - {e}")
            else:
                print(f"   ❌ Строка {line_num}: не распарсилась")
    
    conn.commit()
    conn.close()
    return count

def import_easy_ingredients(file_path: str):
    """Импортирует легкодоступные ингредиенты."""
    print(f"\n📄 Чтение файла: {file_path}")
    print(f"   Абсолютный путь: {os.path.abspath(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return 0
    
    print(f"✅ Файл найден, размер: {os.path.getsize(file_path)} байт")
    
    # Покажем содержимое файла
    print("\n📝 Содержимое файла:")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"   {repr(content[:200])}...")  # Первые 200 символов
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    count = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            name = line.strip().lower()
            if name and not name.startswith('#'):
                try:
                    c.execute("INSERT OR IGNORE INTO easy_ingredients (name) VALUES (?)", (name,))
                    if c.rowcount > 0:
                        count += 1
                        print(f"   ✅ {name}")
                    else:
                        print(f"   ⚠️  {name} уже существует")
                except Exception as e:
                    print(f"   ❌ Ошибка для '{name}': {e}")
    
    conn.commit()
    conn.close()
    return count

def main():
    print("=" * 50)
    print("Инициализация базы данных CraftHelper")
    print("=" * 50)
    
    # Создаём таблицы
    print("\n📁 Создание таблиц...")
    init_database()
    print(f"  База данных: {DB_NAME}")
    
    # Импорт рецептов
    recipes_count = import_recipes(RECIPES_FILE)
    print(f"\n📊 Импортировано рецептов: {recipes_count}")
    
    # Импорт ингредиентов
    easy_count = import_easy_ingredients(EASY_INGREDIENTS_FILE)
    print(f"📊 Импортировано ингредиентов: {easy_count}")
    
    # Проверка результата
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM recipes")
    total_recipes = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM easy_ingredients")
    total_easy = c.fetchone()[0]
    conn.close()
    
    print("\n" + "=" * 50)
    print(f"✅ Инициализация завершена!")
    print(f"   Рецептов в базе: {total_recipes}")
    print(f"   Легкодоступных ингредиентов: {total_easy}")
    print("=" * 50)
    
    # Если рецептов 0, покажем подсказку
    if total_recipes == 0:
        print("\n⚠️  Внимание: рецепты не импортированы!")
        print("   Проверьте формат файла assets/recipes.txt")
        print("   Ожидаемый формат: Доска (4) - дерево 2")

if __name__ == "__main__":
    main()