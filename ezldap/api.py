'''
Bind to an LDAP directory and perform various operations.
'''

import sys
import getpass
import copy
import re
import sys

import ldap3
from ldap3.core.exceptions import LDAPSocketOpenError, LDAPStartTLSError, \
    LDAPSessionTerminatedByServerError, LDAPSocketReceiveError

from .ldif import ldif_read
from .password import ssha_passwd
from .config import config


def ping(uri):
    '''
    Returns true if an LDAP server is responding at a given URI by attempting
    an anonymous bind.
    '''
    try:
        con = Connection(uri)
        con.unbind()
        return True
    except (LDAPSocketOpenError, LDAPSessionTerminatedByServerError,
        LDAPSocketReceiveError):
        return False


def supports_starttls(uri):
    '''
    Determine if the server actually supports StartTLS (both the server software
    itself supports it, and the server instance itself has been configured with
    SSL support).
    '''
    try:
        con = ldap3.Connection(uri, auto_bind=ldap3.AUTO_BIND_TLS_BEFORE_BIND)
        con.unbind()
        return True
    except (LDAPStartTLSError, LDAPSocketOpenError, LDAPSessionTerminatedByServerError):
        return False


def auto_bind(conf=None):
    '''
    Automatically detects LDAP config values and returns a directory binding.
    '''
    if conf is None:
        conf = config()

    if conf['binddn'] is not None and conf['bindpw'] is None:
        conf['bindpw'] = getpass.getpass('Enter bind DN password...')

    return Connection(conf['host'], user=conf['binddn'], password=conf['bindpw'])


class Connection(ldap3.Connection):
    '''
    An object-oriented wrapper around an LDAP connection.
    Used to make pyldap's LDAPObject even easier to use.
    To automatically create a binding use auto_bind() instead.
    '''
    def __init__(self, host, user=None, password=None, authentication=ldap3.SIMPLE):
        if host is None:
            raise ValueError('LDAP host cannot be None.')

        # for whatever reason, ldap3 can't deal with ldap:/// identifiers
        host = re.sub(r'///', '//localhost', host)

        self.server = ldap3.Server(host, get_info=ldap3.ALL)
        if supports_starttls(host):
            auto_bind_mode = ldap3.AUTO_BIND_TLS_BEFORE_BIND
        else:
            print('Warning, server does not appear to support SSL/StartTLS, '
                'proceeding without...', file=sys.stderr)
            auto_bind_mode = ldap3.AUTO_BIND_NO_TLS

        if user is None:
            # anonymous bind
            super().__init__(self.server, auto_bind=auto_bind_mode)
        else:
            super().__init__(self.server,
                user=user, password=password, authentication=authentication,
                auto_bind=auto_bind_mode)


    def __enter__(self):
        return self


    def __exit__(self, type_, value, traceback):
        '''
        Auto-unbind when used with "with" keyword.
        '''
        self.unbind()


    def who_am_i(self):
        '''
        Easier wrapper around who_am_i().
        '''
        return self.extend.standard.who_am_i()


    def base_dn(self):
        """
        Detect the base DN from an LDAP connection.
        """
        return self.server.info.naming_contexts[0]


    def search_list(self, search_filter='(objectClass=*)',
                    attributes=ldap3.ALL_ATTRIBUTES, search_base=None, **kwargs):
        '''
        A wrapper around search() with better defaults and output format.
        A list of dictionaries will be returned, with one dict per output object.
        If search_base is None, the directory base DN will be used.
        '''
        if search_base is None:
            search_base = self.base_dn()

        self.search(search_base, search_filter, attributes=attributes, **kwargs)
        query = []
        for res in self.response:
            result = {'dn': [res['dn']]}
            # ensure every attribute is encapsulated in a list
            for k, v in res['attributes'].items():
                if not isinstance(v, list):
                    res['attributes'][k] = [v]

            result.update(res['attributes'])
            query.append(result)

        return query


    def search_list_t(self, search_filter='(objectClass=*)',
                      attributes=ldap3.ALL_ATTRIBUTES, search_base=None,
                      unpack_lists=True, unpack_delimiter='|', **kwargs):
        '''
        A utility function that returns the transposed result of search_list()
        (a dict of lists, with one list per attribute.)
        This is very useful for tasks like retrieving all uidNumbers currently
        assigned or emails used by users. The DN of each entry is always output.
        '''
        response = self.search_list(search_filter, attributes=attributes,
            search_base=search_base, **kwargs)

        all_attribs = {'dn'}
        if attributes == ldap3.ALL_ATTRIBUTES:
            # iterate through and determine all possible attributes returned
            for res in response:
                all_attribs.update(res.keys())
        elif attributes is None:
            # skip over this case, we do not want a list of None
            pass
        else:
            if not isinstance(attributes, list):
                attributes = [attributes]

            all_attribs.update(attributes)

        query = {attrib: [] for attrib in all_attribs}

        for res in response:
            for k in all_attribs:
                try:
                    v = res[k]
                    if unpack_lists and isinstance(v, list):
                        if len(v) > 1:
                            # coerces to string
                            v = unpack_delimiter.join([str(x) for x in v])
                        else:
                            # string coercion avoided for 1-element lists
                            v = v[0]

                except KeyError:
                    v = None

                query[k].append(v)

        return query


    def search_df(self, search_filter='(objectClass=*)',
                  attributes=ldap3.ALL_ATTRIBUTES, search_base=None, **kwargs):
        '''
        A convenience function to search an LDAP directory and return a Pandas
        DataFrame. Very useful for analyzing the contents of your directory,
        computing stats, etc. Requires the pandas package to be installed.
        '''
        try:
            from pandas import DataFrame
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError('This function requires the pandas package to be installed.') from e

        query = self.search_list_t(search_filter, attributes=attributes,
            search_base=search_base, **kwargs)
        return DataFrame(query)


    def exists(self, dn):
        '''
        Returns true if a given DN exists in an LDAP directory.
        '''
        query = self.search_list(search_base=dn, search_scope=ldap3.BASE)
        if len(query) == 1:
            return True
        else:
            return False


    def next_uidn(self, search_filter='(objectClass=posixAccount)',
        search_base=None, uid_start=10000, uid_attribute='uidNumber'):
        """
        Determine the next available uid number in a directory tree.
        """
        users = self.search_list_t(search_filter, uid_attribute, search_base=search_base)
        if len(users['dn']) == 0:
            return uid_start

        return max(users[uid_attribute]) + 1


    def next_gidn(self, search_filter='(objectClass=posixGroup)',
        search_base=None, gid_start=10000, gid_attribute='gidNumber'):
        """
        Determine the next available gid number in a directory tree.
        """
        return self.next_uidn(search_filter, search_base, gid_start, gid_attribute)


    def get_user(self, user, basedn=None, index='uid'):
        '''
        Return given user as a dict or None if none is found. Searches entire
        directory if no base search dn given.
        '''
        if basedn is None:
            basedn = self.base_dn()

        try:
            return self.search_list('({}={})'.format(index, user), search_base=basedn)[0]
        except IndexError:
            return None


    def get_group(self, group, basedn=None, index='cn'):
        '''
        Return a given group. Searches entire directory if no base search dn given.
        '''
        return self.get_user(group, basedn=basedn, index=index)


    def ldif_add(self, ldif):
        """
        Perform an add operation using an LDIF object.
        """
        results = []
        for entry in ldif:
            entry_cp = copy.deepcopy(entry)
            dn = entry_cp.pop('dn')[0]
            #TODO fix for 389 directory server and "objectClasses"
            objectclass = entry_cp.pop('objectClass')
            self.add(dn=dn, object_class=objectclass, attributes=entry_cp)
            results.append(self.result)

        return results


    def ldif_modify(self, ldif):
        """
        Perform an LDIF modify operation from an LDIF object.
        """
        results = []
        for entry in ldif:
            entry_cp = copy.deepcopy(entry)
            dn = entry_cp.pop('dn')[0]
            self.modify(dn, entry_cp)
            results.append(self.result)

        return results


    def modify_replace(self, dn, attrib, value, replace_with=None):
        '''
        Change a single attribute on an object.
        '''
        if value is None:
            raise ValueError('value cannot be None when performing a replace operation.')

        if replace_with is None:
            self.modify(dn, {attrib: [(ldap3.MODIFY_REPLACE, [value] )] })
        else:
            self.modify_delete(dn, attrib, value)
            self.modify_add(dn, attrib, replace_with)

        return self.result


    def modify_add(self, dn, attrib, value):
        '''
        Add a single attribute to an object.
        '''
        if value is None:
            raise ValueError('value cannot be None when performing an add operation.')

        self.modify(dn, {attrib: [(ldap3.MODIFY_ADD, [value] )] })
        return self.result


    def modify_delete(self, dn, attrib, value=None):
        '''
        Delete a single attribute from an object.
        If value is None, deletes all attributes of that name.
        '''
        if value is None:
            self.modify(dn, {attrib: [(ldap3.MODIFY_DELETE, [] )] })
        else:
            self.modify(dn, {attrib: [(ldap3.MODIFY_DELETE, [value] )] })

        return self.result


    def add_group(self, groupname, conf=None,
        ldif_path='~/.ezldap/add_group.ldif', **kwargs):
        """
        Adds a group from an LDIF template.
        """
        replace = {'groupname': groupname, 'gid': self.next_gidn()}

        if conf is None:
            conf = config()

        replace.update(conf)
        replace.update(kwargs)

        ldif = ldif_read(ldif_path, replace)
        return self.ldif_add(ldif)


    def add_to_group(self, username, groupname, conf=None,
        ldif_path='~/.ezldap/add_to_group.ldif', **kwargs):
        """
        Adds a user to a group.
        The user and group in question must already exist.
        """
        replace = {'username': username, 'groupname': groupname}

        if conf is None:
            conf = config()

        replace.update(conf)
        replace.update(kwargs)

        ldif = ldif_read(ldif_path, replace)
        return self.ldif_modify(ldif)


    def add_user(self, username, groupname, password, conf=None,
        ldif_path='~/.ezldap/add_user.ldif', **kwargs):
        '''
        Adds a user. Does not create or modify groups.
        "groupname" may be None if "gid" is specified.
        '''
        replace = {'username': username,
                   'user_password': ssha_passwd(password),
                   'uid': self.next_uidn(),
                   'gid': None}

        if conf is None:
            conf = config()

        replace.update(conf)
        replace.update(kwargs)
        if replace['gid'] is None:
            try:
                replace['gid'] = self.get_group(groupname)['gidNumber'][0]
            except IndexError:
                raise ValueError('Group does not exist')

        ldif = ldif_read(ldif_path, replace)
        return self.ldif_add(ldif)
