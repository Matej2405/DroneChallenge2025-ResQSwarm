import time
from machine import I2C, Pin


class IMUSensor:
    def __init__(self):
        # GPIO Pins Configuration
        self.I2C_SDA_PIN = X
        self.I2C_SCL_PIN = X
        self.I2C_VDD_PIN = X
        self.I2C_GND_PIN = X

        # IMU Configuration
        self.IMU_ADDRESS = 0xXX
        self.I2C_FREQ = 400000
        self.WHO_AM_I_REG = 0x0F
        self.CTRL1_XL = 0x10
        self.CTRL2_G = 0x11
        self.OUTX_L_G = 0x22
        self.OUTX_L_XL = 0x28

        # Sensor Calibration Data
        self.gyro_offset = {'x': 0, 'y': 0, 'z': 0}
        self.accel_offset = {'x': 0, 'y': 0, 'z': 0}

        # Initialize IMU Power Pins
        self.vdd_pin = Pin(self.I2C_VDD_PIN, Pin.OUT)
        self.gnd_pin = Pin(self.I2C_GND_PIN, Pin.OUT)

        # Initialize I2C
        self.i2c = None

    def power_on(self):
        """Power on the IMU and initialize communication."""
        self.vdd_pin.on()
        self.gnd_pin.off()
        time.sleep(0.1)
        self.i2c = I2C(0, scl=Pin(self.I2C_SCL_PIN), sda=Pin(self.I2C_SDA_PIN), freq=self.I2C_FREQ)

        # Configure IMU Registers
        self.i2c.writeto_mem(self.IMU_ADDRESS, self.CTRL1_XL, bytes([0b0101_00_01]))  # Accelerometer
        self.i2c.writeto_mem(self.IMU_ADDRESS, self.CTRL2_G, bytes([0b0101_00_00]))  # Gyroscope

    def twos_complement(self, val, bits):
        """Compute the two's complement of int value val."""
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)
        return val

    def read_imu(self):
        """Read data from the IMU."""
        # Read accelerometer data
        accel_data = self.i2c.readfrom_mem(self.IMU_ADDRESS, self.OUTX_L_XL, 6)
        accel_x = self.twos_complement(accel_data[1] << 8 | accel_data[0], 16)
        accel_y = self.twos_complement(accel_data[3] << 8 | accel_data[2], 16)
        accel_z = self.twos_complement(accel_data[5] << 8 | accel_data[4], 16)

        # Read gyroscope data
        gyro_data = self.i2c.readfrom_mem(self.IMU_ADDRESS, self.OUTX_L_G, 6)
        gyro_x = self.twos_complement(gyro_data[1] << 8 | gyro_data[0], 16)
        gyro_y = self.twos_complement(gyro_data[3] << 8 | gyro_data[2], 16)
        gyro_z = self.twos_complement(gyro_data[5] << 8 | gyro_data[4], 16)

        # Adjust for sensitivity
        accel_sensitivity = 0.000061  # ±2g full scale
        gyro_sensitivity = 0.00875    # ±245 dps full scale

        accel_x *= accel_sensitivity
        accel_y *= accel_sensitivity
        accel_z *= accel_sensitivity

        gyro_x *= gyro_sensitivity
        gyro_y *= gyro_sensitivity
        gyro_z *= gyro_sensitivity
        
        # Apply 90-degree CCW rotation around Z-axis
        accel_x, accel_y 	= -accel_y, -accel_x
        gyro_x, gyro_y 		= gyro_y, -gyro_x
        
        # Apply calibration offsets
        accel_x -= self.accel_offset['x']
        accel_y -= self.accel_offset['y']
        accel_z -= self.accel_offset['z']

        gyro_x -= self.gyro_offset['x']
        gyro_y -= self.gyro_offset['y']
        gyro_z -= self.gyro_offset['z']

        return {'accel': {'x': accel_x, 'y': accel_y, 'z': accel_z},
                'gyro': {'x': gyro_x, 'y': gyro_y, 'z': gyro_z}}

    def calibrate(self):
        """Calibrate sensors and log the results."""

        samples = 100
        accel_sum = {'x': 0, 'y': 0, 'z': 0}
        gyro_sum = {'x': 0, 'y': 0, 'z': 0}

        for _ in range(samples):
            data = self.read_imu()
            for axis in ['x', 'y', 'z']:
                accel_sum[axis] += data['accel'][axis]
                gyro_sum[axis] += data['gyro'][axis]
            # Subtract 1g expected in z-direction
            accel_sum['z'] -= 1.0
            time.sleep(0.01)

        for axis in ['x', 'y', 'z']:
            self.accel_offset[axis] = accel_sum[axis] / samples
            self.gyro_offset[axis] = gyro_sum[axis] / samples

        
        print("Calibration done!")
        print(f"Accelerometer offsets: {self.accel_offset}")
        print(f"Gyroscope offsets: {self.gyro_offset}")



if __name__ == "__main__":    
    from status_led import StatusLED
    from kill_switch import KillSwitch
    from flight_logger import FlightLogger
    
    # Initialize modules
    kill_switch = KillSwitch()
    led = StatusLED()
    logger = FlightLogger()
    imu = IMUSensor()

    logger.start()
    logger.log("IMU test program started")

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
        led.start_blinking(0.1)
        imu.calibrate()
        logger.log(f"Calibration completed: accel_offset={imu.accel_offset}, gyro_offset={imu.gyro_offset}")        
        led.stop_blinking()
        led.turn_on()

        # Run indefinitely to allow workshop participants to play
        logger.log("IMU entering interactive mode")
        print("\nIMU interactive mode: Move the IMU and observe readings below.\nPress Ctrl+C to exit.")
        while True:
            data = imu.read_imu()
            print(f"Accelerometer: {data['accel']}, Gyroscope: {data['gyro']}")
            time.sleep(0.2)

    except KeyboardInterrupt:
        logger.log("Program interrupted by user")
        print("\nExiting program.")

    finally:
        led.turn_off()
        logger.stop()
        print(f"Log saved to {logger.file_name}")
