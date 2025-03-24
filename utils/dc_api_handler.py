import requests
from .sqlite_kv_store import kv_store

class DigiCertApiHandler:
    def __init__(self):
        self.kv_store = kv_store
        self.us_mode = self.kv_store.get("US_MODE")
        self.org_id = self.kv_store.get("ORG_ID")
        self.base_url = self._get_base_url()
        self.api_key = self._get_api_key()
        self.headers = {
            "X-DC-DEVKEY": self.api_key,
            "Content-Type": "application/json"
        }

    def _get_base_url(self):
        return self.kv_store.get("DIGICERT_BASE_URL_US") if self.us_mode else self.kv_store.get("DIGICERT_BASE_URL_EU")

    def _get_api_key(self):
        return self.kv_store.get("DIGICERT_API_KEY_US") if self.us_mode else self.kv_store.get("DIGICERT_API_KEY_EU")

    def make_request(self, method, endpoint, payload=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=payload)
        return response

# Create an instance of DigiCertApiHandler
digicert_api_handler = DigiCertApiHandler()