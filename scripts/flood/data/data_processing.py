import numpy as np

PRAG = 100.0  # primjer praga, npr. 100 cm, prilagodi po potrebi

def detektiraj_anomaliu(razina):
    return razina > PRAG

# Glavna petlja
while True:
    razina = citaj_senzor()
    if razina is not None:
        print(f"Aktuella razina vode: {razina} cm")
        if detektiraj_anomaliu(razina):
            print("UPOZORENJE: Detektirana je nenormalno visoka razina vode!")
            # Ovdje možemo pozvati funkcije za slanje upozorenja (email/SMS)
    time.sleep(0.5)
