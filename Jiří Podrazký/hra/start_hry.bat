@echo off
title Space Invaders - Boot Sequence
color 0b
echo ============================================================
echo        SPACE INVADERS - SYSTEM INITIALIZATION
echo ============================================================
echo.

:: 1. Kontrola existence virtualniho prostredi
if not exist venv (
    echo [INFO] Virtualni prostredi nenalezeno. Vytvarim 'venv'...
    python -m venv venv
)

:: 2. Aktivace prostredi
echo [INFO] Aktivuji virtualni prostredi...
call venv\Scripts\activate

:: 3. Instalace / Kontrola knihoven (pomocí python -m pip pro vyšší spolehlivost)
echo [INFO] Kontrola instalovanych modulu (pygame, requests)...
python -m pip install pygame requests --quiet

:: 4. Spusteni hlavniho menu
echo [INFO] Startuji operacni rozhrani hry...
echo.
python menu.py

:: 5. Osetreni po skonceni hry
echo.
echo [INFO] System Space Invaders byl uspesne ukoncen.
echo Pro zavreni okna stiskni libovolnou klavesu.
pause > nul