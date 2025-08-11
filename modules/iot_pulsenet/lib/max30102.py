from machine import I2C
import utime

class MAX30102:
    def __init__(self, i2c, address=0x57):
        self.i2c = i2c
        self.address = address
        # Reset & initialize
        self.reset()
        self.setup()

    def reset(self):
        self.i2c.writeto_mem(self.address, 0x09, b'\x40')
        utime.sleep_ms(10)

    def setup(self):
        # FIFO config: sample averaging = 4
        self.i2c.writeto_mem(self.address, 0x08, b'\x40')
        # Mode config: SpO2 mode
        self.i2c.writeto_mem(self.address, 0x09, b'\x03')
        # SpO2 config: 16-bit, 100Hz, 411µA
        self.i2c.writeto_mem(self.address, 0x0A, b'\x27')
        self.i2c.writeto_mem(self.address, 0x0C, b'\x24')  # LED1 = 36mA
        self.i2c.writeto_mem(self.address, 0x0D, b'\x24')  # LED2 = 36mA

    def read_fifo(self):
        data = self.i2c.readfrom_mem(self.address, 0x07, 6)
        red = (data[0] << 16 | data[1] << 8 | data[2]) & 0x03FFFF
        ir  = (data[3] << 16 | data[4] << 8 | data[5]) & 0x03FFFF
        return red, ir

    def read_sequential(self, n=1):
        return [self.read_fifo() for _ in range(n)]
