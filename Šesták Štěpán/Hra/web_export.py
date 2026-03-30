# web_export.py
# Tento soubor generuje Zebricek.html ze šablony a aktuálních dat ze žebříčku.
# Volá se automaticky po každém uložení skóre.
# Šablona: web/Zebricek_template.html (tu neměním)
# Výstup:  web/Zebricek.html (přepisuje se při každém volání)

import os
import json
from ui import load_leaderboard

# Cesty ke složkám
_HERE    = os.path.dirname(os.path.abspath(__file__))
_WEB     = os.path.join(_HERE, "..", "web")
TEMPLATE = os.path.join(_WEB, "Zebricek_template.html")
OUTPUT   = os.path.join(_WEB, "Zebricek.html")


def _format_time(seconds):
    # Převede sekundy na formát M:SS (např. 125 -> "2:05")
    if not seconds:
        return "–"
    return f"{seconds // 60}:{seconds % 60:02d}"


def _build_table_html(board):
    # Sestaví HTML tabulku ze seznamu záznamů
    if not board:
        return """
        <div class="table-wrap">
            <div class="empty-state">
                <span>🎮</span>
                Žebříček je zatím prázdný.<br>Zahraj si a buď první!
            </div>
        </div>"""

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    rows   = ""
    for i, entry in enumerate(board, 1):
        medal    = medals.get(i, str(i))
        rc       = f' class="rank-{i}"' if i <= 3 else ''
        name     = str(entry.get("name", "–")).replace("&", "&amp;").replace("<", "&lt;")
        score    = entry.get("score", 0)
        diff     = entry.get("difficulty", "Normal")
        cas      = _format_time(entry.get("time", 0))

        rows += f"""
            <tr>
                <td{rc}>{medal}</td>
                <td>{name}</td>
                <td class="score-cell">{score}</td>
                <td>{cas}</td>
                <td><span class="badge badge-{diff}">{diff}</span></td>
            </tr>"""

    return f"""
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Hráč</th>
                        <th>Skóre</th>
                        <th>Čas</th>
                        <th>Obtížnost</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>"""


def export_leaderboard_html():
    # Načte šablonu, vloží do ní data a uloží jako Zebricek.html
    board = load_leaderboard()

    with open(TEMPLATE, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("%%TABLE_PLACEHOLDER%%", _build_table_html(board))
    html = html.replace("%%JSON_DATA%%", json.dumps(board, ensure_ascii=False))

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
