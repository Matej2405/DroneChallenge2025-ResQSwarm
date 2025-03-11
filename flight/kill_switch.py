from machine import Pin
from status_led import StatusLED
import time

class KillSwitch:
    def __init__(self, pin_num=25):
        self.switch = Pin(pin_num, Pin.IN, Pin.PULL_UP)

    def is_activated(self):
        """Check if the kill switch is activated (pulled to GND)."""
        return self.switch.value() == 0


if __name__ == "__main__":
    # Initialize Kill Switch and Status LED
    kill_switch = KillSwitch()
    led = StatusLED()

    print("Deactivate the kill switch to test.")
    led.start_blinking(0.5)  # Blink LED to indicate waiting for input

    try:
        while True:
            if not kill_switch.is_activated():
                print("Kill switch deactivated!")
                led.stop_blinking()
                led.turn_on()  # Solid LED indicates activation
                break
            time.sleep(0.1)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting test.")
    finally:
        led.stop_blinking()
        led.turn_off()
