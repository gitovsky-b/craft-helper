#!/bin/bash
echo "=== Сборка CraftHelper ==="

pyinstaller --onefile --console --name CraftHelper \
    --add-data "assets/recipes.txt:assets" \
    --add-data "assets/easy_ingredients.txt:assets" \
    --collect-all customtkinter \
    --collect-all PIL \
    --hidden-import models \
    --hidden-import calculator \
    --hidden-import dialogs \
    main.py

echo "Готово: dist/CraftHelper"