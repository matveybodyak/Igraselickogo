@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo  Сборка лаунчера Survival 2D в .exe
echo ============================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден.
    echo Установите Python с python.org и добавьте в PATH.
    pause
    exit /b 1
)

REM Проверка PyInstaller
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller не найден, устанавливаю...
    python -m pip install --upgrade pyinstaller
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить PyInstaller.
        pause
        exit /b 1
    )
)

REM Сборка
echo.
echo Сборка .exe (это займёт ~30-60 секунд)...
echo.
python -m PyInstaller --onefile --noconsole ^
    --name "Survival2D" ^
    --add-data "assets;assets" ^
    launcher.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Сборка не удалась.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Готово! Файл: dist\Survival2D.exe
echo ============================================
echo.
echo Скопируйте dist\Survival2D.exe в корень папки игры
echo (туда, где лежит main.py), затем запускайте двойным кликом.
echo.

REM Открыть папку dist
if exist "dist" start "" "dist"
pause