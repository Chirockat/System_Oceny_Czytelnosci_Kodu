import radon.complexity as cc
import radon.raw as raw

# Nazwa pliku do zbadania
filename = 'merge_sort_bad.py'

print(f"--- Analiza pliku: {filename} ---")

try:
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Obliczanie Złożoności (CC)
    # Radon zwraca listę bloków (funkcji/klas)
    blocks = cc.cc_visit(code)

    print("\n[Złożoność Cyklomatyczna - CC]")
    total_cc = 0
    for block in blocks:
        print(f"Funkcja '{block.name}' -> CC: {block.complexity}")
        total_cc += block.complexity

    # Jeśli są bloki, oblicz średnią, jeśli nie - 0
    avg_cc = total_cc / len(blocks) if blocks else 0
    print(f"ŚREDNIE CC: {avg_cc:.2f}")

    # 2. Obliczanie LLOC (Raw)
    raw_metrics = raw.analyze(code)
    print("\n[Rozmiar kodu]")
    print(f"LLOC (Logiczne linie): {raw_metrics.lloc}")
    print(f"SLOC (Źródłowe linie): {raw_metrics.sloc}")

except FileNotFoundError:
    print(f"BŁĄD: Nie znaleziono pliku '{filename}'. Sprawdź nazwę.")
except Exception as e:
    print(f"BŁĄD: {e}")