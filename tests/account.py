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



def test_account_details():
    endpoint = "account"
    locale_url_header_org = locale_check()
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200


def test_list_permissions():
    endpoint = "authorization"
    locale_url_header_org = locale_check()
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "authorizations" in response.text, "Key 'authorizations' is missing in the response"


def test_list_api_keys():
    endpoint = "key"
    locale_url_header_org = locale_check()
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200


def test_list_product_list():
    endpoint = "product"
    locale_url_header_org = locale_check()
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
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
    locale_url_header_org = locale_check()
    response = make_request("POST",locale_url_header_org[0],endpoint, locale_url_header_org[1], payload)

    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 201
    assert "id" in response.text, "Key 'id' is missing in the response"
    shared_data["new_user_id"] = data["id"]


def test_list_users():
    endpoint = "user"
    locale_url_header_org = locale_check()
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "users" in response.text, "Key 'users' is missing in the response"


def test_delete_user(shared_data):
    user_id = shared_data["new_user_id"]
    endpoint = f"user/{user_id}"
    locale_url_header_org = locale_check()
    response = make_request("DELETE",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    assert response.status_code == 204


def test_list_service_users():
    endpoint = "user/api-only"
    locale_url_header_org = locale_check()
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "users" in response.text, "Key 'users' is missing in the response"

