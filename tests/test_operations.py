'''
Test ldap operations on a test instance of slapd.
'''

import os

import pytest
import slapdtest
import ezldap

@pytest.fixture(scope='module')
def slapd():
    instance = slapdtest.SlapdObject()
    instance.start()
    
    global con
    global config
    global binddn
    
    binddn = instance.root_dn
    config = {
        'host': instance.ldap_uri,
        'binddn': instance.root_dn,
        'bindpw': instance.root_pw,
        'groupdn': 'ou=Group,' + instance.suffix,
        'peopledn': 'ou=People,' + instance.suffix,
        'homedir': '/home'}
    con = ezldap.auto_bind(config)
    # ldap OUs have not been setup yet in test instance,
    # so we need to create them
    #os.system('ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/cosine.ldif')
    #os.system('ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/nis.ldif')
    #os.system('ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/inetorgperson.ldif')
    #os.system('ldapadd -Y EXTERNAL -H ldapi:/// -f tests/setup.ldif')
    os.system('ldapadd -x -H {} -D {} -w {} -f /etc/openldap/schema/cosine.ldif'.format(config['host'], config['binddn'], config['bindpw']))
    os.system('ldapadd -x -H {} -D {} -w {} -f /etc/openldap/schema/nis.ldif'.format(config['host'], config['binddn'], config['bindpw']))
    os.system('ldapadd -x -H {} -D {} -w {} -f /etc/openldap/schema/inetorgperson.ldif'.format(config['host'], config['binddn'], config['bindpw']))
    os.system('ldapadd -x -H {} -D {} -w {} -f tests/setup.ldif'.format(config['host'], config['binddn'], config['bindpw']))
    #con.ldif_add(ezldap.LDIF('tests/setup.ldif'))
    assert con.next_uidn() == 10000
    assert con.next_gidn() == 10000


def test_bind_success(slapd):
    assert con.whoami_s() == 'dn:' + binddn


@pytest.fixture(scope='module')
def test_no_entries_yet(slapd):
    assert con.next_uidn() == 10000
    assert con.next_gidn() == 10000


#@pytest.fixture(scope='module')
def test_add_group(test_no_entries_yet):
    con.add_group('testgroup', ldif_path='ezldap/templates/ldap-add-group.ldif', **config)
    assert len(con.get_group('testgroup')) == 1


#def test_add_user(test_add_group):
#    con.add_user('test1', 'testgroup', 'test1234',
#        ldif_path='ezldap/templates/ldap-add-user.ldif', **config)
#    assert len(con.get_user('test1')) == 1
