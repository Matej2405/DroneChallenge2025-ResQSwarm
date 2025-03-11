if __name__ == "__main__":
    import time
    from motor_control import MotorControl
    from crash_detector import CrashDetector
    from imu_sensor import IMUSensor
    from orientation_estimator import OrientationEstimator
    from status_led import StatusLED
    from kill_switch import KillSwitch
    from flight_logger import FlightLogger
    from flight_controller import FlightController

    # Flight parameters
    LIFT_OFF_DURATION = 5  # seconds
    HOVER_DURATION = 5  # seconds
    LANDING_DURATION = 5  # seconds
    MAX_BASE_THROTTLE = 50_000  # Max throttle for lift-off and hover

    # Initialize modules
    kill_switch = KillSwitch()
    led = StatusLED()
    logger = FlightLogger()
    flight_controller = FlightController()
    motor_control = MotorControl()
    crash_detector = CrashDetector()
    imu = IMUSensor()
    orientation = OrientationEstimator()



    print("Waiting for kill switch to be deactivated...")
    led.start_blinking(0.5)

    try:
        while kill_switch.is_activated():
            time.sleep(0.1)
        logger.start()
        logger.log("Flight Controller program started")
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

        # Start flight sequence
        logger.log("Starting flight sequence")
        print("\nFlight sequence initiated.\n")
        target_angles = {'pitch': 0, 'roll': 0, 'yaw': 0}
        last_time = time.ticks_ms()

        # Lift-Off
        logger.log("Starting lift-off")
        print("\nLifting off...")
        start_time = time.ticks_ms()        
        last_flush_time = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start_time) / 1000.0 < LIFT_OFF_DURATION:
            current_time = time.ticks_ms()
            dt = time.ticks_diff(current_time, last_time) / 1000.0  # Convert to seconds
            last_time = current_time

            # Read IMU data and update orientation
            imu_data = imu.read_imu()
            measured_angles = orientation.complementary_filter(imu_data, dt)

            # Check for crash
            if crash_detector.detect_crash(measured_angles):
                print("Crash detected! Stopping all motors.")
                logger.log(f"Crash detected at angles: pitch={measured_angles['pitch']:.2f}, roll={measured_angles['roll']:.2f}")
                motor_control.stop_all_motors()
                led.start_blinking(0.1)
                time.sleep(5)
                led.stop_blinking()
                raise RuntimeError("Crash detected during lift-off.")

            # Compute motor throttles with increasing base throttle
            base_throttle = int((time.ticks_diff(time.ticks_ms(), start_time) / 1000.0) / LIFT_OFF_DURATION * MAX_BASE_THROTTLE)
            motor_throttles = flight_controller.compute_motor_throttles(measured_angles, target_angles, dt, base_throttle)

            # Apply motor throttles
            for motor_name, throttle in motor_throttles.items():
                motor_control.set_motor_throttle(motor_name, throttle)

            # Log data
            logger.log(f"{measured_angles['pitch']:.2f}," +
                       f"{measured_angles['roll']:.2f}," +
                       f"{measured_angles['yaw']:.2f}," +
                       f"{flight_controller.pid_outputs['pitch']:.2f}," +
                       f"{flight_controller.pid_outputs['roll']:.2f}," +
                       f"{flight_controller.pid_outputs['yaw']:.2f}," +
                       f"{motor_throttles['front_left']}," +
                       f"{motor_throttles['rear_left']}," +
                       f"{motor_throttles['front_right']}," +
                       f"{motor_throttles['rear_right']}")
            # Flush the log every 1 second
            if time.ticks_diff(time.ticks_ms(), last_flush_time) >= 1000:
                # Log and display angles
                last_flush_time = time.ticks_ms()
                logger.flush()

        # Hover
        logger.log("Starting hover")
        print("\nHovering...")
        start_time = time.ticks_ms()
        last_flush_time = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start_time) / 1000.0 < HOVER_DURATION:
            current_time = time.ticks_ms()
            dt = time.ticks_diff(current_time, last_time) / 1000.0
            last_time = current_time

            # Read IMU data and update orientation
            imu_data = imu.read_imu()
            measured_angles = orientation.complementary_filter(imu_data, dt)

            # Check for crash
            if crash_detector.detect_crash(measured_angles):
                print("Crash detected! Stopping all motors.")
                logger.log(f"Crash detected at angles: pitch={measured_angles['pitch']:.2f}, roll={measured_angles['roll']:.2f}")
                motor_control.stop_all_motors()
                led.start_blinking(0.1)
                time.sleep(5)
                led.stop_blinking()
                raise RuntimeError("Crash detected during hover.")

            # Compute motor throttles
            motor_throttles = flight_controller.compute_motor_throttles(measured_angles, target_angles, dt, MAX_BASE_THROTTLE)

            # Apply motor throttles
            for motor_name, throttle in motor_throttles.items():
                motor_control.set_motor_throttle(motor_name, throttle)

            # Log data
            logger.log(f"{measured_angles['pitch']:.2f}," +
                       f"{measured_angles['roll']:.2f}," +
                       f"{measured_angles['yaw']:.2f}," +
                       f"{flight_controller.pid_outputs['pitch']:.2f}," +
                       f"{flight_controller.pid_outputs['roll']:.2f}," +
                       f"{flight_controller.pid_outputs['yaw']:.2f}," +
                       f"{motor_throttles['front_left']}," +
                       f"{motor_throttles['rear_left']}," +
                       f"{motor_throttles['front_right']}," +
                       f"{motor_throttles['rear_right']}")
            
            # Flush the log every 1 second
            if time.ticks_diff(time.ticks_ms(), last_flush_time) >= 1000:
                # Log and display angles
                last_flush_time = time.ticks_ms()
                logger.flush()

        # Landing
        logger.log("Starting landing")
        print("\nLanding...")
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) / 1000.0 < LANDING_DURATION:
            current_time = time.ticks_ms()
            dt = time.ticks_diff(current_time, last_time) / 1000.0
            last_time = current_time

            # Reduce base throttle over time
            base_throttle = int(MAX_BASE_THROTTLE * (1 - time.ticks_diff(time.ticks_ms(), start_time) / 1000.0 / LANDING_DURATION))

            # Read IMU data and update orientation
            imu_data = imu.read_imu()
            measured_angles = orientation.complementary_filter(imu_data, dt)

            # Check for crash
            if crash_detector.detect_crash(measured_angles):
                print("Crash detected! Stopping all motors.")
                logger.log(f"Crash detected at angles: pitch={measured_angles['pitch']:.2f}, roll={measured_angles['roll']:.2f}")
                motor_control.stop_all_motors()
                led.start_blinking(0.1)
                time.sleep(5)
                led.stop_blinking()
                raise RuntimeError("Crash detected during lift-off.")

             # Reduce base throttle over time
            base_throttle = int(MAX_BASE_THROTTLE * (1 - time.ticks_diff(time.ticks_ms(), start_time) / 1000.0 / LANDING_DURATION))
            motor_throttles = flight_controller.compute_motor_throttles(measured_angles, target_angles, dt, base_throttle)

            # Apply motor throttles
            for motor_name, throttle in motor_throttles.items():
                motor_control.set_motor_throttle(motor_name, throttle)

            # Log data
            logger.log(f"{measured_angles['pitch']:.2f}," +
                       f"{measured_angles['roll']:.2f}," +
                       f"{measured_angles['yaw']:.2f}," +
                       f"{flight_controller.pid_outputs['pitch']:.2f}," +
                       f"{flight_controller.pid_outputs['roll']:.2f}," +
                       f"{flight_controller.pid_outputs['yaw']:.2f}," +
                       f"{motor_throttles['front_left']}," +
                       f"{motor_throttles['rear_left']}," +
                       f"{motor_throttles['front_right']}," +
                       f"{motor_throttles['rear_right']}")
            # Flush the log every 1 second
            if time.ticks_diff(time.ticks_ms(), last_flush_time) >= 1000:
                # Log and display angles
                last_flush_time = time.ticks_ms()
                logger.flush()

        # Apply zero throttles when landing ends
        motor_control.stop_all_motors()

        print("\nLanding complete. Motors stopped.")
        logger.log("Landing complete")

    except KeyboardInterrupt:
        logger.log("Program interrupted by user")
        print("\nExiting program.")

    finally:
        motor_control.stop_all_motors()
        led.turn_off()
        logger.stop()
        print(f"Log saved to {logger.file_name}")
