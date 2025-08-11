# neopixel.py — MicroPython driver for single NeoPixel LED

import time
from machine import Pin

# Timing in microseconds
T0H = 350
T1H = 900
T0L = 900
T1L = 350

class NeoPixel:
    def __init__(self, pin_num, n=1):
        self.pin = Pin(pin_num, Pin.OUT)
        self.n = n
        self.buf = bytearray(n * 3)

    def __setitem__(self, idx, color_tuple):
        r, g, b = color_tuple
        i = idx * 3
        self.buf[i] = g
        self.buf[i + 1] = r
        self.buf[i + 2] = b

    def write(self):
        for byte in self.buf:
            for bit in range(8):
                if byte & (1 << (7 - bit)):
                    self.pin.on()
                    time.sleep_us(T1H)
                    self.pin.off()
                    time.sleep_us(T1L)
                else:
                    self.pin.on()
                    time.sleep_us(T0H)
                    self.pin.off()
                    time.sleep_us(T0L)
        time.sleep_us(50)  # reset

    def fill(self, color_tuple):
        for i in range(self.n):
            self[i] = color_tuple
