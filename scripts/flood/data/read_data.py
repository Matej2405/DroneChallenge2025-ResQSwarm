import serial
import time

# Inicijalizacija serijskog porta (prilagodi port i brzinu)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # vrijeme za uspostavu veze

def citaj_senzor():
    linija = ser.readline().decode('utf-8').strip()
    if linija:
        try:
            razina_vode = float(linija)
            return razina_vode
        except ValueError:
            return None

while True:
    razina = citaj_senzor()
    if razina is not None:
        print(f"Aktuella razina vode: {razina} cm")
    time.sleep(0.5)
