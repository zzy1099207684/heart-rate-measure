from umqtt.simple import MQTTClient
import ujson
class BehindShowService:
    def __init__(self, Encoder):
        self.rot = Encoder
        self.oled = self.rot.oled
        self.history = []
        self.mqtt_topic='Group6-HR'
        self.BROKER_IP='192.168.6.253'

    def showResult(self, result):
        pointer = 0
        while True:
            self.oled.fill(0)
            for num, prop in enumerate(result[pointer:pointer + 6]):
                self.oled.text(prop, 0, 10 * num, 1)
            self.oled.show()

            if self.rot.fifo.has_data():
                value = self.rot.fifo.get()
                if value == 0:
                    break
                else:
                    pointer += value
                    pointer = min(len(result) - 6, max(0, pointer))

        # 调用  getResult 需要传入包含平均心率，平均ppi的字典

    def getResult(self, index, resultInfo):
        result = [
            f'MEAN HR:{resultInfo["ave_bpm"]}',
            f'MEAN PPI:{resultInfo["ave_ppi"]}',
            f'RMSSD:{resultInfo["rmssd"]}',
            f'SDNN:{resultInfo["sdnn"]}',
            f'SD1:{resultInfo["sd1"]}',
            f'SD2:{resultInfo["sd2"]}',
        ]
        if index == 2:
            result.extend([
                f'SNS:{resultInfo["sns"]}',
                f'PNS:{resultInfo["pns"]}',
            ])
        result.append('Press to quit:->')
        return result

    def show_history(self):
        current = 0
        items = [f'MEASUREMENT {i + 1}' for i in range(len(self.history))]
        items.append('Exit')
        self._show_histories(items, current)
        while True:
            if self.rot.fifo.has_data():
                value = self.rot.fifo.get()
                if value == 0:
                    if current == len(items) - 1:
                        break
                    self.showResult(self.history[current])
                else:
                    current += value
                    current = current % len(items)
                self._show_histories(items, current)

    def _show_histories(self, items, current=0):
        self.oled.fill(0)
        for num, item in enumerate(items):
            text_color = 1
            left = 0
            top = num * 10 + 4
            left2 = 128
            top2 = 10

            if current == num:
                text_color = 0
                self.oled.fill_rect(0, top - 2, left2, top2, 1)
            self.oled.text(item, 0, top, text_color)
        self.oled.show()

    def numScaled(self, val, newMaxNum=13, newMinNum=55, targetMaxNum=65535, targetMinNum=0):
        return round(((val - targetMinNum) / (targetMaxNum - targetMinNum)) * (newMaxNum - newMinNum) + newMinNum)

    # def numScaled(self, val, newMaxNum=10, newMinNum=63, targetMaxNum=65535, targetMinNum=0):
    #     return round(((val - targetMinNum) / (targetMaxNum - targetMinNum)) * (newMaxNum - newMinNum) + newMinNum)

        # mq

    def connectMqtt(self):
        mqtt_client = MQTTClient("", self.BROKER_IP)
        mqtt_client.connect(clean_session=True)
        return mqtt_client

    def outcomeMqtt(self, result):
        measurement = {
            "mean_hr": result['ave_bpm'],
            "mean_ppi": result['ave_ppi'],
            "rmssd": result['rmssd'],
            "sdnn": result['sdnn'],
            "sd1": result['sd1'],
            "sd2": result['sd2']
        }
        return measurement

    def mqtt_publish(self, result):
        try:
            mqttClient = self.connectMqtt()
        except Exception as e:
            error_msg = f"MQTT ERROR: Failed to connect: {e}"
            print(error_msg)

        # Send MQTT message
        try:
            measurement = self.outcomeMqtt(result)
            json_message = ujson.dumps(measurement)
            mqttClient.publish(self.mqtt_topic, json_message)
            print(f"Sending to MQTT: {self.mqtt_topic} -> {json_message}")

        except Exception as e:
            error_msg = f"MQTT ERROR: Failed to publish: {e}"
            print(error_msg)

