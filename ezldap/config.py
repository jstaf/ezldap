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
    if os.path.exists('~/.ezldap.yml'):
        return yaml.load(open('~/.ezldap.yml'))
    else:
        to_return = {
            'host': get_ldap_host(),
            'binddn': get_binddn(),
            'bindpw': None
        }
        return to_return


def readlines_to_dict(list_of_strings):
    '''
    Read a UNIX conf file as a key-value dictionary.
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
    ldap_conf = readlines_to_dict(open('/etc/openldap/ldap.conf').readlines())
    return ldap_conf['URI']


def get_binddn():
    '''
    Get the dn of the user you are connecting as using ldapsearch.
    If run as root, fetches the Manager dn from conf files.
    '''
    proc = subprocess.Popen('ldapsearch -x uid=`whoami`', stdout=subprocess.PIPE, shell=True)
    whoami = proc.stdout.readlines()
    whoami = list(map(lambda x: x.decode(), whoami))
    whoami_dict = readlines_to_dict(whoami)
    return whoami_dict['dn:']
