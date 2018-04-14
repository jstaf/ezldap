'''
Test ldap operations on a test instance of slapd.
'''

import pytest
import slapdtest
import ezldap

@pytest.fixture(scope='module')
def slapd():
    instance = slapdtest.SlapdObject()
    instance.openldap_schema_files = (
        'core.schema',
        'cosine.schema',
        'nis.schema',
        'inetorgperson.schema'
    )
    instance.start()
    # ldap OUs have not been setup yet in test instance, so we need to create them
    instance.ldapadd(open('tests/setup.ldif').read())
    #instance.ldapadd(open('/etc/openldap/schema/cosine.ldif').read())
    #instance.ldapadd(open('/etc/openldap/schema/nis.ldif').read())
    #instance.ldapadd(open('/etc/openldap/schema/inetorgperson.ldif').read())
    
    global config    
    config = {
        'host': instance.default_ldap_uri,
        'binddn': instance.root_dn,
        'bindpw': instance.root_pw,
        'groupdn': 'ou=Group,' + instance.suffix,
        'peopledn': 'ou=People,' + instance.suffix,
        'homedir': '/home'}
    con = ezldap.auto_bind(config)

    assert con.next_uidn() == 10000
    assert con.next_gidn() == 10000
    return con


def test_bind_success(slapd):
    assert slapd.whoami_s() == 'dn:cn=Manager,dc=slapd-test,dc=python-ldap,dc=org'


def test_add_group(slapd):
    slapd.add_group('testgroup', ldif_path='ezldap/templates/ldap-add-group.ldif', **config)
    assert len(slapd.get_group('testgroup')) == 1


#def test_add_user(test_add_group):
#    con.add_user('test1', 'testgroup', 'test1234',
#        ldif_path='ezldap/templates/ldap-add-user.ldif', **config)
#    assert len(con.get_user('test1')) == 1
