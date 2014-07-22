#!/usr/bin/env python
import base64
import flask
import crochet; crochet.setup()
import twisted.internet
import random
import os
from autobahn.twisted import wamp


g = dict(zone=0,
         mode="dev",
         battery=dict(level=1),
         log=[],
         old_logs=[
             "This is an old log.",
             "This is another\nold log.",
             "Cats."
         ],
         state="stopped",
         pyenv=dict(version=1),
         project=dict(name="my project", version="2ae01472317d1935a84797ec1983ae243fc6aa28"),
         servo_boards=[
             dict(
                 serial_number="abc",
                 servos=[
                     dict(value=50),
                     dict(value=50),
                     dict(value=50),
                     dict(value=50),
                     dict(value=50),
                     dict(value=50),
                     dict(value=50),
                     dict(value=50)
                 ]
             ),
             dict(
                 serial_number="def",
                 servos=[
                     dict(value=50),
                     dict(value=50),
                     dict(value=50),
                     dict(value=50),
                     dict(value=50),
                     dict(value=50),
                     dict(value=50),
                     dict(value=50),
                     dict(value=50),
                     dict(value=50)
                 ]
             ),
             dict(
                 serial_number="ghi",
                 servos=[
                     dict(value=50),
                     dict(value=50),
                     dict(value=50),
                     dict(value=50)
                 ]
             )
         ],
         motor_boards={
             "abcde": {
                 "motors": [{"value": 0}, {"value": 0}]
             },
             "fghij": {
                 "motors": [{"value": 0}]
             },
             "klmno": {
                 "motors": [{"value": 0}, {"value": 0}, {"value": 0}]
             },
         },
         ruggeduinos=[
             dict(
                 serial_number="abc",
                 pins=[
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=0, type="analogue"),
                     dict(mode=None, value=0, type="analogue"),
                     dict(mode=None, value=0, type="analogue"),
                     dict(mode=None, value=0, type="analogue"),
                     dict(mode=None, value=0, type="analogue"),
                     dict(mode=None, value=0, type="analogue"),
                 ]
             ),
             dict(
                 serial_number="def",
                 pins=[
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=0, type="analogue"),
                     dict(mode=None, value=0, type="analogue"),
                 ]
             ),
             dict(
                 serial_number="ghi",
                 pins=[
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=False, type="digital"),
                     dict(mode=None, value=0, type="analogue"),
                     dict(mode=None, value=0, type="analogue"),
                     dict(mode=None, value=0, type="analogue"),
                     dict(mode=None, value=0, type="analogue"),
                     dict(mode=None, value=0, type="analogue"),
                     dict(mode=None, value=0, type="analogue"),
                 ]
             )
         ])


################################################################################
wapp = wamp.Application()


def log(m):
    wapp.session.publish("org.srobo.log", m)
    g["log"].append(m)


@wapp.register("org.srobo.zone")
def wapp_get_zone():
    return g["zone"]


@wapp.subscribe("org.srobo.zone")
def wapp_sub_zone(zone):
    log("Zone changed to: {}".format(zone))
    g["zone"] = zone


@wapp.register("org.srobo.mode")
def wapp_get_mode():
    return g["mode"]


@wapp.subscribe("org.srobo.mode")
def wapp_sub_mode(mode):
    log("Mode changed to: {}".format(mode))
    g["mode"] = mode


@wapp.subscribe("org.srobo.log")
def wrap_sub_log(log):
    g["log"].append(log)


@wapp.register("org.srobo.log")
def wapp_get_log():
    return "\n".join(g["log"])


@wapp.register("org.srobo.old_logs")
def wapp_get_old_logs():
    return g["old_logs"]


def sleep(delay):
    d = twisted.internet.defer.Deferred()
    twisted.internet.reactor.callLater(delay, d.callback, None)
    return d


@wapp.register("org.srobo.start")
def wrap_start():
    wapp.session.publish("org.srobo.project.name", g["project"]["name"])
    wapp.session.publish("org.srobo.project.version", g["project"]["version"])
    wapp.session.publish("org.srobo.pyenv.version", g["pyenv"]["version"])

    g["state"] = "booting"
    wapp.session.publish("org.srobo.state", "booting")
    yield sleep(5)
    g["state"] = "started"
    wapp.session.publish("org.srobo.state", "started")

    log("Robot started.")


@wapp.register("org.srobo.stop")
def wrap_start():
    g["state"] = "stopping"
    wapp.session.publish("org.srobo.state", "stopping")
    yield sleep(5)
    g["state"] = "stopped"
    wapp.session.publish("org.srobo.state", "stopped")

    log("Robot stopped.")


@wapp.register("org.srobo.state")
def wapp_get_state():
    return g["state"]


@wapp.register("org.srobo.pyenv.version")
def wapp_get_pyenv_version():
    return g["pyenv"]["version"]


@wapp.register("org.srobo.project.name")
def wapp_get_project_name():
    return g["project"]["name"]


@wapp.register("org.srobo.project.version")
def wapp_get_project_version():
    return g["project"]["version"]


@wapp.subscribe("org.srobo.servo.value")
def wapp_sub_mode(board, index, value):
    g["servo_boards"][board]["servos"][index]["value"] = value


@wapp.register("org.srobo.servo")
def wapp_get_servo(board, index):
    return g["servo_boards"][board]["servos"][index]


@wapp.register("org.srobo.servo_boards")
def wapp_get_servos():
    return g["servo_boards"]


@wapp.subscribe("org.srobo.motors.motor_value")
def wapp_motors_motor_value(board, index, value):
    g["motor_boards"][board]["motors"][index]["value"] = value


@wapp.register("org.srobo.motors.get_motor")
def wapp_motors_get_motor(board, index):
    return g["motor_boards"][board]["motors"][index]


@wapp.register("org.srobo.motors.get_board")
def wapp_motors_get_board(serial_number):
    return g["motor_boards"][serial_number]


@wapp.register("org.srobo.motors.all_boards")
def wapp_motors_all_boards():
    return g["motor_boards"]


@wapp.register("org.srobo.ruggeduinos")
def wapp_get_motors():
    return g["ruggeduinos"]


@wapp.subscribe("org.srobo.io.mode")
def wapp_io_mode(board, pin, mode):
    g["ruggeduinos"][board]["pins"][pin]["mode"] = mode


@wapp.subscribe("org.srobo.io.value")
def wapp_io_value(board, pin, value):
    g["ruggeduinos"][board]["pins"][pin]["value"] = value


@wapp.register("org.srobo.io.pin")
def wapp_get_io_pin(board, pin):
    return g["ruggeduinos"][board]["pins"][pin]


@wapp.register("org.srobo.battery")
def wapp_get_battery():
    return g["battery"]


@wapp.register("org.srobo.battery.level")
def wapp_get_battery_level():
    return g["battery"]["level"]


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


@app.route("/log")
def app_get_log():
    return flask.jsonify(log="\n".join(g["log"]))


@app.route("/battery")
def app_get_battery():
    return flask.jsonify(battery=g["battery"])


@app.route("/battery/level")
def app_get_battery_level():
    return flask.jsonify(level=g["battery"]["level"])


################################################################################
if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    @crochet.run_in_reactor
    def start_wamp():
        wapp.run("ws://0.0.0.0:9000", "srobo", standalone=True,
                 start_reactor=False)

    start_wamp()

    def publish_battery():
        if g["battery"]["level"] > 0:
            g["battery"]["level"] -= 0.001
            wapp.session.publish("org.srobo.battery.level", g["battery"]["level"])
    l1 = twisted.internet.task.LoopingCall(publish_battery)
    l1.start(1, now=False)

    temp_images = os.listdir("temp_images")
    def publish_camera():
        src = "/temp_images/{}".format(random.choice(temp_images))
        wapp.session.publish("org.srobo.camera.image", src)
    l2 = twisted.internet.task.LoopingCall(publish_camera)
    l2.start(10, now=False)

    app.run(host="0.0.0.0", port=8000)
