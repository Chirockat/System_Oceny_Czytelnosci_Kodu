import numpy as np
from pyit2fls import T1TSK, T1FS, tri_mf, trapezoid_mf, gaussian_mf, IT2FS, TSK, einstein_sum_s_norm, product_t_norm, IT2FS_plot
import matplotlib.pyplot as plt

# --- 1. DEFINICJA UNIWERSÓW ---

# Uniwersum dla Gęstości (AST Density): zazwyczaj od 0 do 20 węzłów na linię
# Bazując na Twoich wytycznych: do 7 (małe), do 9 (dobre), powyżej 9 (duże)
density_universe = np.linspace(0, 20, 2000)

# Uniwersum dla Złożoności (CC): od 1 do 50 (powyżej 50 to już dramat)
cc_universe = np.linspace(0, 50, 5000)

# --- Zmienna 1: DENSITY (Gęstość kodu - AST Node Density) ---
# Rozciągamy, by system był mniej czuły na drobne różnice.
# Nakładamy na siebie zbiory, np. Density=5 będzie należeć i do Low i do Optimal.

# Niska gęstość (Kod rozwlekły)
# UMF rozciągnięte aż do 8 (wcześniej 6), LMF do 5.
d_low = IT2FS(density_universe,
              trapezoid_mf, [-0.1, 0, 4, 8, 1.0],      # UMF: Szeroka tolerancja
              trapezoid_mf, [-0.1, 0, 2, 5, 1.0])      # LMF: Rdzeń pewności

# Optymalna gęstość (Kod Basic)
# Rozciągamy zakres "dobrego kodu" od 3 aż do 14 (wcześniej 10).
# Dzięki temu kod o gęstości 11 (lekko zbity) nadal łapie się na "Optimal".
d_optimal = IT2FS(density_universe,
                  trapezoid_mf, [3, 6, 10, 14, 1.0],   # UMF: Bardzo szeroki zakres "akceptowalności"
                  trapezoid_mf, [5, 7, 8, 11, 1.0])    # LMF: Ścisły środek (ideał 7-8)

# Wysoka gęstość (Kod Modern/Zbity)
# Zaczynamy łapać "wysokość" już od 10, ale pewność (LMF) dopiero od 14.
d_high = IT2FS(density_universe,
               trapezoid_mf, [10, 14, 20, 20.1, 1.0],  # UMF
               trapezoid_mf, [13, 16, 20, 20.1, 1.0])  # LMF


# --- Zmienna 2: COMPLEXITY (CC) ---
# Tutaj rozciągnięcie jest kluczowe, bo CC rzadko jest idealnie małe.

# Niska złożoność (Dobry kod)
# Rozciągamy UMF do 10! (wcześniej 6).
# Oznacza to, że funkcja z CC=8 ma jeszcze szansę być uznana za "trochę prostą".
c_low = IT2FS(cc_universe,
              trapezoid_mf, [-0.1, 0, 5, 10, 1.0],     # UMF
              trapezoid_mf, [-0.1, 0, 3, 6, 1.0])      # LMF

# Średnia złożoność
# Gigantyczne rozciągnięcie. CC od 5 do 20 może być uznane za średnie.
# To oddaje realia - CC=15 to jeszcze nie tragedia w dużych projektach.
c_medium = IT2FS(cc_universe,
                 trapezoid_mf, [5, 10, 15, 25, 1.0],   # UMF: Bardzo szerokie ramię
                 trapezoid_mf, [8, 12, 14, 18, 1.0])   # LMF: Rdzeń (typowy średniak)

# Wysoka złożoność
# Przesuwamy start "paniki". Dopiero powyżej 15 zaczynamy się martwić (UMF),
# a pewność, że jest źle (LMF), mamy dopiero przy 25.
c_high = IT2FS(cc_universe,
               trapezoid_mf, [15, 25, 50, 50.1, 1.0],  # UMF
               trapezoid_mf, [22, 30, 50, 50.1, 1.0])  # LMF
# Wizualizacja zbiorów (Opcjonalnie)
d_low.plot()
d_optimal.plot()
d_high.plot()

c_low.plot()
c_medium.plot()
c_high.plot()


# --- 3. FUNKCJE WYJŚCIA (TSK Consequents) ---
# Wyjście to ocena 0-100. Funkcja liniowa: y = const + a*density + b*complexity

# Ocena IDEALNA (Startujemy od 100, odejmujemy punkty za wzrost CC)
def perfect_score(inputs):
    # inputs['complexity'] to konkretna liczba (np. 3)
    # 100 - 2 * CC. Dla CC=1 wynik 98.
    return 100 - 2 * inputs['complexity']

# Ocena DOBRA (Startujemy od 80)
# Używana gdy kod jest trochę za gęsty lub trochę za rzadki
def good_score(inputs):
    return 80 - 2 * inputs['complexity']

# Ocena ŚREDNIA (Startujemy od 60)
# Dla kodu "Messy" (małe density) lub "Modern" (duże density)
def medium_score(inputs):
    return 60 - 1.5 * inputs['complexity']

# Ocena SŁABA (Startujemy od 40)
def bad_score(inputs):
    return 40 - inputs['complexity']

# Ocena KRYTYCZNA (Startujemy od 20)
def critical_score(inputs):
    return 20 # Stała niska ocena


# --- 4. STEROWNIK I REGUŁY ---

controller = TSK(t_norm=product_t_norm, s_norm=einstein_sum_s_norm)

controller.add_input_variable('density')
controller.add_input_variable('complexity')
controller.add_output_variable('quality')

# Reguły wnioskowania - Serce systemu
# Słownik w funkcji wyjścia: {'const': C, 'density': a, 'complexity': b} -> y = C + a*d + b*c

# 1. ZŁOTY ŚRODEK (Twój kod "Basic"): Optymalna gęstość + Niskie CC -> PERFECT
controller.add_rule(
    [('density', d_optimal), ('complexity', c_low)],
    [('quality', {'const': 100, 'density': 0, 'complexity': -2})]
)

# 2. KOD MESSY (Twój kod "Messy"): Niska gęstość (rozcieńczony) + Niskie/Średnie CC
# Ocena niższa, bo dużo czytania bez sensu
controller.add_rule(
    [('density', d_low), ('complexity', c_low)],
    [('quality', {'const': 75, 'density': 0, 'complexity': -2})]
)

# 3. KOD MODERN (Twój kod "Modern"): Wysoka gęstość + Niskie CC
# Trudny kognitywnie, mimo że logicznie prosty.
controller.add_rule(
    [('density', d_high), ('complexity', c_low)],
    [('quality', {'const': 70, 'density': -1, 'complexity': -2})]
)

# 4. OSTRZEŻENIE: Średnie CC, ale Density OK
controller.add_rule(
    [('density', d_optimal), ('complexity', c_medium)],
    [('quality', {'const': 65, 'density': 0, 'complexity': -3})]
)

# 5. SPAGHETTI: Niska gęstość (dużo linii) + Wysokie CC (dużo ifów) -> BAD
controller.add_rule(
    [('density', d_low), ('complexity', c_high)],
    [('quality', {'const': 30, 'density': 0, 'complexity': -1})]
)

# 6. KATASTROFA: Wysokie CC i Wysoka Gęstość (Code Golf + Logic Hell) -> CRITICAL
controller.add_rule(
    [('density', d_high), ('complexity', c_high)],
    [('quality', {'const': 10, 'density': 0, 'complexity': 0})]
)


# --- 5. SYMULACJA NA PRZYKŁADACH ---

print("-" * 50)
print(f"{'TYP KODU':<15} | {'Dens.':<5} | {'CC':<5} | {'OCENA (0-100)':<15}")
print("-" * 50)



# Scenariusz 1: "Knapsack Basic" (Ten zrównoważony)
# Density ok. 5-6, CC małe (np. 3)
case_basic = {'density': 6, 'complexity': 7.5}
res_basic = controller.evaluate(case_basic)
print(f"{'BASIC (Ideal)':<15} | {case_basic['density']:<5} | {case_basic['complexity']:<5} | {res_basic['quality']:.2f}")

# Scenariusz 2: "Knapsack Modern" (Zbyt gęsty)
# Density bardzo duże (np. 14), CC bardzo małe (np. 2)
case_modern = {'density': 14.0, 'complexity': 7}
res_modern = controller.evaluate(case_modern)
print(f"{'MODERN (Dense)':<15} | {case_modern['density']:<5} | {case_modern['complexity']:<5} | {res_modern['quality']:.2f}")

# Scenariusz 3: "Knapsack Messy" (Rozwlekły + Ifologia)

case_messy = {'density': 6, 'complexity': 12}
res_messy = controller.evaluate(case_messy)
print(f"{'MESSY (Spag.)':<15} | {case_messy['density']:<5} | {case_messy['complexity']:<5} | {res_messy['quality']:.2f}")

# Scenariusz 4: "God Class" (Najgorszy przypadek)
# Wszystko źle
case_bad = {'density': 15.0, 'complexity': 25.0}
res_bad = controller.evaluate(case_bad)
print(f"{'BAD CODE':<15} | {case_bad['density']:<5} | {case_bad['complexity']:<5} | {res_bad['quality']:.2f}")

print("-" * 50)

# --- 6. WYKRES POWIERZCHNI STEROWANIA (3D) ---
# Pokaże nam, jak zmienia się ocena w zależności od obu parametrów

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

x = np.linspace(0, 20, 50)  # Density
y = np.linspace(0, 20, 50)  # Complexity
X, Y = np.meshgrid(x, y)
Z = np.zeros_like(X)

for i in range(len(x)):
    for j in range(len(y)):
        res = controller.evaluate({'density': X[i, j], 'complexity': Y[i, j]})
        Z[i, j] = res['quality']

surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.8)
ax.set_xlabel('AST Density (Gęstość)')
ax.set_ylabel('Complexity (CC)')
ax.set_zlabel('Ocena Jakości')
ax.set_title('Ocena kodu: Zależność od Gęstości i CC')
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()

# Wykres zbiorów wejściowych dla sprawdzenia
IT2FS_plot(d_low, d_optimal, d_high, legends=["Low Dens", "Optimal Dens", "High Dens"], filename=None)