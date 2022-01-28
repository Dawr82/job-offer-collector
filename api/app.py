import json
import sys
from collections import namedtuple

from flask import Flask, render_template, abort
from flask_restful import Api, Resource
import redis
import pymongo
import bson

sys.path.append("..")


app = Flask(__name__)
api = Api(app)

redis_client = redis.Redis(host="redis-db", port=6379, db=0)
mongo_client = pymongo.MongoClient("mongodb://root:root@mongo-db:27017/scraper?authSource=admin&retryWrites=true&w=majority")

class JobOfferFull(Resource):

    def get(self, source="nfj"):
        # If the data is not present in redis cache, fetch it from MongoDB and save to redis.   
        data = redis_client.get(source) 
        if data is None:
            collection = mongo_client["scraper"][source]
            data = list(collection.find())
            for offer in data:
                offer.pop("_id")
            redis_client.set(source, json.dumps(data, indent=4))
            return data
        return json.loads(data)

api.add_resource(JobOfferFull, "/api/offers", "/api/offers/<string:source>")

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