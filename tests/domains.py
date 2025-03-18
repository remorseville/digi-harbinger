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


# DOMAIN DCV TESTING
def test_list_domains():
    endpoint = "domain"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "id" in response.text, "Key 'id' is missing in the response"
    assert "name" in response.text, "Key 'name' is missing in the response"


# SUBMIT NEW DOMAIN
def test_add_domain(shared_data):
    endpoint = "domain"
    payload = {
        "name": "delete.test.digicertsub.com",  # DOMAIN USED _ CURRENTLY NOT A VAR _ TODO
        "organization": {
            "id": 1903266,  # SAME WITH ORG_ID TODO GET THE FIRST ORG ID
        },
        "validations": [
            {
                "type": "ov"
            }
        ],
        "dcv_method": "dns-txt-token"
    }

    response = make_request("POST", endpoint, payload)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 201
    assert "id" in response.text, "Key 'id' is missing in the response"
    assert "dcv_token" in response.text, "Key 'dcv_token' is missing in the response"
    shared_data["new_domain_id"] = data["id"]


def test_deactivate_domain(shared_data):
    domain_id = shared_data["new_domain_id"]
    endpoint = f"domain/{domain_id}/deactivate"
    response = make_request("PUT", endpoint)
    assert response.status_code == 204


def test_activate_domain(shared_data):
    domain_id = shared_data["new_domain_id"]
    endpoint = f"domain/{domain_id}/activate"
    response = make_request("PUT", endpoint)
    assert response.status_code == 204


def test_domain_info(shared_data):
    domain_id = shared_data["new_domain_id"]
    endpoint = f"domain/{domain_id}"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200


def domain_change_dcv_method(shared_data, dcv_method):
    domain_id = shared_data["new_domain_id"]
    endpoint = f"domain/{domain_id}/dcv/method"
    payload = {
        "dcv_method": dcv_method
    }

    response = make_request("PUT", endpoint, payload)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "dcv_token" in response.text, "Key 'dcv_token' is missing in the response"
    assert "token" in response.text, "Key 'token' is missing in the response"


def test_domain_change_dcv_dns_txt_token(shared_data):
    domain_change_dcv_method(shared_data, "dns-txt-token")


def test_domain_change_dcv_cname(shared_data):
    domain_change_dcv_method(shared_data, "dns-cname-token")


def test_domain_change_dcv_http_token(shared_data):
    domain_change_dcv_method(shared_data, "http-token")


def test_delete_domain(shared_data):
    domain_id = shared_data["new_domain_id"]
    endpoint = f"domain/{domain_id}"
    response = make_request("DELETE", endpoint)
    assert response.status_code == 204
