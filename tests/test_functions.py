

def test_scripts():

    test_group = {
        "account": [
            "./tests/account.py::test_account_details",
            "./tests/account.py::test_list_permissions",
            "./tests/account.py::test_list_api_keys",
            "./tests/account.py::test_list_product_list",
            "./tests/account.py::test_list_users",
            "./tests/account.py::test_add_user",
            "./tests/account.py::test_delete_user",
            "./tests/account.py::test_list_service_users",

        ],
        "organizations": [
            "./tests/organizations.py::test_list_orgs",
            "./tests/organizations.py::test_submit_new_org",
            "./tests/organizations.py::test_org_info",
            "./tests/organizations.py::test_deactivate_org",
            "./tests/organizations.py::test_activate_org",
            "./tests/organizations.py::test_org_validation_details",
            "./tests/organizations.py::test_delete_org"
        ],
        "domains": [
            "./tests/domains.py::test_list_domains",
            "./tests/domains.py::test_add_domain",
            "./tests/domains.py::test_deactivate_domain",
            "./tests/domains.py::test_activate_domain",
            "./tests/domains.py::test_domain_info",
            "./tests/domains.py::test_domain_change_dcv_dns_txt_token",
            "./tests/domains.py::test_domain_change_dcv_cname",
            "./tests/domains.py::test_domain_change_dcv_http_token",
            "./tests/domains.py::test_delete_domain",
        ],
        "orders": [
            "./tests/orders.py::test_list_orders",
            "./tests/orders.py::test_order_validation_status",
            "./tests/orders.py::test_ssl_dv_geotrust_flex",
            "./tests/orders.py::test_ssl_dv_rapidssl",
            "./tests/orders.py::test_ssl_basic",
            "./tests/orders.py::test_ssl_securesite_flex",
            "./tests/orders.py::test_ssl_securesite_pro",
            "./tests/orders.py::test_ssl_plus",
            "./tests/orders.py::test_ssl_multi_domain",
            "./tests/orders.py::test_ssl_type_hint"
        ],
        "certificates": [
            "./tests/certificates.py::test_download_certificate_default_pem",
            "./tests/certificates.py::test_download_certificate_default",
            "./tests/certificates.py::test_download_certificate_default_cer",
            "./tests/certificates.py::test_download_certificate_apache",
            "./tests/certificates.py::test_download_certificate_pem_all",
            "./tests/certificates.py::test_download_certificate_pem_nointermediate",
            "./tests/certificates.py::test_download_certificate_pem_noroot",
            "./tests/certificates.py::test_download_certificate_p7b",
            "./tests/certificates.py::test_download_certificate_cer",
        ],
        "tools": [
            "./tests/tools.py::test_list_replacement_benefits"
        ],
        "containers": [
            "./tests/containers.py::test_list_containers",
            "./tests/containers.py::test_container_info"
        ]
    }
    return test_group


def cis_test_scripts():

    cis_test_group = {
        
        "issuance": [
            "./tests_cis/issuance.py::test_issuance_heartbeat",

        ],
        "validation": [
            "./tests_cis/validation.py::test_validation_heartbeat",

        ],
    }
    
    return cis_test_group