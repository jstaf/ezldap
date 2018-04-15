'''
Bind to an LDAP directory and perform various operations.
'''

import sys
import getpass
import re
from collections import OrderedDict

import ldap
import ldap.modlist
from ldap.ldapobject import LDAPObject

from .ldif import LDIF
from .password import ssha_passwd
from .config import config


def get_attrib_list(query, name):
    """
    Grab all of a certain attribute from an LDAP search query.
    """
    attrs = [obj[1][name] for obj in query]
    # determine if attrs should be unpacked and decoded
    if all([len(attr) == 1 for attr in attrs]):
        attrs = [attr[0].decode() for attr in attrs]

    return attrs


def auto_bind(conf=None):
    '''
    Automatically detects LDAP config values and returns a directory binding.
    '''
    if conf is None:
        conf = config()

    uri = conf['host']
    binding = LDAP(uri)
    if uri.startswith('ldaps://'):
        try:
            binding.start_tls_s()
        except ldap.PROTOCOL_ERROR as e:
            raise ldap.PROTOCOL_ERROR('TLS appears to be unsupported.') from e
        except ldap.CONNECT_ERROR as e:
            # give some helpful advice and rethrow
            raise ldap.CONNECT_ERROR(
                'Your certificate is untrusted - this is either an SELinux issue or '
                'your LDAP SSL has not been setup correctly.') from e

    if conf['bindpw'] is None:
        print('Enter bind DN password...', file=sys.stderr)
        conf['bindpw'] = getpass.getpass()

    binding.simple_bind_s(conf['binddn'], conf['bindpw'])

    return binding


class LDAP(LDAPObject):
    '''
    An object-oriented wrapper around an LDAP connection.
    Used to make pyldap's LDAPObject even easier to use.
    To automatically create a binding use auto_bind() instead.
    '''

    def __init__(self, host):
        super().__init__(host, trace_file=sys.stderr, trace_stack_limit=None)


    def __enter__(self):
        return self


    def __exit__(self, type_, value, traceback):
        """
        Auto-unbind when used with "with"
        """
        self.unbind_s()


    def base_dn(self):
        """
        Detect the base DN from an LDAP connection.
        Uses the bind DN as a "hint".
        """
        whoami = self.whoami_s()
        return re.findall(r'dc=.+$', whoami)[0]


    def search_safe(self, basedn=None, filter='(objectClass=*)',
            scope=ldap.SCOPE_SUBTREE):
        '''
        A wrapper around search_s that returns empty lists instead of exceptions
        when no results are found. If basedn is None, the directory base DN will
        be used.
        '''
        if basedn is None:
            basedn = self.base_dn()

        #TODO - implement paging limits to avoid ldap.SIZELIMIT_EXCEEDED
        #for non admin binds

        try:
            return self.search_ext_s(basedn, scope, filterstr=filter)
        except ldap.NO_SUCH_OBJECT:
            return []


    def next_uidn(self, uidstart=10000):
        """
        Determine the next available uid number in a directory tree.
        """
        users = self.search_safe(self.base_dn(), '(uid=*)')
        if len(users) == 0:
            return uidstart

        uidns = get_attrib_list(users, 'uidNumber')
        uidns = [int(uidn) for uidn in uidns]
        return max(uidns) + 1


    def next_gidn(self, gidstart=10000):
        """
        Determine the next available gid number in a directory tree.
        """
        groups = self.search_safe(self.base_dn(), '(objectClass=posixGroup)')
        if len(groups) == 0:
            return gidstart

        gidns = get_attrib_list(groups, 'gidNumber')
        gidns = [int(gidn) for gidn in gidns]
        return max(gidns) + 1


    def get_user(self, user, basedn=None, index='uid'):
        '''
        Return given user. Searches entire directory if no base search dn given.
        '''
        if basedn is None:
            basedn = self.base_dn()

        return self.search_safe(basedn, '({}={})'.format(index, user))


    def get_group(self, group, basedn=None, index='cn'):
        '''
        Return a given group. Searches entire directory if no base search dn given.
        '''
        if basedn is None:
            basedn = self.base_dn()

        return self.search_safe(basedn, '({}={})'.format(index, group))


    def ldif_add(self, ldif):
        """
        Perform an add operation using an LDIF object.
        """
        for dn, attrs in ldif.entries.items():
            self.add_s(dn, ldap.modlist.addModlist(attrs))


    def ldif_modify(self, ldif):
        """
        Perform an LDIF modify operation from an LDIF object.
        """
        for dn, attrs in ldif.entries.items():
            modlist = _create_modify_modlist(attrs)
            self.modify_s(dn, modlist)


    def modify_replace(self, dn, attrib, value):
        '''
        Change a single attribute on an object.
        '''
        self.modify_s(dn, [(ldap.MOD_REPLACE, attrib, to_bytes(value))])


    def modify_add(self, dn, attrib, value):
        '''
        Add a single attribute to an object.
        '''
        self.modify_s(dn, [(ldap.MOD_ADD, attrib, to_bytes(value))])


    def modify_delete(self, dn, attrib, value=None):
        '''
        Delete a single attribute from an object.
        If value is None, deletes all attributes of that name.
        '''
        self.modify_s(dn, [(ldap.MOD_DELETE, attrib, to_bytes(value))])


    def add_group(self, groupname,
        ldif_path='~/.ezldap/ldap-add-group.ldif', **kwargs):
        """
        Adds a group from an LDIF template.
        """
        replace = {'groupname': groupname, 'gid': self.next_gidn()}
        replace.update(config())
        replace.update(kwargs)

        ldif = LDIF(ldif_path, replace)
        self.ldif_add(ldif)


    def add_user_to_group(self, username, groupname,
        ldif_path='~/.ezldap/ldap-add-user-to-group.ldif', **kwargs):
        """
        Adds a user to a group.
        The user and group in question must already exist.
        """
        replace = {
                'username': username,
                'groupname': groupname,
                'userdn': None}

        replace.update(config())
        replace.update(kwargs)
        if replace['userdn'] is None:
            try:
                replace['userdn'] = self.get_user(username, self.base_dn())[0][0]
            except IndexError:
                raise ValueError('User does not exist')

        ldif = LDIF(ldif_path, replace)
        self.ldif_modify(ldif)


    def add_user(self, username, groupname, password,
        ldif_path='~/.ezldap/ldap-add-user.ldif', **kwargs):
        '''
        Adds a user. Does not create or modify groups.
        "groupname" may be None if "gid" is specified.
        '''
        replace = {
            'username': username,
            'user_password': ssha_passwd(password),
            'gid': None,
            'uid': None}

        replace.update(config())
        replace.update(kwargs)
        if replace['uid'] is None:
            replace['uid'] = self.next_uidn()

        if replace['gid'] is None:
            try:
                replace['gid'] = int(get_attrib_list(self.get_group(groupname, self.base_dn()), 'gidNumber')[0])
            except IndexError:
                raise ValueError('Group does not exist')

        ldif = LDIF(ldif_path, replace)
        self.ldif_add(ldif)


def to_bytes(value):
    if not isinstance(value, bytes):
        return str(value).encode()
    else:
        return value


def _create_modify_modlist(attrs):
    '''
    We need to carefully massage our LDIF object to a
    pyldap modlist because the pyldap API is super awkward.
    Ref: https://www.python-ldap.org/en/latest/reference/ldap.html#ldap.LDAPObject.modify_ext_s
    '''
    changes = OrderedDict()
    changes['delete'] = ldap.MOD_DELETE
    changes['replace'] = ldap.MOD_REPLACE
    changes['add'] = ldap.MOD_ADD

    modlist = []
    for change_type in changes.keys():
        # skip change types that don't occur
        if change_type not in attrs.keys():
            continue

        # else iterate over those values of change type
        for attrib_name in attrs[change_type]:
            attrib_name = attrib_name.decode()
            try:
                modlist.append((changes[change_type], attrib_name, attrs[attrib_name]))
            except KeyError as e:
                if change_type == 'delete':
                    # mod_vals is allowed to be None when performing a delete
                    modlist.append((changes[change_type], attrib_name, None))
                else:
                    raise KeyError('No value found to modify. Check your LDIF syntax.') from e

    return modlist
