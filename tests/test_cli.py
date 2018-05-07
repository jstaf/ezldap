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


@pytest.mark.skip
def test_search_dn(slapd):
    pass


@pytest.mark.skip
def test_add_user(slapd):
    pass


@pytest.mark.skip
def test_add_group(slapd):
    pass


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
