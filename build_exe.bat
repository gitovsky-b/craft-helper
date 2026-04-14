@echo off
echo ========================================
echo    Сборка CraftHelper (десктоп)
echo ========================================

if exist venv\Scripts\activate (
    call venv\Scripts\activate
)

pip install pyinstaller

echo Сборка приложения...
pyinstaller CraftHelper.spec

if %errorlevel%==0 (
    echo Готово! Файл: dist\CraftHelper.exe
) else (
    echo Ошибка сборки
)
pause