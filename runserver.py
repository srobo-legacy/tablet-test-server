#!/usr/bin/env python3
import flask


app = flask.Flask(__name__, template_folder=".", static_folder=".", static_url_path="")


@app.route("/")
def index():
    return flask.render_template("index.html")


app.run(port=8000, debug=True)
