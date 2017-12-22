'''
Autodetect and retrieve configuration values from an active LDAP server.
Ideally the user should have to do nothing aside from specify a password.
'''

import os
import subprocess

import yaml

def config():
    '''
    Attempts to generate a dictionary of config values for LDAP details from 
    the following config files, in order:
    ~/.ezldap.yml, /etc/openldap/ldap.conf + /usr/bin/ldapwhoami
    '''
    if os.path.exists(os.path.expanduser('~/.ezldap/config.yml')):
        return yaml.load(open(os.path.expanduser('~/.ezldap/config.yml')))
    else:
        return guess_config()


def guess_config():
    base = get_base_dn()
    conf = {
        'host': get_ldap_host(),
        'binddn': get_current_dn(),
        'bindpw': None,
        'peopledn': None,
        'groupdn': None,
        'uidstart': 10000,
        'gidstart': 10000
    }
    return conf


def readlines_to_dict(list_of_strings):
    '''
    Read a UNIX conf file or LDIF output as a key-value dictionary.
    '''
    conf = {}
    for line in list_of_strings:
        if line[0] in ['#', '\n']:
            continue
        else:
            line_l = line.split()
            key = line_l.pop(0)
            conf[key] = line_l

    return conf


def get_ldap_host():
    '''
    Retrieves the LDAP host from /etc/openldap/ldap.conf.
    '''
    try:
        ldap_conf = readlines_to_dict(open('/etc/openldap/ldap.conf').readlines())
        return ldap_conf['URI']
    except KeyError:
        return None


def get_base_dn():
    '''
    Retrieves the base dn from /etc/openldap/ldap.conf.
    '''
    ldap_conf = readlines_to_dict(open('/etc/openldap/ldap.conf').readlines())
    try:
        return ldap_conf['BASE']
    except KeyError:
        return None


def get_current_dn():
    '''
    Get the dn of the user you are currently as using ldapsearch.
    '''
    try:
        proc = subprocess.Popen('ldapsearch -x uid=`whoami`', 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        whoami = proc.stdout.readlines()
        whoami = list(map(lambda x: x.decode(), whoami))
        whoami_dict = readlines_to_dict(whoami)
        return whoami_dict['dn:']
    except KeyError:
        return None


def get_current_group_dn():
    return None
