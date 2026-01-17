import numpy as np
from pyit2fls import T1TSK, T1FS, tri_mf, trapezoid_mf, gaussian_mf, IT2FS, TSK, einstein_sum_s_norm, product_t_norm, max_s_norm, IT2FS_plot
import matplotlib.pyplot as plt

# uniwersum - ile sztuk produktu pracownik wykonał
number_of_products_universe = np.linspace(0, 100, 100000)

# ta funkcja przynależenia jest de facto równoważna zbiorowi ostremu,
# tylko zero należy do zbioru rozmytego
zero = IT2FS(number_of_products_universe, tri_mf, [-0.001, 0, 0.001, 1.0], tri_mf, [-0.001, 0, 0.001, 1.0])

# niewielka nadprodukcja - do 10 sztuk ponad normę (oczywiście stopniowo przynależenie do tej zmiennej maleje)
low = IT2FS(number_of_products_universe, trapezoid_mf, [0, 1, 50, 50.1, 1.0], trapezoid_mf, [0, 1, 50, 50.1, 1.0])
# średnia nadprodukcja - od 11 sztuk do 20 ponad normę
medium = IT2FS(number_of_products_universe, trapezoid_mf, [50.1, 51, 60.99, 90, 1.0], trapezoid_mf, [50.1, 51, 55, 70, 1.0])
medium.check_set()
# duża nadprodukcja ponad 20 sztuk ponad normę
high = IT2FS(number_of_products_universe, trapezoid_mf, [59.999, 80, 100, 101, 1.0], trapezoid_mf, [79.99, 90, 100, 101, 1.0])
high.check_set()

zero.plot()
low.plot()
medium.plot()
high.plot()
medium.check_set()
high.check_set()

# kara -20 zł
def fine(x): return -20
# brak premii
def minimal_wage(x): return 0
# tutaj wypłacamy 5 zł za każdą ponadwymiarową sztukę
def little_bonus(x): return 5 * (x - 50) # to jest tożsame z wielomianem 5x - 250
# tutaj wypłacamy 10 zł za każdą ponadwymiarową sztukę
def high_bonus(x): return 10 * (x - 50) # to jest tożsame z wielomianem 10x - 250

# definiujemy sterownik rozmyty TSK
controller = TSK(t_norm=product_t_norm, s_norm=einstein_sum_s_norm)
# jedno wejście, jedno wyjście
controller.add_input_variable('number_of_products')
controller.add_output_variable('payment')

# jeżeli nie wyprodukowano żadnej sztuki, to otrzymujemy karę
controller.add_rule([('number_of_products', zero)],[('payment', {"const": -20, "number_of_products":0})])
# jeżeli produkujemy w normie to nie dostajemy premii
controller.add_rule([('number_of_products', low)],[('payment', {"const": 0, "number_of_products":0})])
# jeżeli produkujemy niewielką nadwyżkę otrzyumjemy niewielką premię
controller.add_rule([('number_of_products', medium)],[('payment', {"const": -250, "number_of_products": 5})])
# jeżeli produkujemy znaczną nadwyżkę otrzymujemy odpowiednio większą premię
controller.add_rule([('number_of_products', high)],[('payment', {"const": -500, "number_of_products": 10})])

values = [0, 1, 5, 10, 20, 49, 50, 51, 52, 53, 54, 55, 60, 62, 65, 66, 67, 68, 69, 70, 72, 75, 77, 79, 80, 82, 85, 90, 100]

for value in values:
    # podajemy ostre wejścia i uzyskujemy wyjście
    it2out = controller.evaluate({'number_of_products': value})
    print(value, 'payment: ', it2out['payment'], it2out['payment'] / (value - 50) if value > 50 else '')  # tutaj możemy pobrać konkretną wartość wyjścia

plt.show()

IT2FS_plot(low, medium, high, legends=["low", "medium", "high"])


# tutaj rysujemy wykres premii w zależności od liczby wyprodukowanych sztuk
x = range(0, 100)
y = [controller.evaluate({'number_of_products': x})['payment'] for x in x]
plt.plot(x, y)
plt.show()


