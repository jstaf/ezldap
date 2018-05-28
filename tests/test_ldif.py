'''
Ensure that the LDIF templating is working correctly.
'''

import pytest
import ldap3
from ezldap import ldif_read

template = 'ezldap/templates/add_group.ldif'
LDIF_PREFIX = 'tests/ldif/'

def test_incomplete_templating():
    '''
    Does the LDIF properly fail on all the right fields
    '''
    with pytest.raises(KeyError) as err:
        ldif_read(template, replacements={})
        assert 'groupname' in str(err.value)

        ldif_read(template, replacements={'groupname': 'test'})
        assert 'groupdn' in str(err.value)

        ldif_read(template, replacements={
            'groupname': 'test',
            'groupdn': 'ou=Group,dc=example,dc=com'})
        assert 'gid' in str(err.value)


def test_template_content():
    ldif = ldif_read(template, replacements={
        'groupname': 'test',
        'groupdn': 'dc=Group,dc=example,dc=com',
        'gid': 10001})
    assert ldif[0]['dn'][0] == 'cn=test,dc=Group,dc=example,dc=com'
    assert ldif[0]['cn'][0] == 'test'
    assert ldif[0]['gidNumber'][0] == '10001'


def test_read_ldif_change():
    ldif = ldif_read(LDIF_PREFIX+'test_ldif_change.ldif')
    assert ldif[0]['cn'][0][0] == ldap3.MODIFY_REPLACE
    assert ldif[0]['cn'][0][1][0] == 'New name'
    assert len(ldif[0]['mail']) == 2
    assert 'shadowLastChange' in ldif[0].keys()


def test_dash_in_file():
    ldif = ldif_read(LDIF_PREFIX+'test_ldif_change.ldif')
    for key in ldif[0].keys():
        assert key.strip()[0] not in {'#', '-'}
