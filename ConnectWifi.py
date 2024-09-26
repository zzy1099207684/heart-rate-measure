
import network
from time import sleep
import Waiting


class ConnectWifi:
    def __init__(self):
        self.ssid = 'KMD652_Group_6'
        self.password = 'Yyzzymj666'
        self.connect()

    def connect(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.ssid, self.password)
        while wlan.isconnected() == False:
            Waiting.startPage()
            print('Waiting for connection')
            sleep(1)
        ip = wlan.ifconfig()[0]
        print(f'Connected on {ip}')
        return ip



