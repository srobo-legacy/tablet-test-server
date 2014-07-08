#!/usr/bin/env python3
import flask


app = flask.Flask(__name__, template_folder=".", static_folder=".",
                  static_url_path="")
mode = "dev"
zone = 0


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/settings/mode", methods=["GET", "PUT"])
def settings_mode():
    global mode
    if flask.request.method == "PUT":
        mode = flask.request.json["mode"]
    return flask.jsonify(mode=mode)


@app.route("/settings/zone", methods=["GET", "PUT"])
def settings_zone():
    global zone
    if flask.request.method == "PUT":
        zone = flask.request.json["zone"]
    return flask.jsonify(zone=zone)

app.run(port=8000, debug=True)
