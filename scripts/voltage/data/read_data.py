import serial
import time

# Initialize serial port (adjust port and baud rate as necessary)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Allow connection to establish

def read_voltage():
    line = ser.readline().decode('utf-8').strip()
    if line:
        try:
            voltage = float(line)
            return voltage
        except ValueError:
            return None

while True:
    voltage = read_voltage()
    if voltage is not None:
        print(f"Voltage reading: {voltage} V")
    time.sleep(0.5)
