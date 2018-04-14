'''
Test ldap operations on a test instance of slapd.
'''

import pytest
import ezldap


def test_bind_success(slapd):
    assert slapd.whoami_s() == 'dn:cn=Manager,dc=ezldap,dc=io'


def test_add_group(slapd, config):
    slapd.add_group('testgroup', ldif_path='ezldap/templates/ldap-add-group.ldif', **config)
    assert len(slapd.get_group('testgroup')) == 1


#def test_add_user(test_add_group):
#    con.add_user('test1', 'testgroup', 'test1234',
#        ldif_path='ezldap/templates/ldap-add-user.ldif', **config)
#    assert len(con.get_user('test1')) == 1
