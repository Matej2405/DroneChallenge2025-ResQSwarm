class CrashDetector:
    ANGLE_THRESHOLD = 45
    
    def detect_crash(self, angle):
        """
        Detect a crash based on pitch and roll angles.
        Returns True if either roll or pitch exceeds ±45°.
        """
        return abs(angle['roll']) > self.ANGLE_THRESHOLD or abs(angle['pitch']) > self.ANGLE_THRESHOLD


if __name__ == "__main__":
    import time
    from status_led import StatusLED
    from kill_switch import KillSwitch
    from flight_logger import FlightLogger
    from imu_sensor import IMUSensor
    from orientation_estimator import OrientationEstimator

    # Initialize modules
    kill_switch = KillSwitch()
    led = StatusLED()
    logger = FlightLogger()
    imu = IMUSensor()
    orientation = OrientationEstimator()
    crash_detector = CrashDetector()

    logger.start()
    logger.log("Crash Detector test program started")

    print("Waiting for kill switch to be deactivated...")
    led.start_blinking(1.0)

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
        led.start_blinking(0.5)
        imu.calibrate()
        logger.log(f"Calibration completed: accel_offset={imu.accel_offset}, gyro_offset={imu.gyro_offset}")        
        led.stop_blinking()
        led.turn_on()

        # Enter interactive mode
        logger.log("Crash Detector entering interactive mode")
        print("\nInteractive Mode: Move the IMU and observe crash detection.\nPress Ctrl+C to exit.")
        last_time = time.ticks_ms()

        while True:
            current_time = time.ticks_ms()
            dt = time.ticks_diff(current_time, last_time) / 1000.0  # Convert to seconds
            last_time = current_time

            # Read IMU data and update orientation
            data = imu.read_imu()            
            angles = orientation.complementary_filter(data, dt)

            # Check for crash
            if crash_detector.detect_crash(angles):
                print("Crash detected!")
                logger.log(f"Crash detected at angles: pitch={angles['pitch']:.2f}, roll={angles['roll']:.2f}")
                led.start_blinking(0.1)  # Rapid blinking to signal crash
                time.sleep(2)  # Allow observation
                led.stop_blinking()
                break

            # Log and display angles
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
