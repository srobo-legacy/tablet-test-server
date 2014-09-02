#!/usr/bin/env python
from __future__ import print_function

import base64
import functools
import random
import os

import flask
import crochet; crochet.setup()
import twisted.internet
from autobahn import util
from autobahn.wamp import message
from autobahn.twisted import wamp
from autobahn.wamp.types import ComponentConfig
from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks
from autobahn.websocket.protocol import parseWsUrl
from autobahn.twisted.websocket import WampWebSocketClientFactory, \
                                       WampWebSocketServerFactory


g = {
    "zone": 0,
    "mode": "dev",
    "battery": {"level": 1},
    "logs": [
        {"type": "current", "name": "current", "title": "Current", "contents": []},
        {"type": "old", "name": "old_1", "title": "#1", "contents": ["This is an old log."]},
        {"type": "old", "name": "old_2", "title": "#2", "contents": ["This is another", "old log."]},
        {"type": "old", "name": "old_3", "title": "#3", "contents": ["Cats."]},
    ],
    "state": "stopped",
    "pyenv": {"version": 1},
    "project": {
        "name": "my project",
        "version": "2ae01472317d1935a84797ec1983ae243fc6aa28"
    },
    "power_outputs": [
        {"state": False},
        {"state": False},
        {"state": False},
        {"state": False},
        {"state": False},
        {"state": False}
    ],
    "servo_boards": {
        "abcde": {
            "servos": [
                {"value": 50},
                {"value": 50},
                {"value": 50},
                {"value": 50},
                {"value": 50},
                {"value": 50},
                {"value": 50},
                {"value": 50},
                {"value": 50},
                {"value": 50},
                {"value": 50},
                {"value": 50}
            ]
        }
    },
    "motor_boards": {
        "abcde": {
            "motors": [{"value": 0}, {"value": 0}]
        },
        "fghij": {
            "motors": [{"value": 0}, {"value": 0}]
        }
    },
    "ruggeduinos": {
        "abcde": {
            "pins": [
                {"mode": "input", "value": False, "type": "digital"},
                {"mode": "input", "value": False, "type": "digital"},
                {"mode": "input", "value": False, "type": "digital"},
                {"mode": "input", "value": False, "type": "digital"},
                {"mode": "input", "value": False, "type": "digital"},
                {"mode": "input", "value": False, "type": "digital"},
                {"mode": "input", "value": False, "type": "digital"},
                {"mode": "input", "value": False, "type": "digital"},
                {"mode": "input", "value": False, "type": "digital"},
                {"mode": "input", "value": False, "type": "digital"},
                {"mode": "input", "value": False, "type": "digital"},
                {"mode": "input", "value": False, "type": "digital"},
                {"mode": "input", "value": 0, "type": "analogue"},
                {"mode": "input", "value": 0, "type": "analogue"},
                {"mode": "input", "value": 0, "type": "analogue"},
                {"mode": "input", "value": 0, "type": "analogue"},
                {"mode": "input", "value": 0, "type": "analogue"},
                {"mode": "input", "value": 0, "type": "analogue"}
            ]
        }
    }
}


################################################################################
class MyComponent(wamp.ApplicationSession):
    @inlineCallbacks
    def onJoin(self, details):
        print(details)
        yield self.subscribe(self.wapp_hello, "org.srobo.hello")
        yield self.register(self.wapp_get_zone, "org.srobo.zone")
        yield self.subscribe(self.wapp_sub_zone, "org.srobo.zone")
        yield self.register(self.wapp_get_mode, "org.srobo.mode")
        yield self.subscribe(self.wapp_sub_mode, "org.srobo.mode")
        yield self.subscribe(self.wapp_sub_log, "org.srobo.logs.append")
        yield self.register(self.wapp_logs_all, "org.srobo.logs.all")
        yield self.register(self.wapp_logs_get, "org.srobo.logs.get")
        yield self.register(self.wapp_start, "org.srobo.start")
        yield self.register(self.wapp_stop, "org.srobo.stop")
        yield self.register(self.wapp_get_state, "org.srobo.state")
        yield self.register(self.wapp_get_pyenv_version, "org.srobo.pyenv.version")
        yield self.register(self.wapp_get_project_name, "org.srobo.project.name")
        yield self.register(self.wapp_get_project_version, "org.srobo.project.version")
        yield self.subscribe(self.wapp_power_output_state, "org.srobo.power.output_state")
        yield self.register(self.wapp_power_get_output_state, "org.srobo.power.get_output_state")
        yield self.subscribe(self.wapp_servos_servo_value, "org.srobo.servos.servo_value")
        yield self.register(self.wapp_servos_get_servo, "org.srobo.servos.get_servo")
        yield self.register(self.wapp_servos_get_board, "org.srobo.servos.get_board")
        yield self.register(self.wapp_servos_all_boards, "org.srobo.servos.all_boards")
        yield self.subscribe(self.wapp_motors_motor_value, "org.srobo.motors.motor_value")
        yield self.register(self.wapp_motors_get_motor, "org.srobo.motors.get_motor")
        yield self.register(self.wapp_motors_get_board, "org.srobo.motors.get_board")
        yield self.register(self.wapp_motors_all_boards, "org.srobo.motors.all_boards")
        yield self.subscribe(self.wapp_ruggeduinos_pin_mode, "org.srobo.ruggeduinos.pin_mode")
        yield self.subscribe(self.wapp_ruggeduinos_pin_value, "org.srobo.ruggeduinos.pin_value")
        yield self.register(self.wapp_ruggeduinos_get_pin, "org.srobo.ruggeduinos.get_pin")
        yield self.register(self.wapp_ruggeduinos_get_board, "org.srobo.ruggeduinos.get_board")
        yield self.register(self.wapp_ruggeduinos_all_boards, "org.srobo.ruggeduinos.all_boards")

        temp_images = os.listdir("temp_images")
        while True:
            src = "/temp_images/{}".format(random.choice(temp_images))
            markers = []
            for i in range(5):
                x = random.randint(0, 1500)
                y = random.randint(0, 1500)
                size = random.randint(200, 500)
                m = functools.partial(random.randint, 0, 50)
                markers.append({
                    "code": i,
                    "distance": random.randint(25, 300) / 100.0,
                    "vertices": [
                        (x + m(), y + m()),
                        (x + m() + size + m(), y + m()),
                        (x + m() + size, y + m() + size),
                        (x + m(), y + m() + size)
                    ]
                })
            self.publish("org.srobo.camera.image", src, markers)
            yield sleep(10)

    def find_log(self, name):
        for log in g["logs"]:
            if log["name"] == name:
                return log

    def log(self, msg):
        line_no = len(self.find_log("current")["contents"])
        self.publish("org.srobo.logs.append", "current", msg, line_no)
        self.find_log("current")["contents"].append(msg)

    def wapp_hello(self, client_version):
        compatible = False if random.randint(0, 10) == 0 else True
        return {"compatible": compatible}

    def wapp_get_zone(self):
        return g["zone"]

    def wapp_sub_zone(self, zone):
        self.log("Zone changed to: {}".format(zone))
        g["zone"] = zone

    def wapp_get_mode(self):
        return g["mode"]

    def wapp_sub_mode(self, mode):
        self.log("Mode changed to: {}".format(mode))
        g["mode"] = mode

    def wapp_sub_log(self, log, text):
        self.find_log(log)["contents"].append(log)

    def wapp_logs_all(self):
        return g["logs"]

    def wapp_logs_get(self, name):
        return self.find_log(name)

    @inlineCallbacks
    def wapp_start(self):
        self.publish("org.srobo.project.name", g["project"]["name"])
        self.publish("org.srobo.project.version", g["project"]["version"])
        self.publish("org.srobo.pyenv.version", g["pyenv"]["version"])

        g["state"] = "booting"
        self.publish("org.srobo.state", "booting")
        yield sleep(5)
        g["state"] = "started"
        self.publish("org.srobo.state", "started")

        self.log("User code started.")

    @inlineCallbacks
    def wapp_stop(self):
        g["state"] = "stopping"
        self.publish("org.srobo.state", "stopping")
        yield sleep(5)
        g["state"] = "stopped"
        self.publish("org.srobo.state", "stopped")

        self.log("User code stopped.")

    def wapp_get_state(self):
        return g["state"]

    def wapp_get_pyenv_version(self):
        return g["pyenv"]["version"]

    def wapp_get_project_name(self):
        return g["project"]["name"]

    def wapp_get_project_version(self):
        return g["project"]["version"]

    def wapp_power_output_state(self, index, state):
        g["power_outputs"][index]["state"] = state

    def wapp_power_get_output_state(self, index):
        return g["power_outputs"][index]["state"]

    def wapp_servos_servo_value(self, board, index, value):
        g["servo_boards"][board]["servos"][index]["value"] = value

    def wapp_servos_get_servo(self, board, index):
        return g["servo_boards"][board]["servos"][index]

    def wapp_servos_get_board(self, serial_number):
        return g["servo_boards"][serial_number]

    def wapp_servos_all_boards(self):
        return g["servo_boards"]

    def wapp_motors_motor_value(self, board, index, value):
        g["motor_boards"][board]["motors"][index]["value"] = value

    def wapp_motors_get_motor(self, board, index):
        return g["motor_boards"][board]["motors"][index]

    def wapp_motors_get_board(self, serial_number):
        return g["motor_boards"][serial_number]

    def wapp_motors_all_boards(self):
        return g["motor_boards"]

    def wapp_ruggeduinos_pin_mode(self, board, index, mode):
        g["ruggeduinos"][board]["pins"][index]["mode"] = mode

    def wapp_ruggeduinos_pin_value(self, board, index, value):
        g["ruggeduinos"][board]["pins"][index]["value"] = value

    def wapp_ruggeduinos_get_pin(self, board, index):
        return g["ruggeduinos"][board]["pins"][index]

    def wapp_ruggeduinos_get_board(self, serial_number):
        return g["ruggeduinos"][serial_number]

    def wapp_ruggeduinos_all_boards(self):
        return g["ruggeduinos"]


################################################################################
app = flask.Flask(__name__, template_folder=".", static_folder=".",
                  static_url_path="")


@app.after_request
def add_header(response):
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    return response


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/settings/zone")
def app_get_zone():
    return flask.jsonify(zone=g["zone"])


@app.route("/settings/mode")
def app_get_mode():
    return flask.jsonify(zone=g["mode"])


@app.route("/logs/current")
def app_get_current_log():
    return flask.jsonify(log="\n".join(g["logs"]["current"]))


################################################################################
if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    @crochet.run_in_reactor
    def start_wamp():
        runner = wamp.ApplicationRunner(url="ws://0.0.0.0:9000", realm="srobo",
                                        standalone=True)
        runner.run(MyComponent, start_reactor=False)

    start_wamp()

    app.run(host="0.0.0.0", port=8000)
