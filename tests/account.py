import requests
from dotenv import dotenv_values
import json
import os
import sys


# globals
APP_DATA = os.getenv('LOCALAPPDATA')
APP_DIRECTORY = os.path.join(APP_DATA, "Digi-Harbinger")
ENV_FILE = os.path.join(APP_DIRECTORY, ".env")
ENV_VARS = dotenv_values(ENV_FILE)


# dynamic path handling (packaged vs dev)
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# request helper function
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


def test_account_details():
    endpoint = "account"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200


def test_list_permissions():
    endpoint = "authorization"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "authorizations" in response.text, "Key 'authorizations' is missing in the response"


def test_list_api_keys():
    endpoint = "key"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200


def test_list_product_list():
    endpoint = "product"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "products" in response.text, "Key 'products' is missing in the response"


def test_add_user(shared_data):
    endpoint = "user"
    payload = {
        "first_name": "Super",
        "last_name": "Mario",
        "email": "super.mario@mushroom-kingdom.gov",
        "telephone": "555-555-5555",
        "job_title": "Plumber",
        "username": "TurtleSmasher",
        "access_roles": [
            {
                "id": 5
            }
        ]
    }
    response = make_request("POST", endpoint, payload)

    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 201
    assert "id" in response.text, "Key 'id' is missing in the response"
    shared_data["new_user_id"] = data["id"]


def test_list_users():
    endpoint = "user"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "users" in response.text, "Key 'users' is missing in the response"


def test_delete_user(shared_data):
    user_id = shared_data["new_user_id"]
    endpoint = f"user/{user_id}"
    response = make_request("DELETE", endpoint)
    assert response.status_code == 204


def test_list_service_users():
    endpoint = "user/api-only"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "users" in response.text, "Key 'users' is missing in the response"

