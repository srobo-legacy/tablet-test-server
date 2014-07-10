#!/usr/bin/env python
import crochet; crochet.setup()
import flask

from autobahn.twisted import wamp


g = dict(zone=0)

################################################################################
wapp = wamp.Application()


@wapp.register("org.srobo.zone")
def wapp_get_zone():
    return g["zone"]


@wapp.subscribe("org.srobo.zone")
def wapp_sub_zone(zone):
    g["zone"] = zone


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


################################################################################
if __name__ == "__main__":
    @crochet.run_in_reactor
    def start_wamp():
        wapp.run("ws://0.0.0.0:9000", "srobo", standalone=True,
                 start_reactor=False)

    start_wamp()

    app.run(host="0.0.0.0", port=8000, debug=True)
