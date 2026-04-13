#!/usr/bin/env python3
import sys
import sqlite3
from pathlib import Path
from gui import CraftApp

def check_database():
    """Проверяет, есть ли рецепты в базе."""
    db_path = Path.home() / ".craft_helper" / "craft.db"
    if not db_path.exists():
        print("❌ База данных не найдена!")
        print(f"   Запустите сначала: python3 init_db.py")
        return False
    
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM recipes")
    count = c.fetchone()[0]
    conn.close()
    
    if count == 0:
        print("⚠️  База данных пуста!")
        print(f"   Запустите: python3 init_db.py")
        return False
    
    return True

if __name__ == "__main__":
    if not check_database():
        sys.exit(1)
    
    app = CraftApp()
    app.mainloop()