from Galois import Galois


class Encode:
    def __init__(self, t = 5, n = 63, s = 6):

        self.t = t  # zdolność korekcyjna
        self.n = n  # długość wektora kodowego
        self.r = 2 * t  # bity parzystości / liczba pozycji kontrolnych
        self.k = self.n - self.r  # liczba symboli informacyjnych
        self.s = s  # potęga ciała Gallois
        self.gf = Galois(self.s)


    def encode(self, information) -> list[int]:

        information = bin(information)[2:]
        #print(information)
        if len(information) / self.s > self.k:
            raise Exception(f"Too long information to encode, max bytes: {self.k}")

        padding = self.s - (len(information) % self.s)
        #print(padding)
        information = "0" * padding + information
        #print(information)

        info_pol = []
        for i in range(0, len(information), self.s):
            info_pol.append(information[i : i + self.s])
            #print(i)
            #print(info_pol)

        for i in range(0, len(info_pol)):
            info_pol[i] = self.gf.find_alfa_power(info_pol[i])
            #print(info_pol[i])

        #print(info_pol)
        info_pol = [64] * (self.k - len(info_pol)) + info_pol
        #print(info_pol)
        return self.gf.code_vector(info_pol, self.t)