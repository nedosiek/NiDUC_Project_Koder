from Galois import Galois
import random

class DecoderPelny:
    t: int  # zdolność korekcyjna
    n: int  # długość wektora kodowego

    r: int  # bity parzystości / liczba pozycji kontrolnych
    k: int  # liczba symboli informacyjnych
    s: int  # potęga ciała Gallois

    def __init__(
        self, t = 3, n = 63, s = 6
    ):
        self.t = t
        self.n = n
        self.r = 2 * t
        self.k = self.n - self.r
        self.s = s
        self.gf = Galois(self.s)
        self.test_message = [64] * 63

    def xor_alfas(self, alfa1, alfa2):
        alfa1 = self.gf.alfas[alfa1]
        alfa2 = self.gf.alfas[alfa2]

        # Pobitowa operacja XOR
        xor_result_pol = [s ^ a for s, a in zip(alfa1, alfa2)]

        # Rezultat operaji w ciałach Galua
        xor_result_value = self.gf.pol_to_number(xor_result_pol)
        result_xor_alfas = self.gf.find_alfa_power(xor_result_value)
        return result_xor_alfas

    # Metoda obliczania syndromów dla alfa^i=1...6
    def calculate_syndromes(self, received: list[int]) -> list[int]:
        syndromes = []
        for i in range(1, 2 * self.t+1):
            syndrome = 64
            for j in range(len(received)):
                if received[j] != 64:
                    k = len(received) - j - 1
                    power = i * k
                    while power > (self.n - 1):
                        power = power % (2**self.s - 1)
                    a_power = self.gf.add_alfa_powers(received[j], power)
                    syndrome = self.xor_alfas(syndrome, a_power)

            syndromes.append(syndrome)
        syndromes = list(reversed(syndromes))
        return syndromes

    # Obliczenie error-locator polynomial
    def algorithm_Euclidean(self, syndromes: list[int]) -> list[int]:
        x = [0] + [64]*(2*self.t)  # x^2t
        #print(x)
        cala_czesc_tab = []
        dzielniki = []
        dodatkowy = syndromes.copy()
        dzielniki.append(dodatkowy)

        reszta = self.gf.div_polynomials(x, dzielniki[0])
        dzielniki.append(reszta)
        cala_czesc = self.gf.div_polynomials_cala(x, dzielniki[0])
        cala_czesc_tab.append(cala_czesc)

        def find_degree(poly):
            degree = len(poly) - 1
            for el in poly:
                if el != 64:
                    break
                degree -= 1
            return degree

        r = find_degree(reszta)
        i = 0

        while r >= self.t:
            cala_czesc = self.gf.div_polynomials_cala(dzielniki[i], dzielniki[i + 1])
            cala_czesc_tab.append(cala_czesc)
            reszta = self.gf.div_polynomials(dzielniki[i], dzielniki[i + 1])
            dzielniki.append(reszta)
            r = find_degree(reszta)
            i += 1

        if i == 0:
            errors = cala_czesc
        else:
            errors = cala_czesc_tab[0]
            for k in range(1, i + 1):
                wiel_pomoc = self.gf.mul_polynomials(errors, cala_czesc_tab[k])
                if k == 1:
                    errors = self.gf.sum_two_polynomials(wiel_pomoc, [64, 0])
                else:
                    errors = self.gf.sum_two_polynomials(wiel_pomoc, cala_czesc_tab[k - 2])

        errors_location = list(reversed(errors))
        #print("Errors location:")
        #print(errors_location)
        return errors_location

    # Obliczenie pierwiastków error-locator polynomial
    def chein_Search(self, errors_location: list[int]) -> list[int]:
        roots = []
        for i in range(0, self.n):
            root = 64
            for j in range(len(errors_location)):
                if errors_location[j] != 64:
                    power = i * (len(errors_location) - j - 1) % (2**self.s - 1)
                    a_power = self.gf.add_alfa_powers(errors_location[j], power)
                    root = self.xor_alfas(root, a_power)

            if root == 64:
                if i == 64:
                    roots.append(i - 64)
                else:
                    roots.append(i)

        #print(roots)
        return roots

    # Korekta błędów
    def error_Values(self, syndromes: list[int], roots: list[int]):
        if len(roots) == 0:
            return []
        T = len(roots)
        equations_y_tab = []
        if T <= self.t:
            if T == 1:
                root = roots[0]
                if syndromes[len(syndromes) - 1] < root:
                    equation = syndromes[len(syndromes) - 1] + self.n - root
                else:
                    equation = syndromes[len(syndromes) - 1] - root
                equations_y_tab.append(equation)
            else:
                potegi = [roots[:]]
                mnoz_czesc_1 = 2

                for i in range(1, T):
                    new_potegi = []
                    for j in range(len(roots)):
                        value = roots[j] * mnoz_czesc_1
                        while value > 62:
                            value = value % (2**self.s - 1)
                        new_potegi.append(value)
                    potegi.append(new_potegi)
                    mnoz_czesc_1 += 1

                if T == 2:
                    equation_1 = self.gf.add_alfa_powers(potegi[0][0], potegi[1][1])
                    equation_2 = self.gf.add_alfa_powers(potegi[0][1], potegi[1][0])
                    det_T = self.xor_alfas(equation_1, equation_2)

                    for i in range(0, len(potegi)):
                        equation_1 = self.gf.add_alfa_powers(
                            potegi[0][(i + 1) % T], syndromes[len(syndromes) - 2]
                        )
                        equation_2 = self.gf.add_alfa_powers(
                            potegi[1][(i + 1) % T], syndromes[len(syndromes) - 1]
                        )
                        equation = self.xor_alfas(equation_1, equation_2)
                        if equation < det_T:
                            equation = equation + self.n - det_T
                        else:
                            equation = equation - det_T
                        equations_y_tab.append(equation)

                else:
                    diag_1 = 64
                    diag_2 = 64
                    for i in range(0, T):
                        mnoz_czesc_1 = self.gf.add_alfa_powers(
                            potegi[i][0], potegi[(i + 1) % T][1]
                        )
                        mnoz_1 = self.gf.add_alfa_powers(
                            mnoz_czesc_1, potegi[(i + 2) % T][2]
                        )
                        diag_1 = self.xor_alfas(diag_1, mnoz_1)
                        mnoz_czesc_2 = self.gf.add_alfa_powers(
                            potegi[(i + 2) % T][0], potegi[(i + 1) % T][1]
                        )
                        mnoz_2 = self.gf.add_alfa_powers(mnoz_czesc_2, potegi[i][2])
                        diag_2 = self.xor_alfas(diag_2, mnoz_2)
                    det_T = self.xor_alfas(diag_1, diag_2)

                    syndromes = list(reversed(syndromes))
                    s = []
                    for el in range(len(syndromes) // 2):
                        s.append(syndromes[el])

                    for i in range(0, T):
                        diag_1 = 64
                        diag_2 = 64
                        for j in range(0, T):
                            mnoz_czesc_1 = self.gf.add_alfa_powers(
                                potegi[j][i], potegi[(j + 1) % T][(i + 1) % T]
                            )
                            mnoz_1 = self.gf.add_alfa_powers(
                                mnoz_czesc_1, s[(j + 2) % T]
                            )
                            diag_1 = self.xor_alfas(diag_1, mnoz_1)
                            mnoz_czesc_2 = self.gf.add_alfa_powers(
                                potegi[(j + 2) % T][i], potegi[(j + 1) % T][(i + 1) % T]
                            )
                            mnoz_2 = self.gf.add_alfa_powers(mnoz_czesc_2, s[j])
                            diag_2 = self.xor_alfas(diag_2, mnoz_2)
                        equation = self.xor_alfas(diag_1, diag_2)
                        if equation < det_T:
                            equation = equation + self.n - det_T
                        else:
                            equation = equation - det_T
                        equations_y_tab.append(equation)

                    equations_y_tab = equations_y_tab[1:] + equations_y_tab[:1]

        return equations_y_tab

    def decoder(self, received: list[int]):
        syndromes = self.calculate_syndromes(received)
        errors_location = self.algorithm_Euclidean(syndromes)
        roots = self.chein_Search(errors_location)
        y_tab = self.error_Values(syndromes, roots)
        e_x = [64] * (roots[len(roots) - 1] + 1)
        for i in range(1, len(roots) + 1):
            e_x[roots[len(roots) - i]] = y_tab[len(y_tab) - i]

        e_x = list(reversed(e_x))
        c_x = self.gf.sum_two_polynomials(received, e_x)

        return c_x

    def full_error_scan(self, num_tests=1000):
        if not hasattr(self, "test_message"):
            raise ValueError("Brak testowej wiadomości. Ustaw self.test_message przed wywołaniem tej metody.")

        message_length = len(self.test_message)
        total_tests = 0
        errors = 0
        correct = 0

        for _ in range(num_tests):  # Wykonujemy określoną liczbę losowych testów
            try:
                total_tests += 1
                corrupted_message = self.test_message.copy()

                # Losowy wybór pozycji błędów
                error_positions = sorted(random.sample(range(message_length), 5))

                for pos in error_positions:
                    corrupted_message[pos] = random.randint(0, 62)  # Losowy symbol w GF(2^6)

                print(f"Testowanie błędów na pozycjach: {error_positions}")

                # Dekodowanie za pomocą `decoder`
                result = self.decoder(corrupted_message)

                if result == "Uncorrectable errors":
                    errors += 1
                else:
                    correct += 1
            except KeyError:
                print("xd")
            except KeyboardInterrupt:
                print("Testowanie przerwane.")
                break
            except IndexError:
                errors += 1

        print("Pełne testowanie zakończone.")
        print(f"Liczba niepoprawnych dekodowań: {errors}")
        print(f"Liczba poprawnych dekodowań: {correct}")
        print(f"Łączna liczba testów: {total_tests}")

        return errors, correct

# d = DecoderPelny()
# t = Transmitter()
# y = [64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 2, 34, 50, 27, 18, 34, 17, 20, 15, 16, 19, 2]
# print(y)
# m = [64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 2, 64, 64, 64, 64, 64, 64, 64, 64, 64, 2, 34, 50, 27, 18, 34, 17, 20, 15, 16, 28, 2]
# print(m)
# k = d.decoder(m)
# print(k)