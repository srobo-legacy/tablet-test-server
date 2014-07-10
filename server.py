#!/usr/bin/env python
import crochet; crochet.setup()
import flask
import twisted.internet
from autobahn.twisted import wamp


g = dict(zone=0, mode="dev", level=1, log=[], state="stopped")

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


def sleep(delay):
    d = twisted.internet.defer.Deferred()
    twisted.internet.reactor.callLater(delay, d.callback, None)
    return d


@wapp.register("org.srobo.start")
def wrap_start():
    g["state"] = "booting"
    wapp.session.publish("org.srobo.state", "booting")
    yield sleep(5)
    g["state"] = "started"
    wapp.session.publish("org.srobo.state", "started")


@wapp.register("org.srobo.stop")
def wrap_start():
    g["state"] = "stopping"
    wapp.session.publish("org.srobo.state", "stopping")
    yield sleep(5)
    g["state"] = "stopped"
    wapp.session.publish("org.srobo.state", "stopped")


@wapp.register("org.srobo.state")
def wapp_get_state():
    return g["state"]


################################################################################
app = flask.Flask(__name__, template_folder=".", static_folder=".",
                  static_url_path="")
app.config["DEBUG"] = True


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/settings/zone")
def app_get_zone():
    @crochet.wait_for(timeout=1)
    def call_get_zone():
        return wapp.session.call("org.srobo.zone")

    return flask.jsonify(zone=call_get_zone())


@app.route("/settings/mode")
def app_get_mode():
    @crochet.wait_for(timeout=1)
    def call_get_mode():
        return wapp.session.call("org.srobo.mode")

    return flask.jsonify(mode=call_get_mode())


@app.route("/log")
def app_get_log():
    @crochet.wait_for(timeout=1)
    def call_get_log():
        return wapp.session.call("org.srobo.log")

    return flask.jsonify(log=call_get_log())


@app.route("/battery")
def app_get_battery():
    return flask.jsonify(level=g["level"])


################################################################################
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    @crochet.run_in_reactor
    def start_wamp():
        wapp.run("ws://0.0.0.0:9000", "srobo", standalone=True,
                 start_reactor=False)

        def publish_battery():
            g["level"] -= 0.001
            wapp.session.publish("org.srobo.battery.level", g["level"])

        l = twisted.internet.task.LoopingCall(publish_battery)
        l.start(1, now=False)

    start_wamp()

    app.run(host="0.0.0.0", port=8000, debug=True)
