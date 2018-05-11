'''
Test the ezldap CLI and ensure it works properly.
'''

import subprocess
import pytest
import ezldap

PREFIX = 'ezldap/templates/'

def syscall(call):
    '''
    Run syscall and return output.
    '''
    proc = subprocess.Popen(call, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            shell=True, universal_newlines=True)
    stdout, stderr = proc.communicate()
    if proc.returncode > 0:
        raise subprocess.SubprocessError(stdout)

    return stdout


def cli(call):
    return syscall('EZLDAP_CONFIG=tests/ezldap_config.yml ezldap ' + call)


def test_search(slapd):
    '''
    Does the search CLI successfully spit out a nice LDIF?
    '''
    stdout = cli('search "(objectClass=organizationalUnit)"')
    assert 'dn: ou=Group,dc=ezldap,dc=io' in stdout
    assert 'dn: ou=People,dc=ezldap,dc=io' in stdout


def test_search_dn(slapd):
    stdout = cli('search_dn Manager')
    assert 'cn=Manager,dc=ezldap,dc=io' in stdout


def test_add_group(slapd):
    cli('add_group --ldif {}/add_group.ldif cli_testgroup'.format(PREFIX))
    group1 = slapd.get_group('cli_testgroup')
    assert group1['cn'][0] == 'cli_testgroup'


def test_add_group_bygid(slapd):
    cli('add_group --ldif {}/add_group.ldif cli_testgroup2 44444'.format(PREFIX))
    group2 = slapd.get_group('cli_testgroup2')
    assert group2['cn'][0] == 'cli_testgroup2'
    assert group2['gidNumber'][0] == 44444


def test_add_user_nogroup(slapd):
    '''
    Are users properly created when no group exists?
    '''
    username = 'cli_testuser'
    cli('add_user '
        '--ldif-user {}/add_user.ldif '
        '--ldif-group {}/add_group.ldif '
        '--ldif-add-to-group {}/add_to_group.ldif '
        '{}'.format(PREFIX, PREFIX, PREFIX, username))
    user = slapd.get_user(username)
    assert user['uid'][0] == username
    group = slapd.get_group(username)
    assert group['cn'][0] == username
    assert username in group['memberUid']


def test_add_user_wgroup(slapd):
    '''
    Are users properly created and added to the group when the group already exists?
    '''
    username, groupname = 'cli_testuser_wgroup', 'cli_user_wgroup'
    cli('add_group --ldif {}/add_group.ldif {}'.format(PREFIX, groupname))
    cli('add_user '
        '--ldif-user {}/add_user.ldif '
        '--ldif-group {}/add_group.ldif '
        '--ldif-add-to-group {}/add_to_group.ldif '
        '{} {}'.format(PREFIX, PREFIX, PREFIX, username, groupname))
    group = slapd.get_group(groupname)
    assert username in group['memberUid']
    user = slapd.get_user(username)
    assert user['uid'][0] == username


def test_add_to_group(slapd):
    username = 'cli_ag_user'
    groupname = 'cli_ag'
    cli('add_user '
        '--ldif-user {}/add_user.ldif '
        '--ldif-group {}/add_group.ldif '
        '--ldif-add-to-group {}/add_to_group.ldif '
        '{}'.format(PREFIX, PREFIX, PREFIX, username))
    cli('add_group --ldif {}/add_group.ldif {}'.format(PREFIX, groupname))
    cli('add_to_group --ldif {}/add_to_group.ldif {} {}'.format(PREFIX, username, groupname))
    group = slapd.get_group(groupname)
    assert username in group['memberUid']


@pytest.mark.skip
def test_change_home(slapd):
    pass


@pytest.mark.skip
def test_change_shell(slapd):
    pass


@pytest.mark.skip
def test_change_pw(slapd):
    pass


@pytest.mark.skip
def test_check_pw(slapd):
    pass
