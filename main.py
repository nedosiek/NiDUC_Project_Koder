from Encode import Encode
from Decoder import Decoder
from DecoderPelny import DecoderPelny

e = Encode()
d = Decoder()
dP = DecoderPelny()
temp = list(e.encode(111))
print("Wiadomosc zakodowana:")
print(temp)

temp[7] = 12
temp[1] = 12
temp[2] = 12
#temp[3] = 12
#temp[53] = 12

print("Wiadomosc z bledami:")
print(temp)

decoded_wiadomosc = dP.decoder(temp)
print("Wiadomosc zdekodowana:")
print(decoded_wiadomosc)

'''
from Encode import Encode
from Decoder import Decoder
import random

class Decoder_check_in:
    def __init__(self):
        self.i = 25
        self.error = 0
        self.correct = 0

        # Używamy Encode do zakodowania wiadomości "111"
        self.e = Encode()
        self.test_message = list(self.e.encode(111))  # Konwersja na listę, aby była modyfikowalna
        self.message_length = len(self.test_message)  # Długość wiadomości

        self.d = Decoder()  # Inicjalizujemy dekoder

    def tests_of_decoder(self):
        for _ in range(self.i):
            self.pos = random.randrange(self.message_length)  # Pozycja błędu w zakresie długości wiadomości

            # Kopiujemy wiadomość, aby zachować oryginalny stan do każdej iteracji
            corrupted_message = self.test_message.copy()

            # Wprowadzenie błędu na pozycji `pos`
            corrupted_message[self.pos] = random.randint(0, len(self.test_message) - 1)  # Zakres 1-60


            second_pos = random.randrange(self.message_length)
            third_pos = random.randrange(self.message_length)
            fourth_pos = random.randrange(self.message_length)
            #fifth_pos = random.randrange(self.message_length)
            while self.pos == second_pos == third_pos == fourth_pos:
                second_pos = random.randrange(self.message_length)
                third_pos = random.randrange(self.message_length)
                fourth_pos = random.randrange(self.message_length)
                #fifth_pos = random.randrange(self.message_length)
#  == fourth_pos == fifth_pos

            # Wprowadzenie błędów na pozycjach `second_pos` i `third_pos`
            corrupted_message[second_pos] = random.randint(0, len(self.test_message) - 1)
            corrupted_message[third_pos] = random.randint(0, len(self.test_message) - 1)
            corrupted_message[fourth_pos] = random.randint(0, len(self.test_message) - 1)
            #corrupted_message[fifth_pos] = random.randint(0, len(self.test_message) - 1)

            print(f"Błędna wiadomość (pos: {self.pos}, second_pos: {second_pos}, third_pos: {third_pos}:, fourth_pos: {fourth_pos})", corrupted_message)
# , fourth_pos: {fourth_pos}, fifth_pos:{fifth_pos}
            # Dekodowanie i sprawdzanie wyniku
            result = self.d.simple(corrupted_message)

            if result == "Uncorrectable errors":
                self.error += 1
            else:
                self.correct += 1

            print("Wykonano iterację. Wynik dekodowania:", result)

        # Wyświetlenie wyników
        print("Number of errors:", self.error)
        print("Number of correct:", self.correct)
        return (self.error, self.correct)

# Testowanie
t = Decoder_check_in()
t.tests_of_decoder()
'''