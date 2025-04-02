import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.x509 import ocsp
import ssl
from urllib.parse import urlparse
from datetime import datetime
import sys

def get_certificate_from_url(url):
    """Fetch the SSL certificate from a given URL"""
    try:
        # Parse URL to get hostname
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = 'https://' + url  # Assume HTTPS if no scheme provided
            parsed_url = urlparse(url)
        
        hostname = parsed_url.hostname
        if not hostname:
            raise ValueError("Invalid URL - no hostname found")

        # Create a secure SSL context
        context = ssl.create_default_context()
        
        # Connect to the server and get the certificate
        with ssl.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert_der = ssock.getpeercert(binary_form=True)
                
        if not cert_der:
            raise ValueError("No certificate returned from server")
            
        # Parse the certificate
        cert = x509.load_der_x509_certificate(cert_der, default_backend())
        return cert
        
    except Exception as e:
        raise RuntimeError(f"Failed to fetch certificate from {url}: {str(e)}")

def get_ocsp_url(cert):
    """Extract OCSP URL from certificate"""
    try:
        # Look for Authority Information Access extension
        for extension in cert.extensions:
            if extension.oid == x509.oid.ExtensionOID.AUTHORITY_INFORMATION_ACCESS:
                for access_description in extension.value:
                    if access_description.access_method == x509.oid.AuthorityInformationAccessOID.OCSP:
                        return access_description.access_location.value
        return None
    except Exception as e:
        raise RuntimeError(f"Failed to extract OCSP URL: {str(e)}")

def perform_ocsp_check(cert, issuer_cert=None):
    """Perform OCSP check for a certificate"""
    try:
        # Get OCSP URL from certificate
        ocsp_url = get_ocsp_url(cert)
        if not ocsp_url:
            raise RuntimeError("No OCSP URL found in certificate")
        
        # If issuer cert not provided, try to get it from AIA
        if issuer_cert is None:
            issuer_cert = get_issuer_certificate(cert)
        
        if issuer_cert is None:
            raise RuntimeError("Could not obtain issuer certificate")
        
        # Build OCSP request
        builder = ocsp.OCSPRequestBuilder()
        builder = builder.add_certificate(cert, issuer_cert, hashes.SHA1())
        request = builder.build()
        
        # Send OCSP request
        response = requests.post(
            ocsp_url,
            data=request.public_bytes(serialization.Encoding.DER),
            headers={'Content-Type': 'application/ocsp-request'}
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"OCSP server returned HTTP {response.status_code}")
        
        # Parse OCSP response
        ocsp_response = ocsp.load_der_ocsp_response(response.content)
        
        return ocsp_response
        
    except Exception as e:
        raise RuntimeError(f"OCSP check failed: {str(e)}")

def get_issuer_certificate(cert):
    """Attempt to get the issuer certificate from certificate's AIA extension"""
    try:
        for extension in cert.extensions:
            if extension.oid == x509.oid.ExtensionOID.AUTHORITY_INFORMATION_ACCESS:
                for access_description in extension.value:
                    if access_description.access_method == x509.oid.AuthorityInformationAccessOID.CA_ISSUERS:
                        issuer_url = access_description.access_location.value
                        issuer_resp = requests.get(issuer_url)
                        if issuer_resp.status_code == 200:
                            issuer_cert = x509.load_der_x509_certificate(
                                issuer_resp.content, default_backend()
                            )
                            return issuer_cert
        return None
    except Exception as e:
        print(f"Warning: Could not fetch issuer certificate: {str(e)}", file=sys.stderr)
        return None

def format_html_result(url, messages, is_valid):
    """Format the results as a styled HTML div"""
    status_color = "#4CAF50" if is_valid else "#F44336"
    status_text = "VALID" if is_valid else "INVALID"
    
    messages_html = "\n".join([f'<div class="message">{msg}</div>' for msg in messages])
    
    html = f"""
<div class="certificate-report ocsp_report" overflow: hidden;">
    <div >
        <h2 class="ok">OCSP Check Result for {url}: {status_text}</h2>
    </div>
    <div>
        {messages_html}
    </div>
</div>
<style>
.message {{
    margin: 8px 0;
    padding: 8px 12px;
    border-left: 4px solid #2196F3;
    background-color: white;
    border-radius: 0 4px 4px 0;
}}
.message.warning {{
    border-left-color: #FFC107;
    background-color: #FFF8E1;
}}
.message.error {{
    border-left-color: #F44336;
    background-color: #FFEBEE;
}}
.message.success {{
    border-left-color: #4CAF50;
    background-color: #E8F5E9;
}}
</style>
    """
    return html

def check_certificate_revocation(url):
    """Main function to check certificate revocation status via OCSP"""
    messages = []
    try:
        messages.append(f'<p >Checking certificate for: {url} </p>')
        
        # Step 1: Get certificate from URL
        cert = get_certificate_from_url(url)
        messages.append("<p>✓ Certificate obtained successfully</p>")
        
        # Step 2: Get issuer certificate
        issuer_cert = get_issuer_certificate(cert)
        if issuer_cert:
            messages.append("<p>✓ Issuer certificate obtained</p>")
        else:
            messages.append('<p class="warning">⚠ Could not obtain issuer certificate - will try OCSP anyway</p>')
        
        # Step 3: Perform OCSP check
        ocsp_response = perform_ocsp_check(cert, issuer_cert)
        
        # Interpret OCSP response
        if ocsp_response.response_status == ocsp.OCSPResponseStatus.SUCCESSFUL:
            messages.append("<p>✓ OCSP response received successfully</p>")
            
            # Check certificate status
            if ocsp_response.certificate_status == ocsp.OCSPCertStatus.GOOD:
                messages.append('<p class="success">✅ Certificate is valid (not revoked)</p>')
                messages.append(f"  This Update: {ocsp_response.this_update_utc}")
                if ocsp_response.next_update_utc:
                    messages.append(f"  Next Update: {ocsp_response.next_update_utc}")
                return format_html_result(url, messages, True)
            elif ocsp_response.certificate_status == ocsp.OCSPCertStatus.REVOKED:
                revoked_info = ocsp_response.revocation_time
                reason = ocsp_response.revocation_reason.name if ocsp_response.revocation_reason else "unspecified"
                messages.append(f'<p class="error">❌ Certificate REVOKED since {revoked_info} (reason: {reason})</p>')
                return format_html_result(url, messages, False)
            else:
                messages.append('<p class="warning">⚠ Certificate status unknown</p>')
                return format_html_result(url, messages, False)
        else:
            status = ocsp_response.response_status.name
            messages.append(f'<p class="error">❌ OCSP check failed with status: {status}</p>')
            return format_html_result(url, messages, False)
            
    except Exception as e:
        messages.append(f'<p class="error">❌ Error during OCSP check: {str(e)}</p>')
        return format_html_result(url, messages, False)

if __name__ == "__main__":
    url = "example.com"  # Replace with your target URL or get from command line
    html_result = check_certificate_revocation(url)
    
    # For command line use, we'll print the HTML
    print("Content-Type: text/html\n")
    print(html_result)