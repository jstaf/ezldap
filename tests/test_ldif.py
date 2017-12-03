'''
Ensure that the LDIF templating is working correctly.
'''

import pytest

from ezldap import LDIF

template = 'config/ldap-add-group.ldif'

def test_templating():
    '''
    Does the LDIF properly fail on all the right fields
    '''
    with pytest.raises(KeyError) as err:
        LDIF(template)
        assert 'groupname' in str(err.value)

        LDIF(template, replacements={'groupname': 'test'})
        assert 'groupdn' in str(err.value)

        LDIF(template, replacements={
            'groupname': 'test', 
            'groupdn': 'ou=Group,dc=example,dc=com'})
        assert 'gid' in str(err.value)


def test_template_content():
    ldif = LDIF(template, replacements={
        'groupname': 'test', 
        'groupdn': 'dc=Group,dc=example,dc=com', 
        'gid': 10001})
    assert list(ldif.entries.keys())[0] == 'cn=test,dc=Group,dc=example,dc=com'
    vals = ldif.entries['cn=test,dc=Group,dc=example,dc=com']
    assert vals['cn'][0] == b'test'
    assert vals['gidNumber'][0] == b'10001'
