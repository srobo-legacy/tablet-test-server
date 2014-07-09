#!/usr/bin/env python2
import time
import threading

import flask
import flask_sockets


app = flask.Flask(__name__, template_folder=".", static_folder=".",
                  static_url_path="")
app.config["DEBUG"] = True
sockets = flask_sockets.Sockets(app)
start_time = time.time()
mode = "dev"
zone = 0
state = "stopped"
log_list = []


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/settings/mode", methods=["GET", "PUT"])
def settings_mode():
    global mode
    if flask.request.method == "PUT":
        global log_list
        mode = flask.request.json["mode"]
        log_list.append("Changed mode to: {}".format(mode))
    return flask.jsonify(mode=mode)


@app.route("/settings/zone", methods=["GET", "PUT"])
def settings_zone():
    global zone
    if flask.request.method == "PUT":
        global log_list
        zone = flask.request.json["zone"]
        log_list.append("Changed zone to: {}".format(zone))
    return flask.jsonify(zone=zone)


@app.route("/battery")
def battery():
    global start_time
    level = 1 - ((time.time() - start_time) / 2000)
    return flask.jsonify(level=level)


@app.route("/log")
def log():
    global log_list
    return flask.jsonify(log="\n".join(log_list))


@app.route("/state")
def get_state():
    global state
    return flask.jsonify(state=state,
                         project=dict(name="myproject",
                                      version="dsahldha98r239hawoa"),
                         pyenv=dict(version="5"))


@app.route("/start")
def start():
    global state
    state = "booting"
    def set_later():
        global state
        time.sleep(10)
        state = "started"
    threading.Thread(target=set_later).start()
    return flask.jsonify()


@app.route("/stop")
def stop():
    global state
    state = "stopping"
    def set_later():
        global state
        time.sleep(10)
        state = "stopped"
    threading.Thread(target=set_later).start()
    return flask.jsonify()


@sockets.route("/ws/log")
def log_socket(ws):
    global log_list
    i = len(log_list)
    while True:
        if i < len(log_list):
            ws.send(log_list[i])
            i += 1
        time.sleep(1)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
