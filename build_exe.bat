@echo off
echo ========================================
echo    Сборка CraftHelper (десктоп)
echo ========================================

if exist venv\Scripts\activate (
    call venv\Scripts\activate
)

pip install pyinstaller

rmdir /s /q build dist 2>nul
del /q *.spec 2>nul

if not exist craft_app.spec (
    echo Файл craft_app.spec не найден!
    exit /b 1
)

echo Сборка приложения...
pyinstaller craft_app.spec

if %errorlevel%==0 (
    echo Готово! Файл: dist\CraftHelper.exe
) else (
    echo Ошибка сборки
)
pause