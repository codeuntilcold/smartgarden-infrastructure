# smartgarden-infrastructure
Repo for the backend and iot gateway of Smart Garden

## Flask backend
We run a Flask backend to manage users, pulling and pushing data from and to Adafruit IO. This backend will manange user data and also update the frontend with latest data using publish/subscribe MQTT to Adafruit IO and SocketIO to frontend.

First install dependencies from `requirements.txt`:

```bash
pip install -c requirements.txt
```

then run Flask backend server:

```bash
$ python run.py
```

~~Any commit to `origin/develop` will automatically deploy this app to this~~ [Heroku Demo App](https://just-a-test-for-flask-backend.herokuapp.com/).

__NEWS__:
For Adafruit's `MQTTClient` to be able to broadcast from socketio, a Redis message queue must be configured. So this means you have to install Redis on your local machine. I'll try to host this on Heroku if I can.

On Ubuntu, just run
```bash
$ sudo apt install redis-server -y
$ redis-server
```

## IOT Gateway
This gateway will communicate with a Microbit board through COM ports, and package data from Microbit to a JSON and publish it to AdafruitIO server.

To run IOT Gateway:
```bash
$ cd python_IOT_Gateway
$ python run.py
```


