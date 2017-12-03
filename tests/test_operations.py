'''
Test ldap operations on a test instance of slapd.
'''

import pytest
import slapdtest

import ezldap

@pytest.fixture(scope='module')
def slapd():
    instance = slapdtest.SlapdObject()
    instance.start()


