## Description
the project is used to measure and parse heart rate and generate data for the server.

## how to use it?
1. download file from git link 
2. use any editor that can open PY file(recommended Thonny) to open it and depend following information to change the configuration.
3. Change corresponding to SSID and PASSWORD OF WIFI IN ConnectWifi.py
4. Change corresponding to mqtt_topic and BROKER_IP OF MQTT IN BehindShowService.py
5. Change corresponding to APIKEY, CLIENT_ID, CLIENT_SECRET and TOKEN_URL in CalculateBehindService.py
6. run install.cmd
7. connect pico to computer again
8. wait for it to connect to wifi, and depend on the menu that is shown to use it.




tips1: only "2. HRV ANALYSIS" will send data to the MQTT server
tips2: history only save the latest 5 data

## If you meet these problems
1. stay on the start page for an as long time, do not worry, it just does not connect to your wifi, check wifi configuration and charge again.




