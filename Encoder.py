
import time

from fifo import Fifo
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C


class Encoder:
    def __init__(self, rot_a, rot_b):
        self.a = Pin(rot_a, mode=Pin.IN, pull=Pin.PULL_UP)
        self.b = Pin(rot_b, mode=Pin.IN, pull=Pin.PULL_UP)
        self.button = Pin(12, mode=Pin.IN, pull=Pin.PULL_UP)
        self.last_press = time.ticks_ms()
        self.fifo = Fifo(300, typecode='i')
        self.a.irq(handler=self.handler_turn, trigger=Pin.IRQ_RISING, hard=True)
        self.button.irq(handler=self.handler_press, trigger=Pin.IRQ_RISING, hard=True)
        self.i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
        self.oled_width = 128
        self.oled_height = 64
        self.oled = SSD1306_I2C(self.oled_width, self.oled_height, self.i2c)

    def handler_turn(self, pin):
        if self.b():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)

    def handler_press(self, pin):
        if time.ticks_diff(time.ticks_ms(), self.last_press) < 300:
            return
        self.fifo.put(0)
        self.last_press = time.ticks_ms()