#!/usr/bin/env python
import flask
import flask_cors


app = flask.Flask(__name__)


@app.route("/custom_pages")
@flask_cors.cross_origin()
def custom_pages():
    return flask.jsonify(
        pages=[
            {
                "title": "My Custom Component",
                "name": "my-custom-component",
                "icon": "cubes",
                "url": "/static/elements/my-custom-components/index.html"
            }
        ]
    )


if __name__ == "__main__":
    app.run(port=10000, debug=True)
