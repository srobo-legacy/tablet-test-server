#!/usr/bin/env python
import flask
import flask_cors


class FlaskStaticCors(flask.Flask):
    @flask_cors.cross_origin()
    def send_static_file(self, filename):
        return super(FlaskStaticCors, self).send_static_file(filename)


app = FlaskStaticCors(__name__)


@app.route("/custom_pages")
@flask_cors.cross_origin()
def custom_pages_info():
    return flask.jsonify(
        pages=[
            {
                "title": "My Custom Component",
                "name": "my-custom-component",
                "icon": "cubes",
                "import_url": "/static/elements/my-custom-component/index.html",
                "element": "my-custom-component"
            }
        ]
    )


if __name__ == "__main__":
    app.run(port=10000, debug=True)
