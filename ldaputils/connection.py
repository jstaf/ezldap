"""
Simplify LDAP connection to a one-liner.
"""

import os
import sys
import yaml
import getpass
import re

import ldap


def config(path='etc/config.yaml'):
    """
    Load LDAP details from config.yaml (or similar)
    """
    if not os.path.exists(path):
        sys.exit('Error: config file ({}), not found!'.format(path))
    with open(path, 'r') as settings:
        return yaml.load(settings)


def bind(config=config()):
    """
    A wrapper function to simplify connecting via a pre-existing config.
    Remember to unbind (con.unbind_s()) when done.
    """
    bind_password = config['binddn_pass']
    if bind_password is None:
        bind_password = getpass.getpass()

    connection = ldap.initialize(config['host'])
    connection.simple_bind_s(config['binddn'], bind_password)
    return connection


def base_dn(connection):
    """
    Detect the base DN from an LDAP connection.
    Uses the bind DN as a "hint".
    """
    whoami = connection.whoami_s()
    return re.findall(r'dc=.+$', whoami)[0]


def next_uidn(connection):
    """
    Determine the next available uid number in a directory tree.
    """
    users = connection.search_s(base_dn(connection), 2, '(uid=*)')
    if len(users) == 0:
        return config()['uidstart']

    uidns = get_attrib_list(users, 'uidNumber')
    uidns = [int(uidn) for uidn in uidns]
    return max(uidns) + 1


def next_gidn(connection):
    """
    Determine the next available gid number in a directory tree.
    """
    groups = connection.search_s(base_dn(connection), 2, '(objectClass=posixGroup)')
    if len(groups) == 0:
        return config()['gidstart']

    gidns = get_attrib_list(groups, 'gidNumber')
    gidns = [int(gidn) for gidn in gidns]
    return max(gidns) + 1


def get_attrib_list(query, name):
    """
    Grab all of a certain attribute from an LDAP search query.
    """
    attrs = [obj[1][name] for obj in query]
    # determine if attrs should be unpacked and decoded
    if all([len(attr) == 1 for attr in attrs]):
        attrs = [attr[0].decode() for attr in attrs]

    return attrs


