from http.client import BAD_REQUEST
import json
import sys
from collections import namedtuple

from flask import Flask, render_template, abort
from flask_restful import Api, Resource
import redis

sys.path.append("..")


app = Flask(__name__)
api = Api(app)

redis_client = redis.Redis(host="redis-db", port=6379, db=0)


class JobOffer(Resource):
    
    def get(self, source="nfj", location=None):
        try:
            data = json.loads(redis_client.get(source))
        except TypeError as exc:
            abort(400, "Invalid data source.")
        else:
            if location is not None:
                data_for_location = [offer for offer in data if location in offer["location"]]
                return data_for_location
            else:
                return data


api.add_resource(JobOffer, "/api/offers", "/api/offers/<string:source>", "/api/offers/<string:source>/<string:location>")


class HTTPStatusCode:
    BAD_REQUEST = 400
    NOT_FOUND = 404
    SUCCESS = 200


@app.errorhandler(HTTPStatusCode.BAD_REQUEST)
def bad_request_error_handler(error):
    return render_template("error_page.html", error=error, title="400 Bad Request"), HTTPStatusCode.BAD_REQUEST


@app.errorhandler(HTTPStatusCode.NOT_FOUND)
def not_found_error_handler(error):
    return render_template("error_page.html", error=error, title="404 Not found"), HTTPStatusCode.NOT_FOUND


@app.route("/")
def homepage():
    return "<h1>Welcome to my website</h1>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)