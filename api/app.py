import json
import sys

from flask import Flask
from flask_restful import Api, Resource
import redis

sys.path.append("..")


app = Flask(__name__)
api = Api(app)

redis_client = redis.Redis(host="redis-db", port=6379, db=0)


class JobOffer(Resource):
    
    def get(self):
        return json.loads(redis_client.get("bdg"))


api.add_resource(JobOffer, "/api/offers")


@app.route("/")
def homepage():
    return "<h1>Welcome to my website</h1>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)