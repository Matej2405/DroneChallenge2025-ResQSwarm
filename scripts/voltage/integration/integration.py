import numpy as np

# Define parameters
WINDOW_SIZE = 10  # Number of readings for moving average
THRESHOLD = 240.0  # Example threshold voltage (in Volts); adjust as needed

voltage_buffer = []

def update_buffer(new_voltage):
    voltage_buffer.append(new_voltage)
    if len(voltage_buffer) > WINDOW_SIZE:
        voltage_buffer.pop(0)

def detect_voltage_anomaly(voltage):
    # Simple threshold check; you might enhance with standard deviation or more advanced methods
    return voltage > THRESHOLD

while True:
    voltage = read_voltage()
    if voltage is not None:
        update_buffer(voltage)
        avg_voltage = np.mean(voltage_buffer)
        print(f"Current Voltage: {voltage} V | Moving Avg: {avg_voltage:.2f} V")
        if detect_voltage_anomaly(voltage):
            print("ALERT: Voltage anomaly detected!")
            # Trigger alert functions (see Steps 4 and 5 below)
    time.sleep(0.5)
