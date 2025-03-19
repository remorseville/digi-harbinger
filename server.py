import requests
import json
import os
import sys
import shutil
import time
import ctypes
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
from dotenv import dotenv_values, set_key, load_dotenv
import importlib

from flaskwebgui import FlaskUI  # TODO used for when changed to UI vs Browser

# local imports
from conftest import process_defined_tests
from tests.test_functions import test_scripts
from tests import crypto


app = Flask(__name__)
ui = FlaskUI(app, width=500, height=500) # TODO used for when changed to UI vs Browser


# dynamic path handling (packaged vs dev)
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# globals
APP_DATA = os.getenv('LOCALAPPDATA')
APP_DIRECTORY = os.path.join(APP_DATA, "Digi-Harbinger")
ENV_FILE = os.path.join(APP_DIRECTORY, ".env")
TEST_FUNCTIONS = test_scripts() # Refer to test_functions.Py - array of test functions for handling
US_STATUS_VERIFIED = False      # Used below with us_ping_get_account_values() # tracks api/api key status
EU_STATUS_VERIFIED = False      # Used below with eu_ping_get_account_values() # tracks api/api key status


# -------------------------- routes -------------------------------- #

@app.after_request
def add_security_headers(resp):
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '-1'
    return resp


# homepage
@app.route('/', methods=['GET', 'POST'])
async def index():

    # pretty print handling for script filenames/functions
    test_functions_cleaned = {
        key: [test.split("::")[1] for test in tests]    # remove file paths
        for key, tests in TEST_FUNCTIONS.items()
    }

    # US org is check / account ping
    org_ids = await us_ping_get_account_values()        
    org_ids = org_ids if org_ids is not None else []

    # EU org id check - account ping
    eu_org_ids = await eu_ping_get_account_values()    
    eu_org_ids = eu_org_ids if eu_org_ids is not None else []

    return render_template("index.html", 
                           org_ids=org_ids,
                           eu_org_ids=eu_org_ids,
                           test_functions=test_functions_cleaned,
                           eu_test_functions=test_functions_cleaned,
                           status_verified=US_STATUS_VERIFIED,
                           eu_status_verified=EU_STATUS_VERIFIED,
                           )


# account/org ping check
@app.route('/verify', methods=['GET'])
async def verification_status():
    data = await us_ping_get_account_values()
    print(data)
    return data


# generated report endpoing
@app.route('/report', methods=['GET', 'POST'])
async def report():
    if request.method == 'POST':
        
        # "Mode" check - used for calling the certcentral usa api vs. Certcentral eu api (base_url)
        mode = request.args.get('us_mode') # checks for post argument boolean
        env_vars = dotenv_values(ENV_FILE) 
        env_vars["US_MODE"] = mode           
        for key, value in env_vars.items():
            set_key(ENV_FILE, key, value)

        # processing of chosen tests in the post request
        selected_tests = request.json.get('selected_tests', [])
        if not selected_tests:
            return jsonify({"error": "No tests selected"}), 400

        full_selected_tests = []                   # final array
        for key, tests in TEST_FUNCTIONS.items():  # global TEST_FUNCTIONS
            for test in tests:
                test_name = test.split("::")[1]    # extract test names
                if test_name in selected_tests:
                    full_selected_tests.append(test)


        await process_defined_tests(full_selected_tests)  # conftest.py

        # date/time handling for report filenames - appends to "Report_****.Html"
        now = datetime.now() 
        formatted_time = now.strftime("%Y%m%d%H%M%S")
        source = resource_path('./templates/report.html')
        destination = resource_path(f'./templates/reports/report_{formatted_time}.html')

        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)  # creates the "Templates/reports" directory  
            shutil.copy2(source, destination)                         # copies generated "Report.Html" to "Templates/reports"
            print(f"File copied from {source} to {destination}")
        except FileNotFoundError:
            print(f"Source file {source} not found.")
        except PermissionError:
            print(f"Permission denied for {destination}.")
        except Exception as e:
            print(f"An error occurred: {e}")

        response = render_template('report.html')
    
        
        return response  # returns the generated report (or last saved "Report.Html" on any failure)
    else:

        # get request handling - used for older report view
        arg = request.args.get('id')                        # get request handling - used for older report view
        if arg:
            return render_template(f"/reports/{arg}.html")  # if passed, generate (older) report
        else:
            response = render_template('report.html')
            
            return response 


# env variable form endpoint
@app.route('/submit_', methods=['POST'])
def submit_env_variables():
    env_vars = dotenv_values(ENV_FILE)
    arg = request.args.get('id')
    data = request.json

    if arg == "api_key_us":
        # update env variables
        # env_vars["ORG_ID"] = data.get('org_id') TODO remove?
        env_vars["DIGICERT_API_KEY_US"] = data.get('api_key')
        for key, value in env_vars.items():
            set_key(ENV_FILE, key, value)
        us_ping_get_account_values()
        return jsonify({"message": "Key received successfully!"})

    elif arg == "api_key_eu":
        # update env variables
        # env_vars["ORG_ID"] = data.get('org_id') TODO remove?
        env_vars["DIGICERT_API_KEY_EU"] = data.get('api_key')
        for key, value in env_vars.items():
            set_key(ENV_FILE, key, value)
        eu_ping_get_account_values()
        return jsonify({"message": "Key received successfully!"})


# Directory of past generated reports - once packaged, they will only persist per session
@app.route('/list-directory')
def list_directory():
    directory_path = resource_path('./templates/reports')
    # list all files in path
    try:
        files = [os.path.splitext(f)[0] for f in os.listdir(directory_path) if f.endswith('.html')]
    except FileNotFoundError:
        return "Directory not found.", 404

    return jsonify({"files": files, "directory": directory_path})


# custom static directory for report handling - html
@app.route('/reports/<filename>')
def custom_static(filename):
    directory_path = resource_path('./reports')
    return send_from_directory(directory_path, filename)


# custom static directory for report handling - css/javascript
@app.route('/c_static/<filename>')
def custom_static_js_css(filename):
    directory_path = resource_path('./static')
    return send_from_directory(directory_path, filename)


# endpoint for generating private key/csr for user
@app.route('/keypair')
def gen_keypair():
    key = crypto.generate_private_key_tab()
    csr = crypto.generate_csr_tab(key)
    keypair = json.loads(csr)
    return jsonify({"csr": keypair["csr"], "key": keypair["key"]})

# -------------------------- end routes -------------------------------- #


# -------------------------- functions -------------------------------- #

# default request helper
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

# -------------------------- end functions -------------------------------- #

# when the app is ran, this generates/checks for the ".Env" file. Stored at "C:\users\$user\appdata\local\digi-harbinger\.Env
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



def user_screen_size():
    user32 = ctypes.windll.user32
    screensize = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
    return screensize



# seperate flask function so waitress can be used (performance)
def start_flask(**server_kwargs):
    
    on_boot()
    app = server_kwargs.pop("app", None)
    server_kwargs.pop("debug", None)

    import waitress
    waitress.serve(app, **server_kwargs)
    




if __name__ == "__main__":
    
    # on close function
    def saybye():
        print("on_exit bye")
    
    screen_dimensions = user_screen_size()
    x = (screen_dimensions[0] / 2) - 475
    y = (screen_dimensions[1] / 2) - 475

    if '_PYI_SPLASH_IPC' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash  # this import error is okay - it's a pytest plugin
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
        width=950,
        height=950,
        browser_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        extra_flags = [f"--window-position={int(x)},{int(y)}"],
        on_shutdown=saybye,
    ).run()


# TODO REMOVE
    #app.run(host='127.0.0.1', debug=True)
