'''
Ensure that the LDIF templating is working correctly.
'''

import pytest
from io import StringIO

from ezldap import ldif_read

template = 'ezldap/templates/ldap-add-group.ldif'

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


@pytest.mark.skip
def test_dash_in_file():
    ldif_read('tests/setup.ldif')
