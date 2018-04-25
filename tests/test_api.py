'''
Test ldap operations on a test instance of slapd.
'''

import ezldap

prefix = 'ezldap/templates/'

def test_bind_success(slapd):
    '''
    If this fails, the bind has failed.
    '''
    assert slapd.who_am_i() == 'dn:cn=Manager,dc=ezldap,dc=io'


def test_base_dn(slapd):
    '''
    Do we retrieve the correct base dn?
    '''
    assert slapd.base_dn() == 'dc=ezldap,dc=io'


def test_search_list(slapd):
    '''
    Does search_list() return the correct number of entries?
    '''
    assert len(slapd.search_list('(objectClass=organizationalUnit)')) == 2
    assert len(slapd.search_list('(objectClass=applicationProcess)')) == 0


def test_search_list_encapsulation(slapd):
    '''
    Dump entire DIT and ensure every attribute of entries returned is
    encapsulated in a list.
    '''
    query = slapd.search_list()
    for res in query:
        for v in res.values():
            assert isinstance(v, list)


def test_search_list_t(slapd):
    query = slapd.search_list_t('(objectClass=organizationalUnit)')
    assert set(query['ou']) == {'Group', 'People'}
    fail = slapd.search_list_t('(objectClass=applicationProcess)')
    assert set(fail['dn']) == set()


def test_search_df(slapd):
    '''
    Does the search_df function return a Pandas DataFrame and is it collapsing
    lists to a "|" delimited string correctly?
    '''
    # dump entire DIT
    df = slapd.search_df()
    ezldapio = df[df['dn'] == 'dc=ezldap,dc=io']
    assert '|' not in ezldapio['dc'].iloc[0]
    assert '|' in ezldapio['objectClass'].iloc[0]
    assert 'organization' in ezldapio['objectClass'].iloc[0]
    assert 'dcObject' in ezldapio['objectClass'].iloc[0]


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


#def test_add_to_group(slapd):
#    slapd.add_group('group1')
#    slapd.add_group('user3')
#    slapd.add_to_group('user3', 'group1')
#    query = slapd.get_group('')
