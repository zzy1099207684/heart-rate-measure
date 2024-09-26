
from fifo import Fifo
from machine import Pin, ADC



class Isr_adc:

    def __init__(self, adc_pin_nr=26):
        self.av = ADC(adc_pin_nr)  # sensor AD channel
        self.samples = Fifo(500)  # fifo where ISR will put samples
        self.dbg = Pin(0, Pin.OUT)  # debug GPIO pin for measuring timing with oscilloscope

    def handler(self, tid):
        try:
            self.samples.put(self.av.read_u16())
            self.dbg.toggle()
        except:
            return