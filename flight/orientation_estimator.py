import math
import time


class OrientationEstimator:
    def __init__(self):
        self.angle = {'pitch': 0.0, 'roll': 0.0, 'yaw': 0.0}
        self.alpha = 0.9  # Complementary filter coefficient

    def normalize_yaw(self, yaw):
        """Normalize yaw to the range -180° to +180°."""
        while yaw > 180:
            yaw -= 360
        while yaw < -180:
            yaw += 360
        return yaw

    def complementary_filter(self, data, dt):
        """Update orientation using a complementary filter."""
        gyro_rate = {
            'pitch'	: data['gyro']['y'],  # Already calibrated
            'roll'	: data['gyro']['x'],   # Already calibrated
            'yaw'	: data['gyro']['z'],    # Already calibrated
        }

        # Gyroscope integration for angular rate
        self.angle['pitch'] += gyro_rate['pitch'] * dt
        self.angle['roll'] += gyro_rate['roll'] * dt
        self.angle['yaw'] += gyro_rate['yaw'] * dt

        # Normalize yaw to avoid overflow
        self.angle['yaw'] = self.normalize_yaw(self.angle['yaw'])

        # Accelerometer angle estimation
        accel_angle_pitch = math.atan2(
            data['accel']['x'],
            math.sqrt(data['accel']['y']**2 + data['accel']['z']**2)
        ) * (180 / math.pi)

        accel_angle_roll = math.atan2(
            data['accel']['y'],
            data['accel']['z']
        ) * (180 / math.pi)
        
        # Complementary filter
        self.angle['pitch'] = self.alpha * self.angle['pitch'] + (1 - self.alpha) * accel_angle_pitch
        self.angle['roll'] = self.alpha * self.angle['roll'] + (1 - self.alpha) * accel_angle_roll
        # Note: Yaw is gyroscope-only (requires magnetometer for full correction)

        # Return the current pitch, roll, and yaw angles.
        return self.angle


if __name__ == "__main__":
    from imu_sensor import IMUSensor
    from status_led import StatusLED
    from kill_switch import KillSwitch
    from flight_logger import FlightLogger

    # Initialize modules
    kill_switch = KillSwitch()
    led = StatusLED()
    logger = FlightLogger()
    imu = IMUSensor()
    orientation = OrientationEstimator()

    logger.start()
    logger.log("Orientation Estimator test program started")

    print("Waiting for kill switch to be deactivated...")
    led.start_blinking(0.5)

    try:
        while kill_switch.is_activated():
            time.sleep(0.1)

        logger.log("Kill switch deactivated")
        print("Kill switch deactivated!")
        led.stop_blinking()
        led.turn_on()

        # Power on and calibrate the IMU
        imu.power_on()
        logger.log("IMU powered on")
        print("IMU powered on, starting calibration...")
        imu.calibrate()
        logger.log(f"Calibration completed: accel_offset={imu.accel_offset}, gyro_offset={imu.gyro_offset}")

        # Run indefinitely to allow participants to interact
        logger.log("Orientation Estimator entering interactive mode")
        print("\nInteractive Mode: Move the IMU to see orientation updates.\nPress Ctrl+C to exit.")
        last_time = time.ticks_ms()
        while True:
            current_time = time.ticks_ms()
            dt = time.ticks_diff(current_time, last_time) / 1000.0  # Convert to seconds
            last_time = current_time

            # Read IMU data (already calibrated)
            data = imu.read_imu()

            # Update orientation
            angles = orientation.complementary_filter(data, dt)

            # Retrieve angles and log
            print(f"Pitch: {angles['pitch']:.2f}°, Roll: {angles['roll']:.2f}°, Yaw: {angles['yaw']:.2f}")
            logger.log(f"Orientation: pitch={angles['pitch']:.2f}, roll={angles['roll']:.2f}, yaw={angles['yaw']:.2f}")

            time.sleep(0.2)

    except KeyboardInterrupt:
        logger.log("Program interrupted by user")
        print("\nExiting program.")

    finally:
        led.turn_off()
        logger.stop()
        print(f"Log saved to {logger.file_name}")
