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


def find_cert_id():
    endpoint = "order/certificate"
    response = make_request("GET", endpoint)
    data = json.loads(response.text)

    for cert in data["orders"]:
        if cert["status"] == "issued":
            product_type = cert["product"]["type"]
            if product_type == "ssl_certificate":
                cert_id = cert["certificate"]["id"]
                print("Captured cert_id:", cert_id)
                return cert_id


# download cert format
def download_certificate(cert_id_for_downloads, cert_format):
    cert_id = cert_id_for_downloads

    match cert_format:
        case "default_pem" | "default" | "default_cer" | "apache":
            endpoint = f"certificate/{cert_id}/download/format/{cert_format}"
            response = make_request("GET", endpoint)
            assert response.status_code == 200
            assert isinstance(response.content, bytes)  # Ensure the response is in bytes
            assert response.headers["Content-Type"] == "application/zip", "Response is not a ZIP file"
            print("Zip File Successfully Downloaded")

        case "pem_all" | "pem_nointermediate" | "pem_noroot":
            endpoint = f"certificate/{cert_id}/download/format/{cert_format}"
            response = make_request("GET", endpoint)
            print(response.text)
            assert response.status_code == 200
            assert isinstance(response.content, bytes)  # Ensure the response is in bytes
            assert response.headers["Content-Type"] == "application/x-pem-file", "Response is not a PEM file"
            assert response.content.startswith(b"-----BEGIN CERTIFICATE-----")  # Check for PEM header

        case "p7b" | "cer":
            endpoint = f"certificate/{cert_id}/download/format/{cert_format}"
            response = make_request("GET", endpoint)
            print(response.text)
            assert response.status_code == 200
            assert isinstance(response.content, bytes)  # Ensure the response is in bytes
            assert response.headers[
                       "Content-Type"] == "application/x-pkcs7-certificates", "Response is not a p7b file"
            assert response.content.startswith(b"-----BEGIN PKCS7-----")  # Check for PKCS7 header


def revoke_certificate():  # TODO
    return


def archive_certificate():  # TODO
    return


def restore_certificate():  # TODO
    return


# download tests
def test_download_certificate_default_pem(cert_id_for_downloads):
    download_certificate(cert_id_for_downloads, "default_pem")


def test_download_certificate_default(cert_id_for_downloads):
    download_certificate(cert_id_for_downloads, "default")


def test_download_certificate_default_cer(cert_id_for_downloads):
    download_certificate(cert_id_for_downloads, "default_cer")


def test_download_certificate_apache(cert_id_for_downloads):
    download_certificate(cert_id_for_downloads, "apache")


def test_download_certificate_pem_all(cert_id_for_downloads):
    download_certificate(cert_id_for_downloads, "pem_all")


def test_download_certificate_pem_nointermediate(cert_id_for_downloads):
    download_certificate(cert_id_for_downloads, "pem_nointermediate")


def test_download_certificate_pem_noroot(cert_id_for_downloads):
    download_certificate(cert_id_for_downloads, "pem_noroot")


def test_download_certificate_p7b(cert_id_for_downloads):
    download_certificate(cert_id_for_downloads, "p7b")


def test_download_certificate_cer(cert_id_for_downloads):
    download_certificate(cert_id_for_downloads, "cer")


