
galois_power = 6

class Galois:
    def __init__(self, number, power = galois_power):
        self.power = power

        if number >= 2**power:
            raise ValueError("too big number for the GF(2**{})".format(self.power))
        self.number = number
        self.alfas = dict()
        for i in range(2**self.power - 1):
            self.alfas[i] = self.generate_alfa(i)

        # reprezentacja zera jako maksymalna potęga w ciele
        self.alfas[2**self.power] = self.generate_alfa(2**self.power)

    # x^6 + x + 1
    def primitive(self):
        return 0b100011

    def primitive_pol(self):
        return [1, 0, 0, 0, 0, 1, 1]

    @staticmethod
    def generate_symbols(power = galois_power):
        return [i for i in range(0, 2**power - 1)]

    def pol_to_number(self, polynomial):
        s = map(str, polynomial)
        s = "".join(s)
        return int(s)

    def number_to_pol(self, number):
        n = bin(number)
        return [c for c in n[2:]]

    def is_alfa_zero(self, alfa_power):
        return alfa_power == 2**self.power

    def generate_alfa(self, power):

        if power in self.alfas:
            return self.alfas[power]

        if self.is_alfa_zero(power):
            return [0 for _ in range(self.power)]

        if power == 2**self.power - 1:
            raise ValueError("Alfa with such power doesnt exists")

        if power < self.power:
            output = [0 for _ in range(self.power)]

            output[-(power + 1)] = 1
            return output

        pol1 = [1]
        for _ in range(power):
            pol1.append(0)

        primitive = self.primitive_pol()
        primitive = [0] * (power - (len(primitive) - 1)) + primitive
        remainder = pol1[:]
        diff_powers = abs(pol1.index(1) - primitive.index(1))

        while diff_powers >= 0:

            partial = [0] * (power + 1)

            for i in range(len(partial) - diff_powers):
                partial[i] = primitive[i + diff_powers]

            remainder = [a ^ b for a, b in zip(partial, remainder)]
            if all(coeff == 0 for coeff in remainder):
                break

            diff_powers = primitive.index(1) - remainder.index(1)

        self.alfas[power] = remainder[len(remainder) - self.power :]
        return self.alfas[power]

    def find_alfa_power(self, alfa_value):
        for key, val in self.alfas.items():
            h = self.pol_to_number(val)
            if h == int(alfa_value):
                return key

    def find_alfa_power1(self, alfa_value):
        for key, val in self.alfas.items():
            h = int(str(self.pol_to_number(val)), 2)
            if h == int(alfa_value):
                return key

    @staticmethod
    def calculate_polynomial(
            polynomial: int, x: int, power = galois_power):

            if x not in range(0, 2**power - 1):
                raise ValueError("provided x in polynomial calculation should be valid symbol in this GF field")

            # tylko reszta przy x^0 ma znaczenie
            if x == 0:
                return polynomial & 1 << 0

            sum = 0
            i = 0
            while polynomial:

                if i == 0:
                    sum += polynomial & 1
                else:
                    base = x * (polynomial & 1)
                    pow = base**i
                    sum += pow % 2**power

                polynomial >>= 1
                i += 1

            return sum

    def mul_polynomials(self, polynomial1, polynomial2):

        sum_polynomials = list()
        for i, symbol in enumerate(polynomial2):
            if symbol == 64:
                continue

            # przemnożenie przez x do danej potęgi == przesunięcie w prawo
            shift_amount = len(polynomial2) - 1 - i
            help1 = polynomial1.copy()
            for _ in range(shift_amount):
                help1.append(64)

            for j in range(len(help1)):
                if help1[j] != 64:
                    help1[j] = self.add_alfa_powers(help1[j], symbol)

            sum_polynomials.append(help1)

        max_length = max(len(x) for x in sum_polynomials)

        # Dopisz zera do każdego wielomianu w sum_polynomials
        for i in range(len(sum_polynomials)):
            brakujace_zera = max_length - len(sum_polynomials[i])
            sum_polynomials[i] = [64] * brakujace_zera + sum_polynomials[i]

        result = []
        for i in range(len(sum_polynomials[0])):
            suma = 0
            for j in range(len(sum_polynomials)):
                alfa = self.alfas[sum_polynomials[j][i]]
                suma ^= int(str(self.pol_to_number(alfa)), 2)

            # tutaj suma to nie wykładnik alfy, ale wartość alfy
            # dla podanej wartości, chcemy znowu żeby współczynniki reprezentowały potęgi alfy
            result.append(self.find_alfa_power(bin(suma)[2:]))

        return result

    def add_alfa_powers(self, alfa_power1, alfa_power2):

        if alfa_power1 > 2**self.power:
            raise ValueError(f"alfa power1 higher than {2**self.power}")

        if alfa_power2 > 2**self.power:
            raise ValueError(f"alfa power2 higher than {2**self.power}")

        if self.is_alfa_zero(alfa_power1):
            return 64
        elif self.is_alfa_zero(alfa_power2):
            return 64

        return (alfa_power1 + alfa_power2) % (2**self.power - 1)


    def create_generating_polynomial(self, t) :
        if 2*t < 1:
            raise ValueError("Potega musi byc wieksza lub rowna 1.")

        generating_polynomial = [0, 1]
        for i in range(2, 2*t+1):
            generating_help = [0, i]
            generating_polynomial = self.mul_polynomials(generating_polynomial, generating_help)
        return generating_polynomial

    def sum_two_polynomials(self, polynomial1, polynomial2):

        sum_polynomials = [polynomial1, polynomial2]
        max_length = max(len(p) for p in sum_polynomials)

        # Dopisz zera do każdego wielomianu w sum_polynomials
        for i in range(len(sum_polynomials)):
            #missing_zero =  - len(sum_polynomials[i])
            missing_zero = max_length - len(sum_polynomials[i])
            sum_polynomials[i] = [64] * missing_zero + sum_polynomials[i]

        result = []
        for i in range(len(sum_polynomials[0])):
            suma = 0
            for j in range(len(sum_polynomials)):
                '''if sum_polynomials[j][i] not in self.alfas:
                    raise ValueError(f"Niepoprawny klucz {sum_polynomials[j][i]} w self.alfas")
                '''
                alfa = self.alfas[sum_polynomials[j][i]]
                suma ^= int(str(self.pol_to_number(alfa)), 2)

            result.append(self.find_alfa_power(bin(suma)[2:]))
        return result


    def code_vector(self, m, t):
        if t < 1:
            raise ValueError("Power must be greater than or equal to 1")

        # mnożymy m(x) i x^power
        # dodajemy 64 na koniec (64 reprezentacja 0 w ciele Galois)
        g = self.create_generating_polynomial(t)
        #print('Wielomian')
        #print(g)
        m += [64] * (2 * t)
        #print(m)
        r = self.div_polynomials(m, g)
        #print(r)

        code_vec = self.sum_two_polynomials(m, r)

        return code_vec

    # symbol * x = 1
    # find x
    def mul_inverse(self) -> int:

        for x in self.generate_symbols(self.power):
            if (self.number * x) % 2**self.power == 1:
                return x
        return None

    # symbol + x = 0
    # find x
    def add_inverse(self) -> int:

        for x in self.generate_symbols(self.power):
            if (self.number + x) % 2**self.power == 0:
                return x
        return None


    # obliczanie reszty r(x) z dzielenia przez g(x)
    def div_polynomials(self, polynomial1, polynomial2):

        for i in range(len(polynomial2)):
            if polynomial2[0] == 64:
                polynomial2.pop(0)
            else:
                break

        # cała część z dzielenia
        div_whole_part = [64] * (len(polynomial1) - len(polynomial2) + 1)

        # Liczba cyfr w całą części odpowiedzi zależy od rozmiarów wielomianów
        for i in range(len(polynomial1) - len(polynomial2) + 1):
            poly_multi = [64] * len(div_whole_part)
            next_coeff = polynomial1[i]
            if next_coeff == 64:
                continue

            if next_coeff < polynomial2[0]:
                if polynomial2[0] == 64:
                    continue
                else:
                    next_coeff = (63 + polynomial1[i] - polynomial2[0]) % 63
            else:
                next_coeff -= polynomial2[0]

            # Jeśli pierszy współczynnik przy pierwszym wielomiani
            # mniejszy od współczynnik a przy drudim

            div_whole_part[i] = next_coeff
            if i != 0:
                poly_multi[i] = div_whole_part[i]
                multi_result = self.mul_polynomials(poly_multi, polynomial2)
                polynomial1 = self.sum_two_polynomials(multi_result, polynomial1)
            else:
                multi_result = self.mul_polynomials(div_whole_part, polynomial2)
                polynomial1 = self.sum_two_polynomials(multi_result, polynomial1)
        remainder = polynomial1

        return remainder


    def div_polynomials_cala(
        self, polynomial1: list[int], polynomial2: list[int]
    ) -> list[int]:

        for i in range(len(polynomial2)):
            if polynomial2[0] == 64:
                polynomial2.pop(0)
            else:
                break
        cala_czesc = [64] * (len(polynomial1) - len(polynomial2) + 1)

        # Liczba cyfr w całą części odpowiedzi zależy od rozmiarów wielomianów
        for i in range(len(polynomial1) - len(polynomial2) + 1):
            if polynomial1 == [64] * len(polynomial1):
                break
            wiel_dla_mnozenia = [64] * len(cala_czesc)
            next_coeff = polynomial1[i]
            if next_coeff == 64:
                continue
            # Jeśli pierszy współczynnik przy pierwszym wielomiani
            # mniejszy od współczynnik a przy drudim
            if next_coeff < polynomial2[0]:
                if polynomial2[0] == 64:
                    continue
                else:
                    next_coeff = (63 + polynomial1[i] - polynomial2[0]) % 63
            else:
                next_coeff -= polynomial2[0]

            cala_czesc[i] = next_coeff
            if i != 0:
                wiel_dla_mnozenia[i] = cala_czesc[i]
                rezult_mnozenia = self.mul_polynomials(wiel_dla_mnozenia, polynomial2)
                polynomial1 = self.sum_two_polynomials(rezult_mnozenia, polynomial1)
            else:
                rezult_mnozenia = self.mul_polynomials(cala_czesc, polynomial2)
                polynomial1 = self.sum_two_polynomials(rezult_mnozenia, polynomial1)
        reszta = polynomial1

        return cala_czesc

    def __add__(self, o):
        return self.number ^ o.number

    def __sub__(self, o):
        return self.number ^ o.number

    def __mul__(self, o):
        return self.number & o.number