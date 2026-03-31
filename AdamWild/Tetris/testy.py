# ============================================================
# TESTY PRO TETRIS
# Spuštění: python testy.py
# Testují herní logiku bez spuštění pygame okna
# ============================================================

# Importujeme funkce a konstanty přímo z tetris.py
import sys
sys.argv = ["tetris.py", "test"]  

from tetris import clear_rows, get_max_score, BLACK, ROWS, COLS


def test_clear_rows():
    """Test funkce clear_rows - ověří že plné řádky se smažou a mřížka zůstane správně velká."""

    # Vytvoříme prázdnou mřížku (stejně jako na začátku hry)
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

    # Poslední dva řádky vyplníme nějakou barvou (simulujeme plné řádky)
    NECO = (255, 0, 0)  # Červená - cokoliv jiného než BLACK
    grid[18] = [NECO for _ in range(COLS)]  # Předposlední řádek - plný
    grid[19] = [NECO for _ in range(COLS)]  # Poslední řádek - plný

    pocet = clear_rows(grid)  # Zavoláme testovanou funkci

    # Ověříme že funkce vrátila správný počet smazaných řádků
    assert pocet == 2, f"CHYBA: Očekávány 2 smazané řádky, dostali jsme {pocet}"
    # Ověříme že řádky jsou nyní prázdné (černé)
    assert grid[18] == [BLACK] * COLS, "CHYBA: Řádek 18 není prázdný po smazání"
    assert grid[19] == [BLACK] * COLS, "CHYBA: Řádek 19 není prázdný po smazání"
    # Ověříme že mřížka má stále správný počet řádků (insert přidal nové nahoře)
    assert len(grid) == ROWS, f"CHYBA: Mřížka má {len(grid)} řádků místo {ROWS}"

    print("✓ TEST 1 PROBĚHL V POŘÁDKU - clear_rows správně smaže 2 plné řádky")


def test_get_max_score():
    """Test funkce get_max_score - ověří správné maximum a ignorování speciálních klíčů."""

    # Simulujeme slovník highscores jako v souboru JSON
    scores = {
        "Honza": 500,
        "Pepa": 1200,
        "Marek": 800,
        "__last_score__": 9999,  # Tento klíč se NESMÍ počítat jako hráčovo skóre
    }

    maximum = get_max_score(scores)

    # Ověříme že maximum je 1200 (Pepa) a ne 9999 (__last_score__)
    assert maximum == 1200, f"CHYBA: Očekáváno maximum 1200, dostali jsme {maximum}"
    assert maximum != 9999, "CHYBA: get_max_score zahrnul speciální klíč __last_score__"

    # Test s prázdným slovníkem - nesmí spadnout, musí vrátit 0
    prazdny = get_max_score({})
    assert prazdny == 0, f"CHYBA: Pro prázdný slovník očekáváno 0, dostali jsme {prazdny}"

    print("✓ TEST 2 PROBĚHL V POŘÁDKU - get_max_score vrátí správné maximum a ignoruje __last_score__")


def spust_testy():
    """Spustí všechny testy a vypíše výsledky do terminálu."""
    print("=" * 55)
    print("   SPOUŠTÍM TESTY...")
    print("=" * 55)

    chyba = False

    try:
        test_clear_rows()
    except AssertionError as e:
        print(f"✗ TEST 1 SELHAL: {e}")
        chyba = True

    try:
        test_get_max_score()
    except AssertionError as e:
        print(f"✗ TEST 2 SELHAL: {e}")
        chyba = True

    print("=" * 55)
    if not chyba:
        print("   VŠECHNY TESTY PROŠLY!")
    else:
        print("   NĚKTERÉ TESTY SELHALY!")
    print("=" * 55)


if __name__ == "__main__":
    spust_testy()