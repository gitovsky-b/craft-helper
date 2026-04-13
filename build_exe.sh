#!/bin/bash
echo "=== Сборка CraftHelper ==="

# Очистка старых сборок
rm -rf build dist *.spec

# Сборка с явным указанием всех скрытых импортов
pyinstaller --onefile --console --name CraftHelper \
    --add-data "assets/recipes.txt:assets" \
    --add-data "assets/easy_ingredients.txt:assets" \
    --collect-all customtkinter \
    --collect-all PIL \
    --hidden-import models \
    --hidden-import calculator \
    --hidden-import dialogs \
    --hidden-import gui \
    --hidden-import database \
    --hidden-import parser \
    --hidden-import resources \
    main.py

echo "Готово: dist/CraftHelper"