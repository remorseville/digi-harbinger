import requests
import json
import os
import sys
import shutil
import time
import ctypes
import importlib
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
from flaskwebgui import FlaskUI             

# local imports
from conftest import process_defined_tests
from tests.test_functions import test_scripts
from tests import crypto
from utils.sqlite_kv_store import kv_store

kv_store = kv_store 


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Required for hot-reloading of html otherwise you'll see cached versions
ui = FlaskUI(app, width=500, height=500)    


def resource_path(relative_path):           # Dynamic path handling for file references (packaged vs dev)
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Globals
APP_DATA = os.getenv('LOCALAPPDATA')
APP_DIRECTORY = os.path.join(APP_DATA, "Digi-Harbinger")
ENV_FILE = os.path.join(APP_DIRECTORY, "env.json")
TEST_FUNCTIONS = test_scripts()             # Refer to test_functions.Py - array of test functions for handling
US_STATUS_VERIFIED = False                  # Used below with us_ping_get_account_values() # tracks api/api key status
EU_STATUS_VERIFIED = False
kv_store.set("US_MODE", "true")                  # Used below with eu_ping_get_account_values() # tracks api/api key status



# -------------------------- routes -------------------------------- #

# Homepage
@app.route('/', methods=['GET', 'POST'])  
async def index():
    

    
    test_functions_cleaned = {                          # Pretty print handling for script filenames/functions
        key: [test.split("::")[1] for test in tests]    # Remove file paths
        for key, tests in TEST_FUNCTIONS.items()
    }

    org_ids = await us_ping_get_account_values()        # US org id check / account ping 
    org_ids = org_ids if org_ids is not None else []

    eu_org_ids = await eu_ping_get_account_values()     # EU org id check / account ping 
    eu_org_ids = eu_org_ids if eu_org_ids is not None else []

    return render_template("index.html", 
                           org_ids=org_ids,
                           eu_org_ids=eu_org_ids,
                           test_functions=test_functions_cleaned,
                           eu_test_functions=test_functions_cleaned,
                           status_verified=US_STATUS_VERIFIED,
                           eu_status_verified=EU_STATUS_VERIFIED,
                           )


# Account/org ping check
@app.route('/verify', methods=['GET'])
async def verification_status():
    data = await us_ping_get_account_values()
    return data


# Generated report endpoint
@app.route('/report', methods=['GET', 'POST'])
async def report():
    ENV_STORE = kv_store                   # Initilize our custom env variable store (api keys, csr, key, urls, etc.)
    if request.method == 'POST':                # "Mode" check - Used for calling the Certcentral us api vs. Certcentral eu api (base_url)
        mode = request.args.get('us_mode')      # Checks for post argument boolean
        org = request.args.get('org')           # Gets org_id from argument
        ENV_STORE.set("US_MODE", mode)          # Sets env "mode" - Used for CCUS vs. CCEU API's
        ENV_STORE.set("ORG_ID", org)           # Sets org_id env varible - Used by both CCUS and CCEU API's       

        selected_tests = request.json.get('selected_tests', [])     # Processing of chosen tests in the post request
        if not selected_tests:
            return jsonify({"error": "No tests selected"}), 400

        full_selected_tests = []                                    # Final array
        for key, tests in TEST_FUNCTIONS.items():                   # Global TEST_FUNCTIONS
            for test in tests:
                test_name = test.split("::")[1]                     # Extract test names
                if test_name in selected_tests:
                    full_selected_tests.append(test)

        await process_defined_tests(full_selected_tests)            # conftest.py

        
        now = datetime.now()                                        # Date/time handling for report filenames - appends to "Report_****.Html"
        formatted_time = now.strftime("%Y%m%d%H%M%S")
        source = resource_path('./templates/report.html')

        if mode == "true":
            destination = resource_path(f'./templates/reports/CCUS_report_{formatted_time}.html')  # Custom report titles
        else:
            destination = resource_path(f'./templates/reports/CCEU_report_{formatted_time}.html')

        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)    # creates the "Templates/reports" directory  
            shutil.copy2(source, destination)                           # copies generated "Report.Html" to "Templates/reports"
            print(f"File copied from {source} to {destination}")
        except FileNotFoundError:
            print(f"Source file {source} not found.")
        except PermissionError:
            print(f"Permission denied for {destination}.")
        except Exception as e:
            print(f"An error occurred: {e}")

        return render_template('report.html')                           # returns the generated report (or last saved "Report.Html" on any failure)
    else:

        arg = request.args.get('id')                                    # get request handling - used for older report view
        if arg:
            return render_template(f"/reports/{arg}.html")              # if passed, generate (older) report
        else:
            return render_template('report.html')


# API key env variable form endpoint
@app.route('/submit_', methods=['POST'])
def submit_env_variables():
    ENV_STORE = kv_store                   # Initilize our custom env variable store (api keys, csr, key, urls, etc.)
    arg = request.args.get('id')
    data = request.json

    if arg == "api_key_us":
        ENV_STORE.set("DIGICERT_API_KEY_US", data.get('api_key') )
        return jsonify({"message": "Key received successfully!"})

    elif arg == "api_key_eu":
        ENV_STORE.set("DIGICERT_API_KEY_EU", data.get('api_key') )
        return jsonify({"message": "Key received successfully!"})


# Directory of past generated reports - once packaged, they will only persist per session TODO change this? It could cause file bloat over time
@app.route('/list-directory')
def list_directory():
    directory_path = resource_path('./templates/reports')
    
    try:
        files = [os.path.splitext(f)[0] for f in os.listdir(directory_path) if f.endswith('.html')]  # list all files in path
    except FileNotFoundError:
        return "Directory not found.", 404

    return jsonify({"files": files, "directory": directory_path})


# Custom static directory for report handling - html
@app.route('/reports/<filename>')
def custom_static(filename):
    directory_path = resource_path('./reports')
    return send_from_directory(directory_path, filename)


# Custom static directory for report handling - css/javascript
@app.route('/c_static/<filename>')
def custom_static_js_css(filename):
    directory_path = resource_path('./static')
    return send_from_directory(directory_path, filename)


# Endpoint for generating private key/csr for user
@app.route('/keypair')
def gen_keypair():
    key = crypto.generate_private_key_tab()
    csr = crypto.generate_csr_tab(key)
    keypair = json.loads(csr)
    return jsonify({"csr": keypair["csr"], "key": keypair["key"]})

# -------------------------- end routes -------------------------------- #


# -------------------------- functions -------------------------------- #

# Default request helper - slightly different as this includes the base_url, 
# rather then rely on the value in env
def make_request(method, base_url, endpoint, headers, payload=None):
    url = f"{base_url}/{endpoint}"
    response = requests.request(method, url, headers=headers, json=payload)
    return response


#  Account ping and org check - Poplates list of account organizations for the dropdown within index.html
#  Used on the CCUS and CCEU tabs within index.html
async def us_ping_get_account_values():
    global US_STATUS_VERIFIED
    ENV_STORE = kv_store                   # Initilize our custom env variable store (api keys, csr, key, urls, etc.)
    try:
        base_url = ENV_STORE.get("DIGICERT_BASE_URL_US")
        api_key = ENV_STORE.get("DIGICERT_API_KEY_US")
        headers = {
            "X-DC-DEVKEY": api_key,
            "Content-Type": "application/json"
        }
        endpoint = "organization"
        response = make_request("GET", base_url, endpoint, headers)
        print(response.text)
        if response.status_code == 200:
            US_STATUS_VERIFIED = True
            data = json.loads(response.text)
            org_ids = []
            for org in data["organizations"]:
                org_ids.append({
                    "org_id": org["id"],
                    "org_name": org["name"]
                    })
            return org_ids
        else:
            print(response)
            US_STATUS_VERIFIED = False
    except ConnectionError as e:
        print(e)
        US_STATUS_VERIFIED = False
        return


async def eu_ping_get_account_values():
    global EU_STATUS_VERIFIED
    ENV_STORE = kv_store                   # Initilize our custom env variable store (api keys, csr, key, urls, etc.)
    try:
        base_url = ENV_STORE.get("DIGICERT_BASE_URL_EU")
        api_key = ENV_STORE.get("DIGICERT_API_KEY_EU")
        headers = {
            "X-DC-DEVKEY": api_key,
            "Content-Type": "application/json"
        }
        endpoint = "organization"
        response = make_request("GET", base_url, endpoint, headers)
        if response.status_code == 200:
            EU_STATUS_VERIFIED = True
            data = json.loads(response.text)
            org_ids = []
            for org in data["organizations"]:
                org_ids.append({
                    "org_id": org["id"],
                    "org_name": org["name"]
                    })
            return org_ids
        else:
            EU_STATUS_VERIFIED = False
    except ConnectionError as e:
        print(e)
        EU_STATUS_VERIFIED = False
        return

# -------------------------- end functions -------------------------------- #

# When the app is ran, this generates/checks for the "env.json" file.
# Stored at "C:\users\$user\appdata\local\digi-harbinger\env.json

def on_boot():
    #ENV_STORE = kv_store
                 # Initilize our custom env variable store (api keys, csr, key, urls, etc.)
    try:
        os.makedirs(APP_DIRECTORY, exist_ok=True)
        if not os.path.exists(ENV_FILE):
            kv_store.set("US_MODE", "true")
            kv_store.set("DIGICERT_API_KEY_US", "")
            kv_store.set("DIGICERT_API_KEY_EU", "")
            kv_store.set("DIGICERT_BASE_URL_US", "https://www.digicert.com/services/v2")
            kv_store.set("DIGICERT_BASE_URL_EU", "https://certcentral.digicert.eu/services/v2")
            kv_store.set("CSR", "")
            kv_store.set("PRIVATE_KEY", "")
            kv_store.set("ORG_ID", "") 
            kv_store.close()
        else:
            print("File already exists")

    except Exception as e:
        print(f"An error occurred: {e}")


# Defines the user's screen size so it can be used for app window placement
def user_screen_size():
    user32 = ctypes.windll.user32
    screensize = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
    return screensize  # (x,y)


# seperate flask function so waitress can be used (performance)
def start_flask(**server_kwargs):
    
    
    app = server_kwargs.pop("app", None)
    server_kwargs.pop("debug", None)

    import waitress
    waitress.serve(app, **server_kwargs)
    


if __name__ == "__main__":
    
    if '_PYI_SPLASH_IPC' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash        # this import error is okay - it's a pytest plugin for the splash screen when ran
        pyi_splash.update_text('UI Loaded ...')
        time.sleep(2)
        pyi_splash.close()

    
    # on close function
    def saybye():
        print("on_exit bye")

    # App dimensions and placement in screen on load
    app_width = 1100
    app_height = 950
    screen_dimensions = user_screen_size()
    screen_x = (screen_dimensions[0] / 2) - (app_width / 2)
    screen_y = (screen_dimensions[1] / 2) - (app_height / 2)

    FlaskUI(
        server=start_flask,
        server_kwargs={
            "app": app,
            "port": 5444,
        },
        width=app_width,
        height=app_height,
        browser_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',  # Chrome dependant at the moment. I attempted to use Edge and it would crash on first run
        extra_flags = [f"--window-position={int(screen_x)},{int(screen_y)}"],       # Centers the app window within the user's main monitor
        on_shutdown=saybye,
        #on_startup=on_boot
    ).run()

