import json
import os
import sys
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from dotenv import dotenv_values, set_key


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



def generate_private_key():

    # generate key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    private_key_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # convert bytes to string for .Env
    private_key_str = private_key_bytes.decode('utf-8').replace('\n', '')

    # write to .env
    ENV_VARS["PRIVATE_KEY"] = private_key_str
    for key, value in ENV_VARS.items():
        set_key(ENV_FILE, key, value)
    return private_key_bytes


def generate_csr(key):
    key_bytes = serialization.load_pem_private_key(key, None)
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Testing"),           # ORG NAME
        x509.NameAttribute(NameOID.COMMON_NAME, "testing.local"),           # CN, SANS
    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("testing.local"),
            x509.DNSName("www.testing.local"),
        ]),
        critical=False,

    ).sign(key_bytes, hashes.SHA256())  # sign with our key

    csr_bytes = csr.public_bytes(serialization.Encoding.PEM)
    csr_string = csr_bytes.decode('utf-8').replace('\n', '')

    # write csr to .env
    ENV_VARS["CSR"] = csr_string
    for key, value in ENV_VARS.items():
        set_key(ENV_FILE, key, value)

    return csr_string


# ---------------- duplicate key and csr functions for seperate handling -------------------- #
def generate_private_key_tab():

    # generate key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    private_key_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # convert bytes to string for .Env
    private_key_str = private_key_bytes.decode('utf-8').replace('\n', '')

    # write to .env
    ENV_VARS["PRIVATE_KEY"] = private_key_str
    for key, value in ENV_VARS.items():
        set_key(ENV_FILE, key, value)
    return private_key_bytes


def generate_csr_tab(key):
    key_bytes = serialization.load_pem_private_key(key, None)
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Testing"),  # ORG NAME
        x509.NameAttribute(NameOID.COMMON_NAME, "testing.local"),  # CN, SANS
    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("testing.local"),
            x509.DNSName("www.testing.local"),
        ]),
        critical=False,
    ).sign(key_bytes, hashes.SHA256())  # sign with our key

    csr_bytes = csr.public_bytes(serialization.Encoding.PEM)
    csr_string = csr_bytes.decode('utf-8').replace('\n', '')

    private_key_str = key.decode('utf-8').replace('\n', '')
    # returns csr and key
    ENV_VARS["CSR"] = csr_string
    for key, value in ENV_VARS.items():
        set_key(ENV_FILE, key, value)

    data = {
        "csr": csr_string,
        "key": private_key_str
    }
    json_data = json.dumps(data)

    return json_data

