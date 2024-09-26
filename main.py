from CalculateBehindService import CalculateBehindService
from Encoder import Encoder
from Isr_adc import Isr_adc
from ShowService import ShowService
from ConnectWifi import ConnectWifi



class main:
    def __init__(self):
        self.encoder = Encoder(10, 11)

        self.calculateBehindService = CalculateBehindService(self.encoder, Isr_adc())
        self.showSever = ShowService(self.encoder, Isr_adc())

    def main(self):
        ConnectWifi().connect()
        self.showSever.menu()




if __name__ == '__main__':
    main().main()

