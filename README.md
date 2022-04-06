# smartgarden-infrastructure
Repo for the backend and iot gateway of Smart Garden

## Flask backend
We run a Flask backend to manage users, pulling and pushing data from and to Adafruit IO. This backend will manange user data and also update the frontend with latest data using publish/subscribe MQTT to Adafruit IO and SocketIO to frontend.

To run Flask backend:
```bash
~$ python run.py
```

## IOT Gateway
This gateway will communicate with a Microbit board through COM ports, and package data from Microbit to a JSON and publish it to AdafruitIO server.


