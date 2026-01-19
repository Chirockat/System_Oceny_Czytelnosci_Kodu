import radon.complexity as cc
import radon.raw as raw
from radon.metrics import h_visit  # <--- Dodany import

# Nazwa pliku do zbadania
filename = 'knapsack_modern.py'

print(f"--- Analiza pliku: {filename} ---")

try:
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Obliczanie Złożoności (CC)
    blocks = cc.cc_visit(code)

    print("\n[1. Złożoność Cyklomatyczna - CC]")
    total_cc = 0
    if blocks:
        for block in blocks:
            print(f"  Funkcja '{block.name}' -> CC: {block.complexity}")
            total_cc += block.complexity
        avg_cc = total_cc / len(blocks)
    else:
        avg_cc = 0
    print(f"-> ŚREDNIE CC: {avg_cc:.2f}")

    # 2. Obliczanie LLOC (Raw)
    raw_metrics = raw.analyze(code)
    print("\n[2. Rozmiar kodu]")
    print(f"-> LLOC (Logiczne linie): {raw_metrics.lloc}")
    print(f"-> SLOC (Źródłowe linie): {raw_metrics.sloc}")

    # 3. Metryki Halsteada (Effort) - NOWE
    # h_visit zwraca obiekt HalsteadReport z polami: volume, difficulty, effort, bugs, time
    halstead_metrics = h_visit(code)

    print("\n[3. Metryki Halsteada]")
    print(f"-> Effort (Wysiłek): {halstead_metrics.total.effort:.2f}")
    print(f"-> Difficulty (Trudność): {halstead_metrics.total.difficulty:.2f}")
    print(f"-> Vocabulary (Gestosc): {halstead_metrics.total.vocabulary:.2f}")
    print(f"-> Volume (objetosc): {halstead_metrics.total.volume:.2f}")
    print(f"\n-> Gestosc xd: {halstead_metrics.total.volume / raw_metrics.lloc:.2f}")



except FileNotFoundError:
    print(f"BŁĄD: Nie znaleziono pliku '{filename}'. Sprawdź nazwę.")
except Exception as e:
    print(f"BŁĄD: {e}")