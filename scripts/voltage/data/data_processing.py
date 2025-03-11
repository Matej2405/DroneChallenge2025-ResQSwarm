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

# Assume send_email_alert() and send_sms_alert() functions are defined as in the methane example.
TO_EMAIL = "recipient@example.com"
TO_PHONE = "+19876543210"  # Recipient's phone number in E.164 format

while True:
    voltage = read_voltage()
    if voltage is not None:
        update_buffer(voltage)
        avg_voltage = np.mean(voltage_buffer)
        print(f"Voltage: {voltage} V | Moving Avg: {avg_voltage:.2f} V")
        if detect_voltage_anomaly(voltage):
            alert_msg = f"ALERT: Voltage anomaly detected! Current reading: {voltage} V"
            send_email_alert("Voltage Anomaly Alert", alert_msg, TO_EMAIL)
            send_sms_alert(alert_msg, TO_PHONE)
            # Optional: Take additional safety measures (e.g., command the drone)
    time.sleep(0.5)

