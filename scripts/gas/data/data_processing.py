THRESHOLD = 10.0  # Example threshold in ppm; adjust as needed

def detect_anomaly(gas_level):
    return gas_level > THRESHOLD

# Example integration:
while True:
    gas_level = read_sensor()
    if gas_level is not None:
        if detect_anomaly(gas_level):
            print("ALERT: High gas level detected!")
        else:
            print(f"Gas level normal: {gas_level} ppm")
    time.sleep(0.5)
