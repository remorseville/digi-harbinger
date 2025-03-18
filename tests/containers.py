import requests
from dotenv import dotenv_values
import json
import os
import sys


# GLOBALS
APP_DATA = os.getenv('LOCALAPPDATA')
APP_DIRECTORY = os.path.join(APP_DATA, "Digi-Harbinger")
ENV_FILE = os.path.join(APP_DIRECTORY, ".env")
ENV_VARS = dotenv_values(ENV_FILE)


# DYNAMIC PATH HANDLING (PACKAGED VS DEV)
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# REQUEST HELPER FUNCTION
def make_request(method, endpoint, payload=None):
    if ENV_VARS["US_MODE"] == "true":
        base_url = ENV_VARS["DIGICERT_BASE_URL_US"]
        api_key = ENV_VARS["DIGICERT_API_KEY_US"]

    else:
        base_url = ENV_VARS["DIGICERT_BASE_URL_EU"]
        api_key = ENV_VARS["DIGICERT_API_KEY_EU"]

    headers = {
        "X-DC-DEVKEY": api_key,
        "Content-Type": "application/json"
    }

    url = f"{base_url}/{endpoint}"
    response = requests.request(method, url, headers=headers, json=payload)
    return response


def test_list_containers(shared_data):
    endpoint = "container"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "containers" in response.text, "Key 'containers' is missing in the response"
    assert "id" in response.text, "Key 'id' is missing in the response"
    shared_data["account_division_id"] = data["containers"][0]["id"]  # GETS DEFAULT ACCOUNT DIVISION


def test_container_info(shared_data):
    account_division_id = shared_data["account_division_id"]
    endpoint = f"container{account_division_id}"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "id" in response.text, "Key 'id' is missing in the response"
    assert "public_id" in response.text, "Key 'public_id' is missing in the response"


