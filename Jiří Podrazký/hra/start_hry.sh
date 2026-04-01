#!/bin/bash

# SPACE INVADERS - MAC/LINUX BOOT SEQUENCE

# 1. Kontrola existence virtuálního prostředí
if [ ! -d "venv" ]; then
    echo "[INFO] Virtuální prostředí nenalezeno. Vytvářím 'venv'..."
    python3 -m venv venv
fi

# 2. Aktivace prostředí
echo "[INFO] Aktivuji virtuální prostředí..."
source venv/bin/activate

# 3. Instalace / Kontrola knihoven
echo "[INFO] Kontrola instalovaných modulů (pygame, requests)..."
pip install pygame requests --quiet

# 4. Spuštění hlavního menu
echo "[INFO] Startuji operační rozhraní hry..."
python3 menu.py

# 5. Ošetření po skončení hry
echo ""
echo "[INFO] System Space Invaders byl úspěšně ukončen."
read -p "Stiskni Enter pro zavření okna..."
