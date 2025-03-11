import time
from machine import PWM, Pin

class MotorControl:
    MAX_THROTTLE = 65535  # Maximum PWM duty cycle for operational use

    def __init__(self):
        self.MOTOR_PINS = {
            "front_right": X,  # Motor 3
            "rear_right": X,   # Motor 1
            "front_left": X,   # Motor 2
            "rear_left": X     # Motor 4
        }
        self.motors = {}
        self.initialize_motors()

    def initialize_motors(self):
        """Initialize PWM for each motor."""
        for name, pin_num in self.MOTOR_PINS.items():
            pwm = PWM(Pin(pin_num))
            pwm.freq(200)  # ESCs typically require 50-500 Hz PWM frequency
            pwm.duty_u16(0)  # Start with motors off
            self.motors[name] = pwm

    def set_motor_throttle(self, motor_name, throttle):
        """Set the throttle for a specific motor."""
        throttle = max(0, min(self.MAX_THROTTLE, int(throttle)))  # Clamp throttle
        self.motors[motor_name].duty_u16(throttle)

    def stop_all_motors(self):
        """Turn off all motors."""
        for motor in self.motors.values():
            motor.duty_u16(0)


if __name__ == "__main__":
    from status_led import StatusLED
    from kill_switch import KillSwitch
    from flight_logger import FlightLogger

    # Constants for testing
    MAX_TEST_THROTTLE = 30000  # Throttle limit for testing
    RAMP_DURATION = 2  # Duration for ramp up/down in seconds
    STEPS = 50  # Number of steps for the ramp

    # Initialize modules
    kill_switch = KillSwitch()
    led = StatusLED()
    logger = FlightLogger()
    motor_control = MotorControl()

    logger.start()
    logger.log("Motor Control test program started")

    print("Waiting for kill switch to be deactivated...")
    led.start_blinking(0.5)

    try:
        while kill_switch.is_activated():
            time.sleep(0.1)

        logger.log("Kill switch deactivated")
        print("Kill switch deactivated!")
        led.stop_blinking()
        led.turn_on()

        # Test each motor
        for motor_name in motor_control.MOTOR_PINS.keys():
            print(f"Testing motor: {motor_name}")
            logger.log(f"Testing motor: {motor_name}")

            # Ramp up
            for throttle in range(0, MAX_TEST_THROTTLE + 1, MAX_TEST_THROTTLE // STEPS):
                motor_control.set_motor_throttle(motor_name, throttle)
                logger.log(f"{motor_name} throttle={throttle}")
                time.sleep(RAMP_DURATION / STEPS)

            # Ramp down
            for throttle in range(MAX_TEST_THROTTLE, -1, -MAX_TEST_THROTTLE // STEPS):
                motor_control.set_motor_throttle(motor_name, throttle)
                logger.log(f"{motor_name} throttle={throttle}")
                time.sleep(RAMP_DURATION / STEPS)

            # Turn off the motor
            motor_control.set_motor_throttle(motor_name, 0)
            logger.log(f"{motor_name} test completed")

        print("Motor testing completed. All motors are off.")
        logger.log("Motor testing completed")

    except KeyboardInterrupt:
        logger.log("Program interrupted by user")
        print("\nExiting program.")

    finally:
        motor_control.stop_all_motors()
        led.turn_off()
        logger.stop()
        print(f"Log saved to {logger.file_name}")
