import json
import os
from collections import Counter

from flask import Flask
from flask_restful import Api, Resource, request
import redis
import pymongo

app = Flask(__name__)
api = Api(app)

REDIS_DB_HOSTNAME = os.getenv("REDIS_DB_HOSTNAME", default="redis")
REDIS_DB_PORT = int(os.getenv("REDIS_DB_PORT", default=6379))
REDIS_DB_DATABASE = os.getenv("REDIS_DB_DATABASE", default=0)

MONGO_DB_HOSTNAME = os.getenv("MONGO_DB_HOSTNAME", default="localhost")
MONGO_DB_USER = os.getenv("MONGO_DB_USER", default="root")
MONGO_DB_PASSWORD = os.getenv("MONGO_DB_PASSWORD", default="root")
MONGO_DB_PORT = os.getenv("MONGO_DB_PORT", default=27017)
MONGO_DB_JOB_OFFER_DATABASE = os.getenv("MONGO_DB_JOB_OFFER_DATABASE", default="scraper")

redis_client = redis.Redis(
    host=REDIS_DB_HOSTNAME, 
    port=REDIS_DB_PORT, 
    db=REDIS_DB_DATABASE)

mongo_conn_string = f"mongodb://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}\
@{MONGO_DB_HOSTNAME}:{MONGO_DB_PORT}/{MONGO_DB_JOB_OFFER_DATABASE}\
?authSource=admin&retryWrites=true&w=majority"

mongo_client = pymongo.MongoClient(mongo_conn_string)


class JobOfferFull(Resource):

    def count(self, count_by, data):
        counter = Counter()
        for offer in data:
            item = offer.get(count_by)
            if item is not None:
                if not isinstance(item, list):
                    counter.update([item])
                else:
                    counter.update(item)
        if not counter:
            return {"Exception": "ValueError", "Message": "Field not present"}
        return dict(counter)
        
    
    def filter(self, filter_by, filter, data):
        try:
            filtered = [offer for offer in data if offer[filter_by] == filter]
        except KeyError:
            return {"Exception": "KeyError", "Message": "Key not present"}
        else:
            return filtered

    
    def sort(self, order, data):
        if order == "asc":
            return dict(sorted(data.items(), key=lambda item: item[1]))
        else:
            return dict(sorted(data.items(), key=lambda item: item[1], reverse=True))


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
                if key not in ('count', 'sort'):
                    data = self.filter(key, request.args.get(key).lower().capitalize(), data)
                    break
            if "count" in get_keys:
                data = self.count(request.args.get('count').lower(), data)
                if "sort" in get_keys:
                    data = self.sort(request.args.get('sort').lower(), data)      
        return data


api.add_resource(JobOfferFull, "/api/offers", "/api/offers/<string:source>")

class HTTPStatusCode:
    BAD_REQUEST = 400
    NOT_FOUND = 404

@app.errorhandler(HTTPStatusCode.BAD_REQUEST)
def bad_request_error_handler(error):
    return {
        "statusCode": 400,
        "description": "Bad Request"
    }

@app.errorhandler(HTTPStatusCode.NOT_FOUND)
def not_found_error_handler(error):
    return {
        "statusCode": 404,
        "description": "Not Found"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)