#!/usr/bin/env python2
import time

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
    return flask.jsonify(state=state)


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
