import pytest
import asyncio
import os
import sys

# local imports
from tests.crypto import generate_csr, generate_private_key
from tests.certificates import find_cert_id


# Custom resource path - returns normpath
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.normpath(os.path.join(base_path, relative_path))


# ---------- Pytest Fuxtures (shared parameters when tests are ran) ------------ #
@pytest.fixture(scope="module")
def shared_data():
    data = {}
    yield data


@pytest.fixture(scope="module")
def cert_id_for_downloads():
    data = find_cert_id()
    yield data


@pytest.fixture(scope="module")
def generate_keypair():
    data = generate_csr(generate_private_key())
    yield data


@pytest.hookimpl(optionalhook=True)
def pytest_html_report_title(report):
    report.title = "Digi-Harbinger"


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend(["<script type='text/javascript' src='{{url_for(\"custom_static_js_css\",filename=\"main.js\")}}'></script>"])


@pytest.fixture(scope="module")
def us_mode():
    data = ""
    yield data
# ---------- End ------------ #


def run_pytest(selected_tests):

    # resource path conversion
    resolved_tests = []
    for test in selected_tests:
        path, *test_name = test.split("::")                             # split path and test name (e.G., "./tests/account.Py::test_account_details")
        resolved_path = resource_path(path) 
        if test_name:
            resolved_test = f"{resolved_path}::{'::'.join(test_name)}"  # reconstruct
        else:
            resolved_test = resolved_path
        resolved_tests.append(resolved_test)

    original_argv = sys.argv                                            # save any current sys.Argv
    

    
    sys.argv = [                                                        # replace sys.Argv with pytest arguments 
        "pytest",                                                       # pytest command
        f"--html={resource_path('./templates/report.html')}",
        f"--css={resource_path('./static/css/custom.css')}",
        "--self-contained-html"
    ] + resolved_tests

    try:
        pytest.main()                                                   # run pytest
    finally:
        sys.argv = original_argv                                        # restore original sys.Argv

@pytest.mark.asyncio
async def process_defined_tests(selected_tests):
    await asyncio.to_thread(run_pytest, selected_tests)
    return

