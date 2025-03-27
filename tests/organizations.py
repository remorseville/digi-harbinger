import json
import requests
import keyring

# Local file imports
from utils.sqlite_kv_store import kv_store


ENV_STORE = kv_store


def make_request(method, base_url, endpoint, headers, payload=None):
    url = f"{base_url}/{endpoint}"
    response = requests.request(method, url, headers=headers, json=payload)
    return response


def locale_check():
    mode = ENV_STORE.get("US_MODE")
    
    if mode == "true":
        base_url = ENV_STORE.get("DIGICERT_BASE_URL_US")
        api_key = keyring.get_password("digi-harbinger", "DIGICERT_API_KEY_US")
    else:
        base_url = ENV_STORE.get("DIGICERT_BASE_URL_EU")
        api_key = keyring.get_password("digi-harbinger", "DIGICERT_API_KEY_EU")
    headers = {
                "X-DC-DEVKEY": api_key,
                "Content-Type": "application/json"
            }
    org_id = ENV_STORE.get("ORG_ID")
    
    url_header = [base_url, headers, org_id]
    return url_header


def test_list_orgs():
    endpoint = "organization"
    locale_url_header_org = locale_check()
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "id" in response.text, "Key 'id' is missing in the response"
    assert "name" in response.text, "Key 'name' is missing in the response"


# org functions
def test_submit_new_org(shared_data):
    endpoint = "organization"
    payload = {
        "name": "Example Organization - 2, LLC",
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

    locale_url_header_org = locale_check()
    response = make_request("POST",locale_url_header_org[0],endpoint, locale_url_header_org[1], payload)

    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 201
    assert "id" in response.text, "Key 'id' is missing in the response"
    shared_data["new_org_id"] = data["id"]


def test_org_info(shared_data):
    org_id = shared_data["new_org_id"]
    endpoint = f"organization/{org_id}"
    locale_url_header_org = locale_check()
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "id" in response.text, "Key 'id' is missing in the response"
    assert "name" in response.text, "Key 'name' is missing in the response"


def test_deactivate_org(shared_data):
    organization_id = shared_data["new_org_id"]
    endpoint = f"organization/{organization_id}/deactivate"
    locale_url_header_org = locale_check()
    response = make_request("PUT",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    assert response.status_code == 204


def test_activate_org(shared_data):
    organization_id = shared_data["new_org_id"]
    endpoint = f"organization/{organization_id}/activate"
    locale_url_header_org = locale_check()
    response = make_request("PUT",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    assert response.status_code == 204


def test_org_validation_details(shared_data):
    organization_id = shared_data["new_org_id"]
    endpoint = f"organization/{organization_id}/validation"
    locale_url_header_org = locale_check()
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "validations" in response.text, "Key 'validations' is missing in the response"
    assert "status" in response.text, "Key 'status' is missing in the response"


def test_delete_org(shared_data):
    organization_id = shared_data["new_org_id"]
    endpoint = f"organization/{organization_id}"
    locale_url_header_org = locale_check()
    response = make_request("DELETE",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    assert response.status_code == 204
