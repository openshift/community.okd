from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.community.okd.plugins.module_utils.openshift_ldap import (
    openshift_equal_dn,
    openshift_ancestorof_dn
)
import pytest

try:
    import ldap
except ImportError:
    pytestmark = pytest.mark.skip("This test requires the python-ldap library")


def test_equal_dn():

    assert openshift_equal_dn("cn=unit,ou=users,dc=ansible,dc=com", "cn=unit,ou=users,dc=ansible,dc=com")
    assert not openshift_equal_dn("cn=unit,ou=users,dc=ansible,dc=com", "cn=units,ou=users,dc=ansible,dc=com")
    assert not openshift_equal_dn("cn=unit,ou=users,dc=ansible,dc=com", "cn=unit,ou=user,dc=ansible,dc=com")
    assert not openshift_equal_dn("cn=unit,ou=users,dc=ansible,dc=com", "cn=unit,ou=users,dc=ansible,dc=org")


def test_ancestor_of_dn():

    assert not openshift_ancestorof_dn("cn=unit,ou=users,dc=ansible,dc=com", "cn=unit,ou=users,dc=ansible,dc=com")
    assert not openshift_ancestorof_dn("cn=unit,ou=users,dc=ansible,dc=com", "cn=units,ou=users,dc=ansible,dc=com")
    assert openshift_ancestorof_dn("ou=users,dc=ansible,dc=com", "cn=john,ou=users,dc=ansible,dc=com")
    assert openshift_ancestorof_dn("ou=users,dc=ansible,dc=com", "cn=mathew,ou=users,dc=ansible,dc=com")
    assert not openshift_ancestorof_dn("ou=users,dc=ansible,dc=com", "cn=mathew,ou=users,dc=ansible,dc=org")
