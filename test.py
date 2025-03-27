
from DecoderPelny import DecoderPelny

import random
dP = DecoderPelny()

# Ustawiamy testową wiadomość (63 symbole w GF(2^6), np. same 64 jako brak błędów)
dP.test_message = [64] * 63

# Wywołujemy metodę
errors, correct = dP.full_error_scan()