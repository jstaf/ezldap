'''
Shared fixtures for multiple test modules.
(pytest autodetects this from its filename.)
'''

import subprocess
import pytest
import ezldap


def ping_slapd():
    '''
    Return true if we can contact slapd.
    '''
    try:
        stdout = subprocess.check_output('ldapsearch -x -b dc=ezldap,dc=io', shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


@pytest.fixture(scope='session')
def slapd(docker_ip, docker_services):
    '''
    Spin up an OpenLDAP slapd instance via Docker for use by tests.
    '''
    docker_services.wait_until_responsive(timeout=15, pause=0.1, check=ping_slapd)
    return ezldap.auto_bind(ezldap.config('tests/ezldap_config.yml'))
