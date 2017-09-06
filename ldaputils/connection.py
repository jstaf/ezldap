"""
Simplify LDAP connection to a one-liner.
"""

import os
import sys
import yaml
import getpass

import ldap


def config(path='config.yaml'):
    """
    Load LDAP details from config.yaml (or similar)
    """
    if not os.path.exists(path):
        sys.exit('Error: config file ({}), not found!'.format(path))
    with open(path, 'r') as settings:
        return yaml.load(settings)


def connect(config=config()):
    """
    A wrapper function to simplify connecting via a pre-existing config.
    """
    bind_password = config['manager_pass']
    if bind_password is None:
        bind_password = getpass.getpass()

    connection = ldap.initialize(config['host'])
    connection.simple_bind_s(config['manager'], bind_password)
    return connection


