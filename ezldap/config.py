'''
Autodetect and retrieve configuration values from an active LDAP server.
Ideally the user should have to do nothing aside from specify a password.
'''

import os
import subprocess
import yaml

def config(path=None):
    '''
    Attempts to generate a dictionary of config values for LDAP details from
    the following config files, in order:
    ~/.ezldap/config.yml, /etc/openldap/ldap.conf + /usr/bin/ldapwhoami
    '''
    if path is not None:
        return yaml.load(open(os.path.expanduser(path)))
    elif os.path.exists(os.path.expanduser('~/.ezldap/config.yml')):
        return yaml.load(open(os.path.expanduser('~/.ezldap/config.yml')))
    else:
        return guess_config()


def guess_config():
    base = get_ldap_conf_val('BASE')
    conf = {
        'host': get_ldap_conf_val('URI'),
        'binddn': get_current_dn(),
        'bindpw': None,
        'peopledn': 'ou=People,{}'.format(base),
        'groupdn': 'ou=Group,{}'.format(base),
        'homedir': '/home'
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


def get_ldap_conf_val(field):
    if os.path.exists('/etc/openldap/ldap.conf'):
        # redhat distros
        path = '/etc/openldap/ldap.conf'
    elif os.path.exists('/etc/ldap/ldap.conf'):
        # ubuntu
        path = '/etc/ldap/ldap.conf'
    else:
        return None

    try:
        ldap_conf = readlines_to_dict(open(path).readlines())
        return ldap_conf[field][0]
    except KeyError:
        return None


def get_current_dn():
    '''
    Get the dn of the user you are currently as using ldapsearch.
    '''
    try:
        proc = subprocess.Popen('ldapsearch -x uid=$(whoami)',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        whoami = [line.decode() for line in proc.stdout.readlines()]
        whoami_dict = readlines_to_dict(whoami)
        return whoami_dict['dn:'][0]
    except KeyError:
        return None
