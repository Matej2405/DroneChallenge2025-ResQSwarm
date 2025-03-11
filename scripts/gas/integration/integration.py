from dronekit import connect, VehicleMode

# Connect to the vehicle (adjust connection string accordingly)
vehicle = connect('127.0.0.1:14550', wait_ready=True)

def arm_and_takeoff(aTargetAltitude):
    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)
    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)
    while True:
        altitude = vehicle.location.global_relative_frame.alt
        print(f"Altitude: {altitude}")
        if altitude >= aTargetAltitude * 0.95:
            print("Target altitude reached")
            break
        time.sleep(1)

# Example usage
arm_and_takeoff(10)  # Take off to 10 meters altitude

# Assume send_email_alert() and send_sms_alert() functions are defined as in the methane example.
TO_PHONE = "+385989943272"  # Recipient's phone number in E.164 format

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


