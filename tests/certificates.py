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



def find_cert_id():
    endpoint = "order/certificate"
    locale_url_header_org = locale_check()
    response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
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
    locale_url_header_org = locale_check()
    match cert_format:
        case "default_pem" | "default" | "default_cer" | "apache":
            endpoint = f"certificate/{cert_id}/download/format/{cert_format}"
            
            response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
            assert response.status_code == 200
            assert isinstance(response.content, bytes)  # Ensure the response is in bytes
            assert response.headers["Content-Type"] == "application/zip", "Response is not a ZIP file"
            print("Zip File Successfully Downloaded")

        case "pem_all" | "pem_nointermediate" | "pem_noroot":
            endpoint = f"certificate/{cert_id}/download/format/{cert_format}"
            response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
            print(response.text)
            assert response.status_code == 200
            assert isinstance(response.content, bytes)  # Ensure the response is in bytes
            assert response.headers["Content-Type"] == "application/x-pem-file", "Response is not a PEM file"
            assert response.content.startswith(b"-----BEGIN CERTIFICATE-----")  # Check for PEM header

        case "p7b" | "cer":
            endpoint = f"certificate/{cert_id}/download/format/{cert_format}"
            response = make_request("GET",locale_url_header_org[0],endpoint, locale_url_header_org[1])
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


