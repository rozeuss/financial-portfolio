import numpy as np
from scipy.optimize import minimize
import math


# Obliczenie jednodniowych stóp zwrotu
def step_1(W):
    R = np.array([])
    for t in range(1, len(W)):
        R = np.append(R, ((W[t] - W[t - 1]) / W[t - 1]))
    return R

# Obliczenie oczekiwanej stopy zwrotu
def step_2(R):
    suma = np.sum(R)

    R_dash = suma * (1 / (len(R)))

    return R_dash

# Obliczenie odchylenia standardowego
def step_3(R, R_dash):
    s = None
    suma = 0
    for i in range(len(R)):
        suma = suma + ((R[i] - R_dash) * (R[i] - R_dash))

    s = math.sqrt((1 / len(R) * suma))
    return s

# Obliczenie współczynnika korelacji
def step_4(x1, x2, aR_dash, bR_dash, s1, s2):
    suma = 0

    for i in range(len(x1)):
        suma = suma + ((x1[i] - aR_dash) * (x2[i] - bR_dash))

    p = suma / (len(x1) * s1 * s2)

    #  return np.corrcoef(x, y)[0, 1]
    return p


# Główna funkcja
def calculate(A, B, ratio):


    #  Jednodniowe stopy zwrotu
    Ra = step_1(A)
    Rb = step_1(B)

    #  Oczekiwana stopa zwrotu
    aR_dash = step_2(Ra)
    bR_dash = step_2(Rb)


    #  Odchylenia standardowe stopy zwrotu
    Sa = step_3(Ra, aR_dash)
    Sb = step_3(Rb, bR_dash)

    #
    p = step_4(Ra, Rb, aR_dash, bR_dash, Sa, Sb)

    def objective_k1_min(x, aR_dash, bR_dash):
        x1 = x[0]
        x2 = x[1]
        return (x1 * aR_dash) + (x2 * bR_dash)

    def objective_k1_max(x, aR_dash, bR_dash):
        x1 = x[0]
        x2 = x[1]
        return -((x1 * aR_dash) + (x2 * bR_dash))

    def objective_k2_min(x, Sa, Sb, p):
        x1 = x[0]
        x2 = x[1]
        return ((x1 * x1) * (Sa * Sa)) + ((x2 * x2) * (Sb * Sb)) + 2 * x1 * Sa * x2 * Sb * p

    def objective_k2_max(x, Sa, Sb, p):
        x1 = x[0]
        x2 = x[1]
        return -(((x1 * x1) * (Sa * Sa)) + ((x2 * x2) * (Sb * Sb)) + 2 * x1 * Sa * x2 * Sb * p)

    def objective_f_meta(x, aR_dash, bR_dash, Sa, Sb, p, K1min, K1max, K2min, K2max):

        ratio_x = math.fabs(ratio - 1)

        x1 = x[0]
        x2 = x[1]
        return -(ratio * (1 - (K1max - objective_k1_min(x, aR_dash, bR_dash)) / (K1max - K1min)) + ratio_x * (
            (K2max - objective_k2_min(x, Sa, Sb, p)) / (K2max - K2min)))

    def constraint1(x):
        sum = 1
        for i in range(2):
            sum = sum - x[i]
        return sum

    def constraint2(x):
        return x[0]

    def constraint3(x):
        return x[1]

    def constraint1a(x):
        return x[0] + x[1] - 1

    def constraint1b(x):
        return -x[0] - x[1] + 1

    x0 = np.array([0.0, 0.0]) # Wartości początkowe zmiennych

    con1 = {'type': 'eq', 'fun': constraint1}
    con2 = {'type': 'ineq', 'fun': constraint2}
    con3 = {'type': 'ineq', 'fun': constraint3}
    con1a = {'type': 'ineq', 'fun': constraint1a}
    con1b = {'type': 'ineq', 'fun': constraint1b}

    cons_k1 = [con1]                            # Ograniczenia dla metody SLSQP
    cons_k2 = [con2, con3, con1a, con1b]        # Ograniczenia dla metody COBYLA (brak obsługi ograniczeń równości)
    bnds = ((0.0, 1.0), (0.0, 1.0))             # Przedziały zmiennych dla metody SLSQP

    #  Wyznaczanie K1min i K1max
    args = (aR_dash, bR_dash)
    sol = minimize(objective_k1_min, x0, args=args, method='SLSQP', bounds=bnds, constraints=cons_k1)
    K1min = sol.fun

    sol = minimize(objective_k1_max, x0, args=args, method='SLSQP', bounds=bnds, constraints=cons_k1)
    K1max = -sol.fun

    #  Wyznaczanie K2min i K2max
    args = (Sa, Sb, p)
    sol = minimize(objective_k2_min, x0, args=args, method='COBYLA', constraints=cons_k2)
    K2min = sol.fun

    sol = minimize(objective_k2_max, x0, args=args, method='COBYLA', constraints=cons_k2)
    K2max = -sol.fun


    #  Wyznaczanie funkcji metakryterium i proporcji między spółkami.
    args = (aR_dash, bR_dash, Sa, Sb, p, K1min, K1max, K2min, K2max)
    sol = minimize(objective_f_meta, x0, args=args, method='SLSQP', bounds=bnds, constraints=cons_k1)
    f_metakryt = -sol.fun



    # Printy dla sprawdzenia poprawności - usunąć w gotowej aplikacji :)
    print('K1min: ' + str(K1min))
    print('K1max: ' + str(K1max))
    print('K2min: ' + str(K2min))
    print('K2max: ' + str(K2max))
    print('Metakryt: ' + str(f_metakryt))
    print('Podział spółek: ' + str(sol.x))

    return [-sol.fun, sol.x[0], sol.x[1]]


# Przykład - usunąć w gotowej aplikacji :)
def example():
    A = np.array([28.9, 29, 28.5, 28, 28.5, 28.6, 29.4, 30, 31.8, 34.5,
                  33.9, 33.8, 35.2, 34.4, 32, 32.7, 34.2, 35.8, 35.4, 34.4, 34.4])

    B = np.array([41.5, 42.6, 41.5, 41.5, 41.9, 42.2, 42, 42, 43, 44,
                  44, 43.5, 47.3, 46.3, 43.5, 43.8, 45, 47.7, 47, 46, 45.8])

    calculate(A, B, 1/3)


example()
