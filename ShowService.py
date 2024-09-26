
from CalculateBehindService import CalculateBehindService




class ShowService:
    def __init__(self, Encoder, ia):
        self.calculateSever = CalculateBehindService(Encoder, ia)
        self.rot = Encoder
        self.oled = self.rot.oled


    def menu(self):
        items = [
            ('1.MEASURE HR', self.calculateSever.heartRate),
            ('2.HRV ANALYSIS', self.calculateSever.heartRatePrase),
            ('3.KUBIOS', self.calculateSever.kubios),
            ('4.HISTORY', self.calculateSever.showHistory),
        ]
        current = 0
        self._menu(items, current)
        while True:
            while self.rot.fifo.has_data():
                value = self.rot.fifo.get()
                if value == 0:
                    method = items[current][1]
                    method()
                else:
                    current += value
                    current = current % len(items)
                self._menu(items, current)

    def _menu(self, items, current=0):
        self.oled.fill(0)
        for num, item in enumerate(items):
            text_color = 1
            left = 0
            top = num * 16 + 4
            left2 = 128
            top2 = 12

            if current == num:
                text_color = 0
                self.oled.fill_rect(0, top - 2, left2, top2, 1)
            self.oled.text(item[0], 0, top, text_color)
        self.oled.show()
