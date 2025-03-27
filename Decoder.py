from numba.core.typing.builtins import Print

from Galois import Galois
#from main import message
import random

class Decoder:
    def __init__(self, t = 5, n = 63, s = 6):

        self.t = t # zdolność korekcyjna
        self.n = n # długość wektora kodowego
        self.r = 2 * t # bity parzystości / liczba pozycji kontrolnych
        self.k = self.n - self.r # liczba symboli informacyjnych
        self.s = s # potęga ciała Gallois
        self.gf = Galois(self.s)
        self.test_message = [64] * 63

    def simple(self, vector_received):
        messenger = "Uncorrectable errors"
        vector_corrected = list()
        g = self.gf.create_generating_polynomial(self.t)

        for i in range(0, self.n): #k=53
            syndrome = self.gf.div_polynomials(vector_received, g)
            #print(syndrome)
            syndrome_weight = 0
            for el in syndrome:
                if el != 64:
                    syndrome_weight += 1


            if syndrome_weight <= self.t:
                vector_corrected = self.gf.sum_two_polynomials(vector_received, syndrome)
                if i == 0:
                    break
                else:
                    for j in range(0, i):
                        first_element = vector_corrected.pop(0)
                        vector_corrected.insert(63, first_element)
                    return vector_corrected # jezeli uda sie poprawic wektor
            else:
                if i == self.n:
                    return messenger
                else:
                    last_element = vector_received.pop()
                    vector_received.insert(0, last_element)
                    #print(vector_received)
                    #print(last_element)

        # z tego sie bierze blad - nasz program tutaj wywala pusta liste
        return messenger # blad - nie udalo sie poprawic wektora
