import requests
import keyring

# Local file imports
from utils.sqlite_kv_store import kv_store


ENV_STORE = kv_store


def make_request(method, base_url, endpoint, headers, payload=None):
    url = f"{base_url}/{endpoint}"
    response = requests.request(method, url, headers=headers, json=payload)
    return response


def env_prep():
    
    base_url = ENV_STORE.get("CIS_BASE_URL")
    api_key = keyring.get_password("digi-harbinger", "CIS_API_KEY")

    headers = {
                "X-DC-DEVKEY": api_key,
                "Content-Type": "application/json"
            }
    
    url_header = [base_url, headers]
    return url_header



def test_issuance_heartbeat():
    endpoint = "cis/health/heartbeat"
    url_header = env_prep()
    base_url = url_header[0]
    header = url_header[1]
    response = make_request("GET",base_url ,endpoint, header)
    assert response.status_code == 204


def test_get_profiles():
    endpoint = "cis/profile"
    url_header = env_prep()
    base_url = url_header[0]
    header = url_header[1]
    response = make_request("GET",base_url ,endpoint, header)
    print(response.text)
    assert response.status_code == 200