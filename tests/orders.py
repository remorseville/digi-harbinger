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


def test_list_orders():
    locale_url_header_org = locale_check()

    endpoint = "order/certificate"
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200


def test_order_validation_status():
    order_id = 1193139621  # order needs to be pending 
    # TODO Convert this one where it finds a pending request? Maybe submit a pending request?
    endpoint = f"order/certificate/{order_id}/validation"
    locale_url_header_org = locale_check()
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200


# order functions
def ov_certificate(generate_keypair, ov_product_identifier):
    locale_url_header_org = locale_check()

    endpoint = f"order/certificate/{ov_product_identifier}"
    payload = {
        "certificate": {
            "common_name": "test.digicertsub.com",

            "csr": generate_keypair,
            "signature_hash": "sha256",
            "server_platform": {
                "id": 2
            }
        },
        "comments": "autobot testing",
        "organization": {
            "id": int(locale_url_header_org[2]),
        },
        "order_validity": {
            "years": 1
        },
        "payment_method": "balance",
        "dcv_method": "dns-txt-token"
    }

    response = make_request("POST",locale_url_header_org[0],endpoint, locale_url_header_org[1], payload)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))

    assert response.status_code == 201
    assert "id" in response.text, "Key 'id' is missing in the response"


def dv_certificate(generate_keypair, dv_product_identifier):
    endpoint = f"order/certificate/{dv_product_identifier}"
    payload = {
        "certificate": {
            "common_name": "autobot.inverted.space",

            "csr": generate_keypair,
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
        "dcv_method": "dns-txt-token"
    }

    locale_url_header = locale_check()
    response = make_request("POST",locale_url_header[0],endpoint, locale_url_header[1], payload)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 201
    assert "id" in response.text, "Key 'id' is missing in the response"
    assert "dcv_random_value" in response.text, "Key 'dcv_random_value' is missing in the response"


# ORDER TESTS
def test_ssl_dv_geotrust_flex(generate_keypair):
    dv_certificate(generate_keypair, "ssl_dv_geotrust_flex")


def test_ssl_dv_rapidssl(generate_keypair):
    dv_certificate(generate_keypair, "ssl_dv_rapidssl")


def test_ssl_basic(generate_keypair):
    ov_certificate(generate_keypair, "ssl_basic" )


def test_ssl_securesite_flex(generate_keypair):
    ov_certificate(generate_keypair, "ssl_securesite_flex")


def test_ssl_securesite_pro(generate_keypair):
    ov_certificate(generate_keypair, "ssl_securesite_pro")


def test_ssl_plus(generate_keypair):
    ov_certificate(generate_keypair, "ssl_plus")


def test_ssl_multi_domain(generate_keypair):
    ov_certificate(generate_keypair, "ssl_multi_domain")


def test_ssl_type_hint(generate_keypair):
    ov_certificate(generate_keypair, "ssl")


