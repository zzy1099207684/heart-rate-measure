
from piotimer import Piotimer
import time
import urequests as requests
from BehindShowService import BehindShowService

import Waiting




class CalculateBehindService:

    def __init__(self, Encoder, ia):
        self.ia = ia
        self.tmr = Piotimer(mode=Piotimer.PERIODIC, freq=250, callback=self.ia.handler)
        self.sdnn = 0
        self.behindShowService = BehindShowService(Encoder)
        self.behindShowService.history = []
        self.currentTime = time.localtime()
        self.year = self.currentTime[0]
        self.month = self.currentTime[1]
        self.day = self.currentTime[2]
        self.oled = Encoder.oled
        self.APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
        self.CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
        self.CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"
        self.TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token"


    def getPPIIntervalFromSignals(self):
        slipNum = 250
        sampleSeconds = 3
        sec = sampleSeconds * slipNum
        signals = []
        signals2 = []
        allSampleNum = []
        allBpm = []
        firstTime = time.time()
        self.oled.fill(0)
        lastArr = []
        lastpoint = 0
        maxVal = 32768
        minVal = 200
        x = 0
        ppiNum = 0
        bpm = 0

        while True:
            # to read:
            if not self.ia.samples.empty():
                value = self.ia.samples.get()
                signals.append(value)
                signals2.append(value)

                if len(signals2) >= 15:
                    sclval = self.behindShowService.numScaled(max(signals2), 10, 63, maxVal, minVal)
                    if sclval < 10:
                        sclval = 10
                    elif sclval > 63:
                        sclval = 63
                    if len(lastArr) < 128:
                        temp = {x: lastpoint, x + 1: sclval}
                        lastArr.append(temp)
                    if x == 128:
                        x = 0
                    if len(lastArr) == 128:
                        lastVal = lastArr[x]
                        self.oled.line(x, lastVal[x], x + 1, lastVal[x + 1], 0)
                        self.oled.show()
                        lastVal[x] = lastpoint
                        lastVal[x + 1] = sclval
                    self.oled.line(x, lastpoint, x + 1, sclval, 1)
                    self.oled.fill_rect(0, 0, 128, 9, 1)
                    self.oled.text(f'PPI:{ppiNum}', 2, 0, 0)
                    self.oled.text(f'HR:{bpm}', 70, 0, 0)
                    self.oled.show()
                    lastpoint = sclval
                    signals2 = []
                    x += 1


                if len(signals) >= sec:
                    maxVal = max(signals)
                    minVal = min(signals)
                    threshold = round((minVal + maxVal) / 2)
                    peakIndexArr = []
                    maxValue = 0
                    num = 0
                    for i, v in enumerate(signals):
                        if v > threshold and v > maxValue:
                            maxValue = v
                            num = i
                        elif v < threshold and maxValue > 0:
                            peakIndexArr.append(num)
                            maxValue = 0
                    signals = []
                    PPI_Arr = []
                    sampleNum = 0
                    for i, v in enumerate(peakIndexArr):
                        if i + 1 <= len(peakIndexArr) - 1:
                            sampleNum = (peakIndexArr[i + 1] - peakIndexArr[i]) * 0.004

                        if 2 > sampleNum > 0.25:
                            PPI_Arr.append(sampleNum)
                            ppiNum = round(sampleNum * 1000)
                            allSampleNum.append(ppiNum)



                    # Some of the artefacts and false readings can be filtered out by
                    # assuming that heart rate is between 30 – 240 bpm
                    bpmArr = []
                    for i, v in enumerate(PPI_Arr):
                        hr = 60 / v
                        bpmArr.append(hr)

                    if len(bpmArr) > 0:
                        bpmArr.sort()
                        bpm = round(bpmArr[len(bpmArr)//2])
                        allBpm.append(bpm)
                        print(bpm, '-----------------')
                    else:
                        pass
                        # print(0)
                secondTime = time.time()
                if secondTime - firstTime >= 30:
                    break
        allSampleNum.sort()
        allSampleNum.pop(0)
        allSampleNum.pop(-1)
        ave_ppi = round(sum(allSampleNum) / len(allSampleNum))
        ave_bpm = round(sum(allBpm) / len(allBpm))

        res = {"ave_ppi": ave_ppi,
               "ave_bpm": ave_bpm,
               "allSampleNum": allSampleNum}

        return res

    # click
    # 1.rate and manydata 3.kubiosdata
    def calculateDataFromPPInterval(self, step):
        res = self.getPPIIntervalFromSignals()
        ave_ppi = res["ave_ppi"]
        ave_bpm = res["ave_bpm"]
        allSampleNum = res["allSampleNum"]

        Waiting.waitImg()

        # -----------------------------------
        if step == 1:
            res = [f'ave_bpm:{ave_bpm}', 'Press to quit:->']
        elif step == 2:
            res = self.heartRateCal(ave_ppi, ave_bpm, allSampleNum)
            # self.mqtt_publish(res)
            self.behindShowService.mqtt_publish(res)
            res = self.behindShowService.getResult(1,res)
        elif step == 3:
            res = self.kubiosPrase(allSampleNum, ave_ppi, ave_bpm)
            res = self.behindShowService.getResult(2,res)
        self.behindShowService.showResult(res)
        self.behindShowService.history.append(res)

    def heartRateCal(self, ave_ppi, ave_bpm, allSampleNum):
        sdsd_2nd = 0
        sdnn = 0
        rmssd_temp = 0
        ppi_head = None
        ppi_length = len(allSampleNum)
        for ppi in allSampleNum:
            sdnn += (ppi - ave_ppi) ** 2
            if ppi_head is not None:
                rmssd_temp += (ppi - ppi_head) ** 2
                sdsd_2nd += ppi - ppi_head
            ppi_head = ppi

        sdnn = round((sdnn / (ppi_length - 1)) ** (1 / 2))
        rmssd = round((rmssd_temp / (ppi_length - 1)) ** (1 / 2))
        sdsd = round((rmssd_temp / (ppi_length - 1) - (sdsd_2nd / ppi_length) ** 2) ** (1 / 2))
        sd1 = round(((sdsd ** 2) / 2) ** (1 / 2))
        sd2 = round((2 * (sdnn ** 2) - (sdsd ** 2) / 2) ** (1 / 2))
        res = {"sdnn": sdnn,
               "rmssd": rmssd,
               "sdsd": sdsd,
               "sd1": sd1,
               "sd2": sd2,
               "ave_ppi": ave_ppi,
               "ave_bpm": ave_bpm}
        return res

    def kubiosPrase(self, ppi_samples, ave_ppi, ave_bpm):
        APIKEY = self.APIKEY
        CLIENT_ID = self.CLIENT_ID
        CLIENT_SECRET = self.CLIENT_SECRET
        TOKEN_URL = self.TOKEN_URL


        dataset = {
            "type": "RRI",
            "data": ppi_samples,
            "analysis": {"type": "readiness"}
        }

        response = requests.post(
            url=TOKEN_URL,
            data='grant_type=client_credentials&client_id={}'.format(CLIENT_ID),
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            auth=(CLIENT_ID, CLIENT_SECRET)
        )
        response = response.json()  # Parse JSON response into a python dictionary
        access_token = response["access_token"]  # Parse access token

        response = requests.post(
            url="https://analysis.kubioscloud.com/v2/analytics/analyze",
            headers={
                "Authorization": "Bearer {}".format(access_token),
                # use access token to access your Kubios Cloud analysis session
                "X-Api-Key": APIKEY
            },
            json=dataset)  # dataset will be automatically converted to JSON by the urequests library
        response = response.json()
        responseInfo = " "
        if response['status'] == 'ok':
            res = response['analysis']
            rmssd_ms = round(res["rmssd_ms"], 1)
            sdnn_ms = round(res["sdnn_ms"], 1)
            sd1_ms = round(res["sd1_ms"], 1)
            sd2_ms = round(res["sd2_ms"], 1)
            sns_index = round(res["sns_index"], 3)
            pns_index = round(res["pns_index"], 3)
            responseInfo = {"rmssd": rmssd_ms,
                            "sdnn": sdnn_ms,
                            "sd1": sd1_ms,
                            "sd2": sd2_ms,
                            "sns": sns_index,
                            "pns": pns_index,
                            "ave_ppi": ave_ppi,
                            "ave_bpm": ave_bpm}

        elif response['status'] == 'error':
            if len(ppi_samples) < 10:
                print("points too less")
            pass

        return responseInfo


    def heartRate(self):
        self.calculateDataFromPPInterval(1)

    def heartRatePrase(self):
        self.calculateDataFromPPInterval(2)

    def kubios(self):
        self.calculateDataFromPPInterval(3)

    def showHistory(self):
        self.behindShowService.show_history()



