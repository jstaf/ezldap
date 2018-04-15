'''
Test ldap operations on a test instance of slapd.
'''

import ezldap

prefix = 'ezldap/templates/'

def test_bind_success(slapd):
    assert slapd.whoami_s() == 'dn:cn=Manager,dc=ezldap,dc=io'


def test_add_group(slapd, config):
    '''
    Test adding a group.
    '''
    slapd.add_group('testgroup', ldif_path=prefix + 'ldap-add-group.ldif', **config)
    assert len(slapd.get_group('testgroup')) == 1
    slapd.add_group('testgroup2', gid=50000, ldif_path=prefix + 'ldap-add-group.ldif', **config)
    assert len(slapd.get_group('testgroup2')) == 1


def test_add_user(slapd, config):
    '''
    Test adding a user to an existing group.
    '''
    slapd.add_group('adduser', gid=50001, ldif_path=prefix + 'ldap-add-group.ldif', **config)
    # by groupname
    slapd.add_user('user1', 'adduser', 'test1234', ldif_path=prefix + 'ldap-add-user.ldif', **config)
    assert len(slapd.get_user('user1')) == 1

    # by gid
    slapd.add_user('user2', None, 'test1234', gid=50001, ldif_path=prefix + 'ldap-add-user.ldif', **config)
    query = slapd.get_user('user2')
    assert len(query) == 1

    # is the password set correctly?
    passwd = query[0][1]['userPassword'][0].decode()
    assert ezldap.ssha_check(passwd, 'test1234')
