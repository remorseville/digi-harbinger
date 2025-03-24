from dotenv import dotenv_values
import json
import os
from utils.sqlite_kv_store import kv_store
import requests


APP_DATA = os.getenv('LOCALAPPDATA')
APP_DIRECTORY = os.path.join(APP_DATA, "Digi-Harbinger")
ENV_FILE = os.path.join(APP_DIRECTORY, "env.json")
ENV_STORE = kv_store


def make_request(method, base_url, endpoint, headers, payload=None):
    url = f"{base_url}/{endpoint}"
    response = requests.request(method, url, headers=headers, json=payload)
    return response


def locale_check():
    mode = ENV_STORE.get("US_MODE")
    
    if mode == "true":
        base_url = ENV_STORE.get("DIGICERT_BASE_URL_US")
        api_key = ENV_STORE.get("DIGICERT_API_KEY_US")
    else:
        base_url = ENV_STORE.get("DIGICERT_BASE_URL_EU")
        api_key = ENV_STORE.get("DIGICERT_API_KEY_EU")
    headers = {
                "X-DC-DEVKEY": api_key,
                "Content-Type": "application/json"
            }
    org_id = ENV_STORE.get("ORG_ID")
    
    url_header = [base_url, headers, org_id]
    return url_header

# domain dcv testing
def test_list_domains():
    endpoint = "domain"
    locale_url_header_org = locale_check()
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "id" in response.text, "Key 'id' is missing in the response"
    assert "name" in response.text, "Key 'name' is missing in the response"


# submit new domain
def test_add_domain(shared_data):
    endpoint = "domain"
    locale_url_header_org = locale_check()
    payload = {
        "name": "delete.test.digicertsub.com",  # domain used _ currently not a var _ TODO
        "organization": {
            "id": locale_url_header_org[2],  # same with org_id TODO get the first org id
        },
        "validations": [
            {
                "type": "ov"
            }
        ],
        "dcv_method": "dns-txt-token"
    }

    locale_url_header_org = locale_check()
    response = make_request("POST",locale_url_header_org[0],endpoint, locale_url_header_org[1], payload)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 201
    assert "id" in response.text, "Key 'id' is missing in the response"
    assert "dcv_token" in response.text, "Key 'dcv_token' is missing in the response"
    shared_data["new_domain_id"] = data["id"]


def test_deactivate_domain(shared_data):
    domain_id = shared_data["new_domain_id"]
    endpoint = f"domain/{domain_id}/deactivate"
    locale_url_header_org = locale_check()
    response = make_request("PUT",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    assert response.status_code == 204


def test_activate_domain(shared_data):
    domain_id = shared_data["new_domain_id"]
    endpoint = f"domain/{domain_id}/activate"
    locale_url_header_org = locale_check()
    response = make_request("PUT",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    assert response.status_code == 204


def test_domain_info(shared_data):
    domain_id = shared_data["new_domain_id"]
    endpoint = f"domain/{domain_id}"
    locale_url_header_org = locale_check()
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200


def domain_change_dcv_method(shared_data, dcv_method):
    domain_id = shared_data["new_domain_id"]
    endpoint = f"domain/{domain_id}/dcv/method"
    payload = {
        "dcv_method": dcv_method
    }

    locale_url_header_org = locale_check()
    response = make_request("PUT",locale_url_header_org[0],endpoint, locale_url_header_org[1], payload)
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
    locale_url_header_org = locale_check()
    response = make_request("DELETE",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    assert response.status_code == 204
