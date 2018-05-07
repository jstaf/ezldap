'''
Test the ezldap CLI and ensure it works properly.
'''

import subprocess
import pytest
import ezldap


def syscall(call):
    '''
    Run syscall and return output.
    '''
    proc = subprocess.Popen(call, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            shell=True, universal_newlines=True)
    stdout, stderr = proc.communicate()
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


@pytest.mark.skip
def test_add_user(slapd):
    pass


def test_add_group(slapd):
    cli('add_group cli_testgroup')
    group1 = slapd.get_group('cli_testgroup')
    assert group1['cn'][0] == 'cli_testgroup'


def test_add_group_bygid(slapd):
    cli('add_group cli_testgroup2 44444')
    group2 = slapd.get_group('cli_testgroup2')
    assert group2['cn'][0] == 'cli_testgroup2'
    assert group2['gidNumber'][0] == 44444


@pytest.mark.skip
def test_add_to_group(slapd):
    pass


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
