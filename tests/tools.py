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


def test_list_replacement_benefits():
    endpoint = "competitive-replacement/certificates"
    locale_url_header_org = locale_check()
    payload = {
            "domains": ["google.com", "amazon.com"]
            }
    
    response = make_request("POST",locale_url_header_org[0],endpoint, locale_url_header_org[1], payload)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "certificates" in response.text, "Key 'certificates' is missing in the response"
    assert "serial_number" in response.text, "Key 'serial_number' is missing in the response"
