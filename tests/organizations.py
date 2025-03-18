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


def test_list_orgs():
    endpoint = "organization"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "id" in response.text, "Key 'id' is missing in the response"
    assert "name" in response.text, "Key 'name' is missing in the response"


# ORG FUNCTIONS
def test_submit_new_org(shared_data):
    endpoint = "organization"
    payload = {
        "name": "Example Organization, LLC",
        "assumed_name": "Example Organization",
        "country": "us",
        "address": "ABC Movers",
        "address2": "Floor 08",
        "city": "Springfield",
        "state": "Virginia",
        "zip": "22162",
        "telephone": "555-555-0100",
        "organization_contact": {
            "first_name": "Jane",
            "last_name": "Doe",
            "job_title": "Manager",
            "email": "jane.doe@example.com",
            "telephone": "555-555-0100",
            "telephone_extension": "736"
        },
        "validations": [
          {
            "type": "ov"
          },
          {
            "type": "ev",
            "verified_users": [
              {
                "first_name": "John",
                "last_name": "Doe",
                "job_title": "Site Reliability Engineer",
                "telephone": "555-555-1001",
                "email": "john.doe@example.com"
              }
            ]
          }
        ]
    }

    response = make_request("POST", endpoint, payload)

    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 201
    assert "id" in response.text, "Key 'id' is missing in the response"
    shared_data["new_org_id"] = data["id"]


def test_org_info(shared_data):
    org_id = shared_data["new_org_id"]
    endpoint = f"organization/{org_id}"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "id" in response.text, "Key 'id' is missing in the response"
    assert "name" in response.text, "Key 'name' is missing in the response"


def test_deactivate_org(shared_data):
    organization_id = shared_data["new_org_id"]
    endpoint = f"organization/{organization_id}/deactivate"
    response = make_request("PUT", endpoint)
    assert response.status_code == 204


def test_activate_org(shared_data):
    organization_id = shared_data["new_org_id"]
    endpoint = f"organization/{organization_id}/activate"
    response = make_request("PUT", endpoint)
    assert response.status_code == 204


def test_org_validation_details(shared_data):
    organization_id = shared_data["new_org_id"]
    endpoint = f"organization/{organization_id}/validation"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "validations" in response.text, "Key 'validations' is missing in the response"
    assert "status" in response.text, "Key 'status' is missing in the response"


def test_delete_org(shared_data):
    organization_id = shared_data["new_org_id"]
    endpoint = f"organization/{organization_id}"
    response = make_request("DELETE", endpoint)
    assert response.status_code == 204
