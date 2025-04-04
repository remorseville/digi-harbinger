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
import keyring
from collections import deque
from threading import Lock

# Local file imports
#from conftest import process_defined_tests  # Configuration file for the pytest module
from tests.test_functions import test_scripts
from tests.test_functions import cis_test_scripts
from tests import crypto
from conftest import process_defined_tests
from utils.sqlite_kv_store import kv_store
from utils.ocsp_check import check_certificate_revocation
from utils.scheduler import AsyncTestScheduler


# __________________________ Environment ________________________________ #
# ----------------------------------------------------------------------- #

app = Flask(__name__)                       # Main Flask App
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Required for hot-reloading of html otherwise you'll see cached versions
ui = FlaskUI(app, width=500, height=500)    


def resource_path(relative_path):           # Dynamic path handling for file references (prod vs dev)
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Globals
TEST_FUNCTIONS = test_scripts()                 # Refer to test_functions.Py - array of CertCentral API test names functions for handling
CIS_TEST_FUNCTIONS = cis_test_scripts()         # Refer to test_functions.Py - array of CIS API test names functions for handling
US_STATUS_VERIFIED = False                      # Used below with us_ping_get_account_values() # tracks api/api key status
EU_STATUS_VERIFIED = False                      # Used below with eu_ping_get_account_values() # tracks api/api key status
CIS_STATUS_VERIFIED = False                     # Used below with cis_ping_get_account_values() # tracks api/api key status
CIS_VALIDATION_STATUS_VERIFIED = False          # Used below with cis_validation_ping_get_account_values() # tracks api/api key status
kv_store = kv_store                             # Load our env sql db
kv_store.set("US_MODE", "true")                 # Sets mode to "true" on load - Toggle used for CCUS vs CCEU API base_url's


# __________________________ Routes ________________________________ #
# ------------------------------------------------------------------ #

""" 
Homepage 
"""
@app.route('/', methods=['GET', 'POST'])  
async def index():
    
    test_functions_cleaned = {                          # Pretty print handling for script filenames/functions (test_functions.py)
        key: [test.split("::")[1] for test in tests]    # Remove file paths
        for key, tests in TEST_FUNCTIONS.items()
    }

    cis_test_functions_cleaned = {                      # Pretty print handling for CIS script filenames/functions (test_functions.py)
        key: [test.split("::")[1] for test in tests]    # Remove file paths
        for key, tests in CIS_TEST_FUNCTIONS.items()
    }

    org_ids = await us_ping_get_account_values()        # US org id check / account ping - Returns array of org_id's
    org_ids = org_ids if org_ids is not None else []

    eu_org_ids = await eu_ping_get_account_values()     # EU org id check / account ping - Returns array of org_id's
    eu_org_ids = eu_org_ids if eu_org_ids is not None else []

    await cis_ping_get_account_values()                 # CIS Issuance API ping
    await cis_validation_ping_get_account_values()      # CIS Validation API ping

    return render_template("index.html",                                # Main index.html being served. Located in /templates/
                           org_ids=org_ids,
                           eu_org_ids=eu_org_ids,
                           test_functions=test_functions_cleaned,
                           eu_test_functions=test_functions_cleaned,
                           cis_test_functions = cis_test_functions_cleaned,
                           status_verified=US_STATUS_VERIFIED,
                           eu_status_verified=EU_STATUS_VERIFIED,
                           cis_status_verified=CIS_STATUS_VERIFIED,
                           cis_validation_status_verified=CIS_VALIDATION_STATUS_VERIFIED,
                           )


""" 
Account/org ping check 
"""
@app.route('/verify', methods=['GET']) #  TODO is this even used? remove? 
async def verification_status():
    data = await us_ping_get_account_values()
    return data


""" 
Generated report endpoint 
"""
@app.route('/report', methods=['GET', 'POST'])
async def report():
    ENV_STORE = kv_store                        # Initilize our custom env variable store db (csr, key, urls, etc.)
    if request.method == 'POST':                # "Mode" check - Used for calling the Certcentral us api vs. Certcentral eu api (base_url)

        cis_api = request.args.get('api')
        
        scheduler_mode = request.args.get('scheduler_mode')
        
        # CIS API Handling
        if cis_api:
            selected_tests = request.json.get('selected_tests', [])     # Processing of chosen tests in the post request
            if not selected_tests:
                return jsonify({"error": "No tests selected"}), 400

            full_selected_tests = []                                    # Final array
            for key, tests in CIS_TEST_FUNCTIONS.items():               # Global CIS_TEST_FUNCTIONS
                for test in tests:
                    test_name = test.split("::")[1]                     # Extract test names
                    if test_name in selected_tests:
                        full_selected_tests.append(test)

            await process_defined_tests(full_selected_tests)            # conftest.py - Main processing of selected tests to be ran

            now = datetime.now()                                        # Date/time handling for report filenames - appends to "report_****.html"
            formatted_time = now.strftime("%Y%m%d%H%M%S")
            source = resource_path('./templates/report.html')
            destination = resource_path(f'./templates/reports/CIS_report_{formatted_time}.html')  # Custom report titles
            
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
            
            report_name = "CIS_report_{formatted_time}"

            return jsonify({"report": report_name})
        

        # CCUS/CCEU API Handling
        else:
            mode = request.args.get('us_mode')      # Checks for post argument boolean
            org = request.args.get('org')           # Gets org_id from argument
            ENV_STORE.set("US_MODE", mode)          # Sets env "mode" - Used for CCUS vs. CCEU API's
            ENV_STORE.set("ORG_ID", org)            # Sets org_id env varible - Used by both CCUS and CCEU API's       

            selected_tests = request.json.get('selected_tests', [])     # Processing of chosen tests in the post request
            if not selected_tests:
                return jsonify({"error": "No tests selected"}), 400

            full_selected_tests = []                                    # Final array
            for key, tests in TEST_FUNCTIONS.items():                   # Global TEST_FUNCTIONS
                for test in tests:
                    test_name = test.split("::")[1]                     # Extract test names
                    if test_name in selected_tests:
                        full_selected_tests.append(test)

            await process_defined_tests(full_selected_tests)            # conftest.py (Pytest) - Main processing of selected tests to be ran

            
            now = datetime.now()                                        # Date/time handling for report filenames - appends to "report_****.html"
            formatted_time = now.strftime("%Y%m%d%H%M%S")
            source = resource_path('./templates/report.html')

            if mode == "true":
                destination = resource_path(f'./templates/reports/CCUS_report_{formatted_time}.html')  # Custom report titles
                report_name = f"CCUS_report_{formatted_time}"
            else:
                destination = resource_path(f'./templates/reports/CCEU_report_{formatted_time}.html')
                report_name = f"CCEU_report_{formatted_time}"

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

            #report_name = f"CC_report_{formatted_time}"

            return jsonify({"report": report_name})                          # returns the generated report (or last saved "Report.Html" on any failure)
    else:

        arg = request.args.get('id')                                    # get request handling - used for older report view
        if arg:
            return render_template(f"/reports/{arg}.html")              # if passed, generate (older) report
        else:
            return render_template('report.html')


""" 
API key env variable form endpoint 
"""
@app.route('/submit_', methods=['POST'])
def submit_env_variables():
    arg = request.args.get('id')
    data = request.json

    service_name = "digi-harbinger"  # Keyring service-name

    if arg == "api_key_us":
        env_var_name = "DIGICERT_API_KEY_US"
        keyring.set_password(service_name, env_var_name, data.get('api_key'))  # Save CCUS API key to keyring
        return jsonify({"message": "Key received successfully!"})

    elif arg == "api_key_eu":
        env_var_name = "DIGICERT_API_KEY_EU"
        keyring.set_password(service_name, env_var_name, data.get('api_key'))  # Save CCEU API key to keyring
        return jsonify({"message": "Key received successfully!"})
    
    elif arg == "api_key_cis":
        env_var_name = "CIS_API_KEY"
        keyring.set_password(service_name, env_var_name, data.get('api_key'))  # Save CIS API key to keyring
        return jsonify({"message": "Key received successfully!"})


""" 
Directory of past generated reports - once packaged, they will only persist per session 
TODO change this? It could cause file bloat over time 
"""
@app.route('/list-directory')
def list_directory():
    directory_path = resource_path('./templates/reports')
    
    try:
        files = [os.path.splitext(f)[0] for f in os.listdir(directory_path) if f.endswith('.html')]  # List all files in path
    except FileNotFoundError:
        return "Directory not found.", 404

    return jsonify({"files": files, "directory": directory_path})


""" 
Custom static directory for report handling - html 
"""
@app.route('/reports/<filename>')
def custom_static(filename):
    directory_path = resource_path('./reports')
    return send_from_directory(directory_path, filename)


""" 
Custom static directory for report handling - css/javascript 
"""
@app.route('/c_static/<filename>')
def custom_static_js_css(filename):
    directory_path = resource_path('./static')
    return send_from_directory(directory_path, filename)


""" 
Endpoint for generating private key/csr for user 
"""
@app.route('/keypair')
def gen_keypair():
    key = crypto.generate_private_key_tab()
    csr = crypto.generate_csr_tab(key)
    keypair = json.loads(csr)
    return jsonify({"csr": keypair["csr"], "key": keypair["key"]})


"""  
SSL Checker - Same that 'digicert.com/help' uses, but just the html <div> element is returned 
"""
@app.route('/help')
def help_check():
    cn = request.args.get('cn')
    if cn:
        url = 'https://www.digicert.com/api/check-host.php'
        data = {"host": f"{cn}"}
        response = requests.post(url, data=data)
        return response.text
    else:
        return


@app.route('/ocsp')
def ocsp_check():
    cn = request.args.get('cn')
    
    if cn:
        result = check_certificate_revocation(cn)
        return result
    else:
        return


""" 
Test Scheduler - Start, Stop, Status - My attempt at running x amount of tests every x minutes.
"""
scheduler = AsyncTestScheduler()


@app.route('/start-tests', methods=['POST'])
async def start_tests():
    data = request.get_json()
    full_selected_tests = []
    selected_tests = data.get('selected_tests', [])
    for key, tests in CIS_TEST_FUNCTIONS.items():                   # Global CIS_TEST_FUNCTIONS
                for test in tests:
                    test_name = test.split("::")[1]       
                    if test_name in selected_tests:
                        full_selected_tests.append(test)
    
    
    interval = data.get('interval', 5)
    repetitions = data.get('repetitions', 1)
    print(selected_tests)
    
    success = await scheduler.schedule_tests(
        selected_tests=full_selected_tests,
        interval_min=interval,
        repetitions=repetitions

    )

    return jsonify({
        "success": success,
        "status": scheduler.get_status(),
        "saved_report": scheduler.get_file_name(),
    })

@app.route('/stop', methods=['POST'])
def stop_scheduler():
    scheduler.stop()
    return jsonify({
        "success": True,
        "status": scheduler.get_status()
    })

@app.route('/status')
def get_status():
    return jsonify(scheduler.get_status())



"""
Output Display
"""
output_buffer = deque(maxlen=100)  # Keep last 100 lines
buffer_lock = Lock()

# Custom stream class to capture stdout
class OutputCapture:
    def write(self, text):
        with buffer_lock:
            output_buffer.append(text)
        # Also write to original stdout if needed
        #sys.__stdout__.write(text)
    
    def flush(self):
        pass

#sys.stdout.isatty = lambda: False
out_capture = OutputCapture()

@app.route('/testing', methods=['POST'])
def output():
    data = request.get_json()

    
    with buffer_lock:
        output_buffer.append(str(data))
        output = ''.join(output_buffer)
        #print(output)
    return jsonify(output)


@app.route('/output')
def get_output():
    with buffer_lock:
        return ''.join(output_buffer)
    
@app.route('/reset')
def reset_output():
    with buffer_lock:
        output_buffer.clear()
        return "ok"




# __________________________ Functions ________________________________ #
# --------------------------------------------------------------------- #

"""
Default api request helper - slightly different as this includes the base_url, 
rather then rely on the value in env
"""
def make_request(method, base_url, endpoint, headers, payload=None):
    url = f"{base_url}/{endpoint}"
    response = requests.request(method, url, headers=headers, json=payload)
    return response


""" 
Account ping and org check - Poplates list of account organizations for the dropdown within index.html
Used on the CCUS and CCEU tabs within index.html
"""
async def us_ping_get_account_values():
    global US_STATUS_VERIFIED
    ENV_STORE = kv_store                   # Initilize our custom env variable store db (csr, key, urls, etc.)
    try:
        base_url = ENV_STORE.get("DIGICERT_BASE_URL_US")
        api_key = keyring.get_password("digi-harbinger", "DIGICERT_API_KEY_US")
        headers = {
            "X-DC-DEVKEY": api_key,
            "Content-Type": "application/json"
        }
        endpoint = "organization"
        response = make_request("GET", base_url, endpoint, headers)
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
    ENV_STORE = kv_store                   # Initilize our custom env variable store db ( csr, key, urls, etc.)
    try:
        base_url = ENV_STORE.get("DIGICERT_BASE_URL_EU")
        api_key = keyring.get_password("digi-harbinger", "DIGICERT_API_KEY_EU")
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
            print(response)
            EU_STATUS_VERIFIED = False
    except ConnectionError as e:
        print(e)
        EU_STATUS_VERIFIED = False
        return
    

"""  
CIS Account ping - Issuance API 
"""
async def cis_ping_get_account_values():
    global CIS_STATUS_VERIFIED
    ENV_STORE = kv_store                   # Initilize our custom env variable store db ( csr, key, urls, etc.)
    try:
        base_url = ENV_STORE.get("CIS_BASE_URL")
        api_key = keyring.get_password("digi-harbinger", "CIS_API_KEY")
        headers = {
            "X-DC-DEVKEY": api_key,
            "Content-Type": "application/json"
        }
        
        if api_key == None:
            CIS_STATUS_VERIFIED = False
            return
        else: 
            endpoint = "cis/health/heartbeat"
            response = make_request("GET", base_url, endpoint, headers)
            if response.status_code == 204:
                CIS_STATUS_VERIFIED = True
            else:
                print(response)
                CIS_STATUS_VERIFIED = False
    except ConnectionError as e:
        print(e)
        CIS_STATUS_VERIFIED = False
        return


"""  
CIS Account ping - Validation API 
"""
async def cis_validation_ping_get_account_values():
    global CIS_VALIDATION_STATUS_VERIFIED
    ENV_STORE = kv_store                   # Initilize our custom env variable store db ( csr, key, urls, etc.)
    try:
        base_url = ENV_STORE.get("CIS_BASE_URL")
        api_key = keyring.get_password("digi-harbinger", "CIS_API_KEY")
        headers = {
            "X-DC-DEVKEY": api_key,
            "Content-Type": "application/json"
        }

        if api_key == None:
            CIS_VALIDATION_STATUS_VERIFIED = False
            return
        else: 
            endpoint = "validation/health/heartbeat"
            response = make_request("GET", base_url, endpoint, headers)
            if response.status_code == 204:
                CIS_VALIDATION_STATUS_VERIFIED = True
            else:
                print(response)
                CIS_VALIDATION_STATUS_VERIFIED = False
    except ConnectionError as e:
        print(e)
        CIS_VALIDATION_STATUS_VERIFIED = False
        return

# ------------------------------- Main ------------------------------------ #

""" 
Defines the user's screen size so it can be used for app window placement 
"""
def user_screen_size():
    user32 = ctypes.windll.user32
    screensize = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
    return screensize  # (x,y)


""" 
Seperate flask function so waitress can be used (performance) 
"""
def start_flask(**server_kwargs):
    app = server_kwargs.pop("app", None)
    server_kwargs.pop("debug", None)

    import waitress
    waitress.serve(app, **server_kwargs)
    


if __name__ == "__main__":
    
    if '_PYI_SPLASH_IPC' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash        # this import error is okay - it's a pytest plugin (hotload) for the splash screen 
        pyi_splash.update_text('UI Loaded ...')
        time.sleep(2)
        pyi_splash.close()

    
    # On close function
    def saybye():
        print("on_exit bye")

    # App dimensions and screen placement on load
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
            "host": "localhost"
        },
        width=app_width,
        height=app_height,
        browser_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',  # Chrome dependant at the moment. I attempted to use Edge and it would crash on first run
        extra_flags = [f"--window-position={int(screen_x)},{int(screen_y)}"],       # Centers the app window within the user's main monitor
        on_shutdown=saybye,
    ).run()

