import os
import requests
from dotenv import load_dotenv
import json

from bs4 import BeautifulSoup

# LOAD .env
load_dotenv()

# CONSTANTS
BASE_URL = os.getenv("DIGICERT_BASE_URL")
API_KEY = os.getenv("DIGICERT_API_KEY")
HEADERS = {
    "X-DC-DEVKEY": API_KEY,
    "Content-Type": "application/json"
}


def make_request(method, endpoint, payload=None):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.request(method, url, headers=HEADERS, json=payload)
    return response

def create_auth_key():
    endpoint = "account/auth-key"
    response = make_request("POST", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))



def dv_certificate():

    #csr ="-----BEGIN CERTIFICATE REQUEST-----MIICrTCCAZUCAQAwKjEQMA4GA1UECgwHVGVzdGluZzEWMBQGA1UEAwwNdGVzdGluZy5sb2NhbDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKI+aTkG4a6lmdQPijXYohBovKoJJiKIsaF/Q+eTty5qP/HSYpXYHMxoPUUjOgvzbnaWBabB5LtTQtYyAmpHXXX5WpIKwyQNE2CWsWf5HLCQHuil7bdzv+tn0H4L3O0tivGcEd1UW01wAL8p9cv9yAJqgYB7sPMu+a7F6u5jvAIcYyftt+ISgx9bOxhtge50wuzFVRb7n3FiUA5fGuOBbYI15voMWcUMna+ODVVnPmMQtc1QgVgTxA0c7l90nxlCOzojd8IrXRna5oQlAIu3u5y2sjqlZ6mBSE0qd1RFEiDjheKGNXRjJxPAxeU8KaXMAXyRe0/i4sQBGbAPXS2e+XsCAwEAAaA+MDwGCSqGSIb3DQEJDjEvMC0wKwYDVR0RBCQwIoINdGVzdGluZy5sb2NhbIIRd3d3LnRlc3RpbmcubG9jYWwwDQYJKoZIhvcNAQELBQADggEBAGYsJqPyIywI4Uif2hJOgueyMGxswYIGE8Gn4Url/Ke8CeKMAeztNe4iR9LkEktOnde0/6259cc7mVzROTotqYVbgKov8yWhPAn8IIctPyfXM+6hiOQ1Vy+Db5Hdoml94FHhxMSpPkVciOXQ6swKO/HTIU3/23eCKCla/PgtucE8z4Ms4r2tPL15sSUr7RVH2OloTSrGKaBvDazzyr3V+1bLl5DBSja3ISGybjyOWza2mIu1mypXiKwyTv3i44tx59WEKhBX9PcMEKXdrJADbPhBzUaok3Q8BAsCvc8cDPCdY0FR3hexHqmH69Zao0WuD+KdVvfe00VeBhxcC/Ou/Ws=-----END CERTIFICATE REQUEST-----"
    csr = "-----BEGIN CERTIFICATE REQUEST-----MIICfDCCAWQCAQAwGzEZMBcGA1UEAxMQdGVzdC5zbG10ZXN0Lnh5ejCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALISBsBAy9/LTq0E6/v+0bUdL+MZp7RpgxjGXIuEtK2+1DHcoR/QagGW5vvZciwEF2pok8KoOsFfc3rdTYMsvCyoifM+pr1kCTUvBChozSndIsLI6e/VJ50UTxnmWnwu2cfLaDRGk5wvZzSqDkU/cDdPj9mYbzxBDiz74NaJSu7vUSO9Q+dewZRZfzA3MY5/8sID2qF4NIvS/QlmKycLkVu7GFDfMbvr5VGyqbCsNFpsRjzJ2PWN/Rc+5SWd8KKWo5ofFfzZeubZPKK8ZIGsdQmt+ZgB+MnNQDH7tIChgCffBzbIm6fZ9TlbPER/LqQ59/LJZ8VlsuCgi+2FkDIX7mECAwEAAaAcMBoGCSqGSIb3DQEJDjENMAswCQYDVR0TBAIwADANBgkqhkiG9w0BAQsFAAOCAQEAakt+J0ysyJDeo6d8FfOQEyElnOw9L2PNm3mWRyu/nBaFg6LgKY7jXsjcO25bw1dYGxO638ze/IEhMKUBu3WB009juKr08hxaDVyktD9DzAUpudbxcdU6wKy5l7Fun3305lY7bEM+RWi3lLxC4T+EbF8Onkx0bXRDqVKEGw46ylC7yCJ3+IpFBwBnjC+UNlhzP0cfV1jB/5rd+FmcfulZE3ebJBL8zoNqTwR8B5Rk9QGm2g5es/836QoVpswfwl0GsN7cvuRzfxtZyyUMk/R3tkuJk4ltT48zlGILMWxAmh29TSXaQIQs8Qgu1JWs+V1x8HvYSpP1jWxcS8bIHFUrZA==-----END CERTIFICATE REQUEST-----"
    endpoint = f"order/certificate/ssl_dv_geotrust"
    payload = {
        "certificate": {
            "common_name": "inverted.space",

            "csr": csr,
            "signature_hash": "sha256",
            "server_platform": {
                "id": 2
            }
        },
        "comments": "autobot testing",

        "order_validity": {
            "years": 1
        },
        "payment_method": "balance",
        "dcv_method": "dns-txt-token",
        "use_auth_key": "true",
    }

    response = make_request("POST", endpoint, payload)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))


def list_orders():
    endpoint = "order/certificate"
    response = make_request("GET", endpoint)

    data = response.json()["orders"]

    for orders in data:
        order = json.dumps(orders)
        certificate = json.loads(order)
        x = certificate["certificate"]
        my_id = certificate["id"]
        status = certificate["status"]

        for key, value in x.items():
            if value == "autobot.digicertsub.com" and status == "issued":
                print(my_id, value)
                endpoint = f"order/certificate/{my_id}/revoke"
                payload = {
                  "skip_approval": "true"
                }
                response2 = make_request("PUT", endpoint, payload)
                print(response2.text)
            elif value == "autobot.digicertsub.com" and status == "pending":
                print(my_id, value)
                endpoint = f"order/certificate/{my_id}/status"
                payload = {
                    "status": "canceled",
                    "note": "Testing."
                }
                response2 = make_request("PUT", endpoint, payload)
                print(response2.text)



def trial():
    import requests
    from bs4 import BeautifulSoup

    url = 'https://www.digicert.com/api/check-host.php'
    data = {"host": "inverted.space"}
    response = requests.post(url, data=data)
    print(response.text)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find('div', {'id': 'CertDetails'})  # Replace with the actual results container
        if results:
            print("Form submission successful! Results:")
            print(results.text)
        else:
            print("Form submission successful, but no results found.")
    else:
        print(f"Form submission failed with status code: {response.status_code}")


if __name__ == "__main__":
    #list_orders()
    #create_auth_key()
    #dv_certificate()
    trial()
