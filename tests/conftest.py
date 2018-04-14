'''
Shared fixtures for multiple test modules.
(pytest autodetects this from its filename.)
'''

import os
import json
import subprocess
import pytest


def ping_slapd():
    '''
    Return true if we can contact slapd.
    '''
    try:
        stdout = subprocess.check_output('ldapsearch -x', shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


@pytest.fixture(scope='session')
def slapd(docker_ip, docker_services):
    docker_services.wait_until_responsive(timeout=15, pause=0.5, check=ping_slapd)
    return ezldap.auto_bind(ezldap.config('tests/ezldap_config.yml'))
