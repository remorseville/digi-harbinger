from dotenv import dotenv_values
import json
from utils.dc_api_handler import digicert_api_handler


make_request = digicert_api_handler.make_request


def test_list_replacement_benefits():
    endpoint = "competitive-replacement/certificates"
    payload = {
            "domains": ["google.com", "amazon.com"]
            }
    response = make_request("POST", endpoint, payload)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))
    assert response.status_code == 200
    assert "certificates" in response.text, "Key 'certificates' is missing in the response"
    assert "serial_number" in response.text, "Key 'serial_number' is missing in the response"
