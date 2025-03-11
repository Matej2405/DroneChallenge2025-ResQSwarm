import time

class FlightLogger:
    def __init__(self, file_name="flight_log.txt"):
        self.file_name = file_name
        self.file = None
        self.start_time = None

    def start(self):
        """Start the logger and initialize the log file."""
        self.file = open(self.file_name, 'w')
        self.start_time = time.ticks_ms()  # Record start time
        self.file.write("Time_ms,Event\n")

    def log(self, event):
        """Log an event with a timestamp."""
        if self.file:
            elapsed_time = time.ticks_diff(time.ticks_ms(), self.start_time)
            self.file.write(f"{elapsed_time},{event}\n")
            
    def flush(self):
        """ Flush the log content to flash memory. """
        if self.file:
            self.file.flush()
        
    
    def stop(self):
        """Stop the logger and close the file."""
        if self.file:
            self.file.close()

if __name__ == "__main__":
    from status_led import StatusLED
    from kill_switch import KillSwitch
    # Initialize components
    led = StatusLED()
    kill_switch = KillSwitch()
    logger = FlightLogger()

    print("System starting...")
    logger.start()
    logger.log("System initialized, waiting for kill switch deactivation")

    led.start_blinking(0.5)  # Blink LED to indicate waiting for kill switch deactivation

    print("Kill switch active. Deactivate it to proceed.")
    try:
        while kill_switch.is_activated():
            time.sleep(0.1)  # Wait for the kill switch to be deactivated

        logger.log("Kill switch deactivated")
        print("Kill switch deactivated!")
        led.stop_blinking()
        led.turn_on()  # Solid LED indicates readiness
        time.sleep(1)  # Hold the LED for visibility
        logger.log("System ready to proceed")

    except KeyboardInterrupt:
        logger.log("Program interrupted by user")
        print("Exiting program.")
    finally:
        led.stop_blinking()
        led.turn_off()
        logger.stop()
        print(f"Log saved to {logger.file_name}")
