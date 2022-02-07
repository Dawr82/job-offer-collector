import json
import sys
from collections import Counter

from flask import Flask, render_template, abort
from flask_restful import Api, Resource, request
from marshmallow import Schema, validate, ValidationError, fields
import redis
import pymongo

sys.path.append("..")


app = Flask(__name__)
api = Api(app)

redis_client = redis.Redis(host="redis-db", port=6379, db=0)
mongo_client = pymongo.MongoClient("mongodb://root:root@mongo-db:27017/scraper?authSource=admin&retryWrites=true&w=majority")


class JobOfferFull(Resource):

    def count(count_by, data):
        counter = Counter()
        for offer in data:
            counter.update(offer.get(count_by))
        return dict(counter)
        
    
    def filter(filter_by, filter, data):
        try:
            filtered = [offer for offer in data if offer['filter_by'] == filter]
        except KeyError:
            return {"Exception": "KeyError", "Message": "Key not present"}
        else:
            return filtered


    def get(self, source="nfj"):  
        data = redis_client.get(source) 
        if data is None:
            collection = mongo_client["scraper"][source]
            data = list(collection.find())
            for offer in data:
                offer.pop("_id")
                offer.pop("insertionDate")
            redis_client.set(source, json.dumps(data, indent=4))
        else:
            data = json.loads(data)
        if request.args:
            get_keys = request.args.keys()
            for key in get_keys:
                if key != "count":
                    data = self.filter(key, request.args.get(key), data)
                    break
            if "count" in get_keys:
                data = self.count(get_keys.get('count'), data)
        return data


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