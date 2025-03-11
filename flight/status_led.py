from machine import Pin, Timer

class StatusLED:
    def __init__(self, pin_num=25):
        self.led = Pin(pin_num, Pin.OUT)
        self.timer = Timer()

    def start_blinking(self, interval):
        self.timer.init(freq=1/interval, mode=Timer.PERIODIC, callback=lambda t: self.led.toggle())

    def stop_blinking(self):
        self.timer.deinit()
        self.led.off()

    def turn_on(self):
        self.led.on()

    def turn_off(self):
        self.led.off()

if __name__ == "__main__":
    led = StatusLED()
    led.start_blinking(0.5)
    import time
    time.sleep(3)
    led.stop_blinking()
    led.turn_on()
    time.sleep(2)
    led.turn_off()
