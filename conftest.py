import pytest
import asyncio
import os
import sys

# local imports
from tests.crypto import generate_csr, generate_private_key
from tests.certificates import find_cert_id


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.normpath(os.path.join(base_path, relative_path))


pytest_plugins = ('pytest_asyncio')


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


def run_pytest(selected_tests):

    # resource path conversion
    resolved_tests = []
    for test in selected_tests:
        # split path and test name (e.G., "./tests/account.Py::test_account_details")
        path, *test_name = test.split("::")
        resolved_path = resource_path(path)
        # reconstruct 
        if test_name:
            resolved_test = f"{resolved_path}::{'::'.join(test_name)}"
        else:
            resolved_test = resolved_path
        resolved_tests.append(resolved_test)

    original_argv = sys.argv # save any current sys.Argv
    

    # replace sys.Argv with pytest arguments 
    sys.argv = [
        "pytest",  # pytest command
        f"--html={resource_path('./templates/report.html')}",
        f"--css={resource_path('./static/css/custom.css')}",
        "--self-contained-html"
    ] + resolved_tests

    try:
        # run pytest
        pytest.main(plugins=['pytest_html'])
    finally:
        # restore original sys.Argv
        sys.argv = original_argv

@pytest.mark.asyncio
async def process_defined_tests(selected_tests):
    await asyncio.to_thread(run_pytest, selected_tests)
    return

