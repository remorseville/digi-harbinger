import requests
import json
import os
import sys
import shutil
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
from dotenv import dotenv_values, set_key, load_dotenv
import importlib

from flaskwebgui import FlaskUI  # TODO used for when changed to UI vs Browser

# LOCAL IMPORTS
from conftest import process_defined_tests
from tests.test_functions import test_scripts
from tests import crypto


app = Flask(__name__)
ui = FlaskUI(app, width=500, height=500) # TODO used for when changed to UI vs Browser


# DYNAMIC PATH HANDLING (PACKAGED VS DEV)
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# GLOBALS
APP_DATA = os.getenv('LOCALAPPDATA')
APP_DIRECTORY = os.path.join(APP_DATA, "Digi-Harbinger")
ENV_FILE = os.path.join(APP_DIRECTORY, ".env")
TEST_FUNCTIONS = test_scripts() # REFER TO test_functions.py - ARRAY OF TEST FUNCTIONS FOR HANDLING
US_STATUS_VERIFIED = False      # USED BELOW WITH us_ping_get_account_values() # TRACKS API/API KEY STATUS
EU_STATUS_VERIFIED = False      # USED BELOW WITH eu_ping_get_account_values() # TRACKS API/API KEY STATUS


# -------------------------- ROUTES -------------------------------- #

# HOMEPAGE
@app.route('/', methods=['GET', 'POST'])
async def index():

    # PRETTY PRINT HANDLING FOR SCRIPT FILENAMES/FUNCTIONS
    test_functions_cleaned = {
        key: [test.split("::")[1] for test in tests]    # REMOVE FILE PATHS
        for key, tests in TEST_FUNCTIONS.items()
    }

    # CHECK FOR ORG ID US
    org_ids = await us_ping_get_account_values()        # THIS IS ALSO AN ACCOUNT PING/STATUS CHECK
    org_ids = org_ids if org_ids is not None else []

    # CHECK FOR ORG ID EU
    eu_org_ids = await eu_ping_get_account_values()     # THIS IS ALSO AN ACCOUNT PING/STATUS CHECK
    eu_org_ids = eu_org_ids if eu_org_ids is not None else []

    return render_template("index.html", 
                           org_ids=org_ids,
                           eu_org_ids=eu_org_ids,
                           test_functions=test_functions_cleaned,
                           eu_test_functions=test_functions_cleaned,
                           status_verified=US_STATUS_VERIFIED,
                           eu_status_verified=EU_STATUS_VERIFIED,
                           )


# ACCOUNT/ORG PING CHECK
@app.route('/verify', methods=['GET'])
async def verification_status():
    data = await us_ping_get_account_values()
    print(data)
    return data


# GENERATED REPORT ENDPOINT
@app.route('/report', methods=['GET', 'POST'])
async def report():
    if request.method == 'POST':
        
        # "MODE" CHECK - USED FOR CALLING THE CERTCENTRAL USA API VS. CERTCENTRAL EU API (BASE_URL)
        mode = request.args.get('us_mode') # CHECKS FOR POST ARGUMENT BOOLEAN
        env_vars = dotenv_values(ENV_FILE) # LOAD .env FILE
        env_vars["US_MODE"] = mode            # SETS "MODE" VARIABLE AND WRITES TO FILE 
        for key, value in env_vars.items():
            set_key(ENV_FILE, key, value)

        # PROCESSING OF CHOSEN TESTS IN THE POST REQUEST
        selected_tests = request.json.get('selected_tests', [])
        if not selected_tests:
            return jsonify({"error": "No tests selected"}), 400

        full_selected_tests = []                   # FINAL ARRAY
        for key, tests in TEST_FUNCTIONS.items():  # GLOBAL TEST_FUNCTIONS
            for test in tests:
                test_name = test.split("::")[1]    # EXTRACT TEST NAME
                if test_name in selected_tests:
                    full_selected_tests.append(test)


        await process_defined_tests(full_selected_tests)  # CONFTEST.PY

        # DATE/TIME HANDLING FOR REPORT FILENAMES - APPENDS TO "report_****.html"
        now = datetime.now() 
        formatted_time = now.strftime("%Y%m%d%H%M%S")
        source = resource_path('./templates/report.html')
        destination = resource_path(f'./templates/reports/report_{formatted_time}.html')

        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)  # CREATES THE "templates/reports" DIRECTORY  
            shutil.copy2(source, destination)                         # COPIES GENERATED "report.html" TO "templates/reports"
            print(f"File copied from {source} to {destination}")
        except FileNotFoundError:
            print(f"Source file {source} not found.")
        except PermissionError:
            print(f"Permission denied for {destination}.")
        except Exception as e:
            print(f"An error occurred: {e}")

        return render_template("report.html")  # RETUNRS THE GENERATED REPORT (OR LAST SAVED "report.html" ON ANY FAILURE)
    else:

        # GET REQUEST HANDLING - USED FOR OLDER REPORT VIEW
        arg = request.args.get('id')                        # PASSED URL PARAMETER "id"
        if arg:
            return render_template(f"/reports/{arg}.html")  # IF PASSED, GENERATE (OLDER) REPORT
        else:
            return render_template("report.html")


# ENV VARIABLE FORM ENDPOINT
@app.route('/submit_', methods=['POST'])
def submit_env_variables():
    env_vars = dotenv_values(ENV_FILE)
    arg = request.args.get('id')
    data = request.json

    if arg == "api_key_us":
        # UPDATE ENV VARIABLES
        # env_vars["ORG_ID"] = data.get('org_id') TODO remove?
        env_vars["DIGICERT_API_KEY_US"] = data.get('api_key')
        for key, value in env_vars.items():
            set_key(ENV_FILE, key, value)
        us_ping_get_account_values()
        return jsonify({"message": "Key received successfully!"})

    elif arg == "api_key_eu":
        # UPDATE ENV VARIABLES
        # env_vars["ORG_ID"] = data.get('org_id') TODO remove?
        env_vars["DIGICERT_API_KEY_EU"] = data.get('api_key')
        for key, value in env_vars.items():
            set_key(ENV_FILE, key, value)
        eu_ping_get_account_values()
        return jsonify({"message": "Key received successfully!"})


# DIRECTORY OF PAST GENERATED REPORTS - ONCE PACKAGED, THEY WILL ONLY PERSIST PER SESSION
@app.route('/list-directory')
def list_directory():
    directory_path = resource_path('./templates/reports')
    # LIST ALL FILES IN PATH
    try:
        files = [os.path.splitext(f)[0] for f in os.listdir(directory_path) if f.endswith('.html')]
    except FileNotFoundError:
        return "Directory not found.", 404

    return jsonify({"files": files, "directory": directory_path})


# CUSTOM STATIC DIRECTORY FOR REPORT HANDLING - HTML
@app.route('/reports/<filename>')
def custom_static(filename):
    directory_path = resource_path('./reports')
    return send_from_directory(directory_path, filename)


# CUSTOM STATIC DIRECTORY FOR REPORT HANDLING - CSS/JAVASCRIPT
@app.route('/c_static/<filename>')
def custom_static_js_css(filename):
    directory_path = resource_path('./static')
    return send_from_directory(directory_path, filename)


# ENDPOINT FOR GENERATING PRIVATE KEY/CSR FOR USER
@app.route('/keypair')
def gen_keypair():
    key = crypto.generate_private_key_tab()
    csr = crypto.generate_csr_tab(key)
    keypair = json.loads(csr)
    return jsonify({"csr": keypair["csr"], "key": keypair["key"]})

# -------------------------- END ROUTES -------------------------------- #


# -------------------------- FUNCTIONS -------------------------------- #

# DEFAULT REQUEST HELPER
def make_request(method, base_url, endpoint, headers, payload=None):
    url = f"{base_url}/{endpoint}"
    response = requests.request(method, url, headers=headers, json=payload)
    return response


async def get_user_details():  # TODO Currently not used - remove?

    try:
        env_vars = dotenv_values(resource_path("./.env"))
        base_url = env_vars["DIGICERT_BASE_URL"]
        api_key = env_vars["DIGICERT_API_KEY"]
        headers = {
            "X-DC-DEVKEY": api_key,
            "Content-Type": "application/json"
        }
        endpoint = "user/me"
        response = make_request("GET", base_url, endpoint, headers)
        data = json.loads(response.text)
        print(data)
        if response.status_code == 200:
            if data["first_name"] != "Public":
                data = json.loads(response.text)
                user_name = data["first_name"]
                return user_name
            else:
                return
        else:
            return
    except ConnectionError as e:
        return



async def us_ping_get_account_values():
    global US_STATUS_VERIFIED
    try:
        env_vars = dotenv_values(ENV_FILE)
        base_url = env_vars["DIGICERT_BASE_URL_US"]
        api_key = env_vars["DIGICERT_API_KEY_US"]
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
            US_STATUS_VERIFIED = False
    except ConnectionError as e:
        print(e)
        US_STATUS_VERIFIED = False
        return



async def eu_ping_get_account_values():
    global EU_STATUS_VERIFIED
    try:
        env_vars = dotenv_values(ENV_FILE)
        base_url = env_vars["DIGICERT_BASE_URL_EU"]
        api_key = env_vars["DIGICERT_API_KEY_EU"]
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

# -------------------------- END FUNCTIONS -------------------------------- #

# WHEN THE APP IS RAN, THIS GENERATES/CHECKS FOR THE ".env" FILE. STORED AT "C:\Users\$USER\AppData\Local\Digi-Harbinger\.env
def on_boot():
    
    try:
        os.makedirs(APP_DIRECTORY, exist_ok=True)
        if not os.path.exists(ENV_FILE):
            with open(ENV_FILE, "w") as f:
                f.write("US_MODE='true'\n")
                f.write("DIGICERT_API_KEY_US=''\n")
                f.write("DIGICERT_API_KEY_EU=''\n")
                f.write("DIGICERT_BASE_URL_US='https://www.digicert.com/services/v2'\n")
                f.write("DIGICERT_BASE_URL_EU='https://certcentral.digicert.eu/services/v2'\n")
                f.write("CSR=''\n")
                f.write("PRIVATE_KEY=''\n")     
        else:
            print("File already exists")

    except Exception as e:
        print(f"An error occurred: {e}")


# SEPERATE FLASK FUNCTION SO WAITRESS CAN BE USED (PERFORMANCE)
def start_flask(**server_kwargs):
    
    on_boot()
    app = server_kwargs.pop("app", None)
    server_kwargs.pop("debug", None)

    import waitress
    waitress.serve(app, **server_kwargs)
    




if __name__ == "__main__":
    
    # ON CLOSE FUNCTION
    def saybye():
        print("on_exit bye")

    if '_PYI_SPLASH_IPC' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash  # THIS IMPORT ERROR IS OKAY - IT'S A PYTEST PLUGIN
        pyi_splash.update_text('UI Loaded ...')
        time.sleep(2)
        pyi_splash.close()
        #log.info('Splash screen closed.')

    FlaskUI(
        server=start_flask,
        server_kwargs={
            "app": app,
            "port": 5444,
        },
        width=1500,
        height=1100,
        browser_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        on_shutdown=saybye,
    ).run()


# TODO REMOVE
    #app.run(host='127.0.0.1', debug=True)
    #start_flaskwebgui()

    #pytest --html=\Users\ben.morse\PycharmProjects\DIGI-TEST-MAR15\templates\report.html --css=custom.css --self-contained-html .\account.py
