import time

class PID:
    def __init__(self, Kp, Ki, Kd, output_limits=(None, None)):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.output_limits = output_limits

        self._integral = 0
        self._previous_error = 0

    def compute(self, error, dt):
        self._integral += error * dt
        derivative = (error - self._previous_error) / dt if dt > 0 else 0

        output = self.Kp * error + self.Ki * self._integral + self.Kd * derivative

        # Apply output limits
        min_output, max_output = self.output_limits
        if min_output is not None:
            output = max(min_output, output)
        if max_output is not None:
            output = min(max_output, output)

        self._previous_error = error

        return output

class FlightController:
    def __init__(self):
        # Initialize PID regulators
        self.pid_roll 	= PID(Kp=64.0, Ki=0.0, Kd=0.0, output_limits=(-5000, 5000))
        self.pid_pitch 	= PID(Kp=64.0, Ki=0.0, Kd=0.0, output_limits=(-5000, 5000))
        self.pid_yaw 	= PID(Kp=128.0, Ki=0.0, Kd=0.0, output_limits=(-5000, 5000))
        

    def compute_motor_throttles(self, measured_angles, target_angles, dt, base_throttle = 55000):
        """Compute motor throttles using PID controllers."""
        pid_roll 	= self.pid_roll.compute(measured_angles['roll'] - target_angles['roll'], dt)
        pid_pitch 	= self.pid_pitch.compute(measured_angles['pitch'] - target_angles['pitch'], dt)
        pid_yaw 	= self.pid_yaw.compute(measured_angles['yaw'] - target_angles['yaw'], dt)
        
        self.pid_outputs = {'roll' 	: pid_roll,
                            'pitch' : pid_pitch,
                            'yaw' 	: pid_yaw}
        
        # Compute motor speeds corrections
        return {
            "front_right"	: 1.15*(base_throttle - pid_roll - pid_pitch + pid_yaw),
            "rear_right"	: 1.1*(base_throttle - pid_roll + pid_pitch - pid_yaw),
            "front_left"	: 1.0*(base_throttle + pid_roll - pid_pitch - pid_yaw),
            "rear_left"		: 1.0*(base_throttle + pid_roll + pid_pitch + pid_yaw)
        }



if __name__ == "__main__":
    from motor_control import MotorControl
    from crash_detector import CrashDetector
    from imu_sensor import IMUSensor
    from orientation_estimator import OrientationEstimator
    from status_led import StatusLED
    from kill_switch import KillSwitch
    from flight_logger import FlightLogger
    
    # Initialize modules
    kill_switch = KillSwitch()
    led = StatusLED()
    logger = FlightLogger()
    flight_controller = FlightController()
    motor_control = MotorControl()
    crash_detector = CrashDetector()
    imu = IMUSensor()
    orientation = OrientationEstimator()
    
    logger.start()
    logger.log("Flight Controller test program started")

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

        # Hover loop
        logger.log("Starting hover loop")
        print("\nHovering... Adjusting to maintain zero roll, pitch, and yaw.\nPress Ctrl+C to exit.")
        target_angles = {'pitch': 0, 'roll': 0, 'yaw': 0}
        last_time = time.ticks_ms()
        last_flush_time = time.ticks_ms()

        while True:
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
                led.start_blinking(0.1)  # Rapid blinking to signal crash
                time.sleep(5)
                led.stop_blinking()
                break

            # Compute motor throttles
            motor_throttles = flight_controller.compute_motor_throttles(measured_angles, target_angles, dt, base_throttle = 2_000)
            
            # Apply motor throttles
            for motor_name, throttle in motor_throttles.items():
                        motor_control.set_motor_throttle(motor_name, throttle)
                        
            logger.log(		f"{measured_angles['pitch']:.2f}" +','
                            f"{measured_angles['roll']:.2f}" +','
                            f"{measured_angles['yaw']:.2f}" +','
                            f"{flight_controller.pid_outputs['pitch']:.2f}" +','
                            f"{flight_controller.pid_outputs['roll']:.2f}" +','
                            f"{flight_controller.pid_outputs['yaw']:.2f}" +','
                            f"{motor_throttles['front_left']}" +','
                            f"{motor_throttles['rear_left']}" +','
                            f"{motor_throttles['front_right']}" +','
                            f"{motor_throttles['rear_right']}")

            # Flush the log every 1 second
            if time.ticks_diff(time.ticks_ms(), last_flush_time) >= 1000:
                # Log and display angles
                last_flush_time = time.ticks_ms()
                print(f"{measured_angles}, {motor_throttles}")
                logger.flush()


    except KeyboardInterrupt:
        logger.log("Program interrupted by user")
        print("\nExiting program.")

    finally:
        motor_control.stop_all_motors()
        led.turn_off()
        logger.stop()
        print(f"Log saved to {logger.file_name}")
