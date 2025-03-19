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


def test_list_orders():
    endpoint = "order/certificate"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200


def test_order_validation_status():
    order_id = 1193139621  # order needs to be pending 
    # TODO Convert this one where it finds a pending request? Maybe submit a pending request?
    endpoint = f"order/certificate/{order_id}/validation"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200


# order functions
def ov_certificate(generate_keypair, ov_product_identifier):

    endpoint = f"order/certificate/{ov_product_identifier}"
    payload = {
        "certificate": {
            "common_name": "test.inverted.space",

            "csr": generate_keypair,
            "signature_hash": "sha256",
            "server_platform": {
                "id": 2
            }
        },
        "comments": "autobot testing",
        "organization": {
            "id": 1903266,
        },
        "order_validity": {
            "years": 1
        },
        "payment_method": "balance",
        "dcv_method": "email"
    }

    response = make_request("POST", endpoint, payload)
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

    response = make_request("POST", endpoint, payload)
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
    ov_certificate(generate_keypair, "ssl_basic")


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


