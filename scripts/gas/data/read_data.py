import serial
import time

# Initialize serial port (adjust COM port and baud rate as necessary)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # wait for the connection to establish

def read_sensor():
    line = ser.readline().decode('utf-8').strip()
    if line:
        try:
            # Assuming sensor returns a numeric value
            value = float(line)
            return value
        except ValueError:
            return None

while True:
    gas_level = read_sensor()
    if gas_level is not None:
        print(f"Current gas level: {gas_level} ppm")
    time.sleep(0.5)



