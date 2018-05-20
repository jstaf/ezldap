'''
Shared fixtures for multiple test modules.
(pytest autodetects this from its filename.)
'''

import subprocess
import pytest
import ezldap

PREFIX = 'ezldap/templates/'

def ping_slapd():
    return ezldap.ping('ldap://localhost')


@pytest.fixture(scope='session')
def config():
    return ezldap.config('tests/ezldap_config.yml')


@pytest.fixture(scope='session')
def slapd(docker_ip, docker_services, config):
    '''
    Spin up an OpenLDAP slapd instance via Docker for use by tests.
    '''
    docker_services.wait_until_responsive(timeout=15, pause=0.1, check=ping_slapd)
    return ezldap.auto_bind(config)


@pytest.fixture(scope='session')
def anon(docker_ip, docker_services, config):
    '''
    Same as slapd fixture, but an anonymous bind.
    '''
    docker_services.wait_until_responsive(timeout=15, pause=0.1, check=ping_slapd)
    return ezldap.Connection(config['host'])
