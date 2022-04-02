import os

import requests
import pandas as pd


API_SERVER = os.getenv("API_SERVER", default="flask-api")
API_SERVER_PORT = int(os.getenv("API_SERVER_PORT", default=5000))

API_SERVER_URL_BASE = f"http://{API_SERVER}:{API_SERVER_PORT}/api/offers/nfj"
API_SERVER_URL_TEMPLATE = API_SERVER_URL_BASE + "?count={count_by}&sort={sort_order}"


def get_data_req(endpoint):
    try:
        r = requests.get(endpoint)
    except Exception as exc:
        print(f"{exc.__class__.__name__}: {exc}")
    else:
        if r.status_code != 200:
            print(f"Status code: {r.status_code}")
        else:
            try:
                data = r.json()
            except Exception as exc:
                print(f"{exc.__class__.__name__}: {exc}")
            else:        
                return data


def prepare(data):
    data = pd.DataFrame(data)
    data = data.rename(columns={"salary": "salary (PLN)"})
    data["seniority"] = data["seniority"].astype(str).apply(lambda x: x.rstrip("]").lstrip("[").replace(",", ", ").replace("'",""))
    data = data.fillna({"locations": "Remote"})
    data["locations"] = data["locations"].astype(str).apply(lambda x: x.rstrip("]").lstrip("[").replace(",", ", ").replace("'",""))     
    return data