from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.community.okd.plugins.module_utils.openshift_ldap import (
    validate_ldap_sync_config,
)


def test_missing_url():
    config = dict(
        kind="LDAPSyncConfig",
        apiVersion="v1",
        insecure=True
    )
    err = validate_ldap_sync_config(config)
    assert err == "url should be non empty attribute."


def test_binddn_and_bindpwd_linked():
    """
        one of bind_dn and bind_pwd cannot be set alone
    """
    config = dict(
        kind="LDAPSyncConfig",
        apiVersion="v1",
        url="ldap://LDAP_SERVICE_IP:389",
        insecure=True,
        bindDN="cn=admin,dc=example,dc=org"
    )

    credentials_error = "bindDN and bindPassword must both be specified, or both be empty."

    assert validate_ldap_sync_config(config) == credentials_error

    config = dict(
        kind="LDAPSyncConfig",
        apiVersion="v1",
        url="ldap://LDAP_SERVICE_IP:389",
        insecure=True,
        bindPassword="testing1223"
    )

    assert validate_ldap_sync_config(config) == credentials_error


def test_insecure_connection():
    config = dict(
        kind="LDAPSyncConfig",
        apiVersion="v1",
        url="ldaps://LDAP_SERVICE_IP:389",
        insecure=True,
    )

    assert validate_ldap_sync_config(config) == "Cannot use ldaps scheme with insecure=true."

    config.update(dict(
        url="ldap://LDAP_SERVICE_IP:389",
        ca="path/to/ca/file"
    ))

    assert validate_ldap_sync_config(config) == "Cannot specify a ca with insecure=true."
