'''
Bind to an LDAP directory and perform various operations.
'''

import sys
import getpass
import re
import copy

import ldap3

from .ldif import read_ldif
from .password import ssha_passwd
from .config import config


def auto_bind(conf=None):
    '''
    Automatically detects LDAP config values and returns a directory binding.
    '''
    if conf is None:
        conf = config()

    if conf['binddn'] is not None and conf['bindpw'] is None:
        print('Enter bind DN password...', file=sys.stderr)
        conf['bindpw'] = getpass.getpass()

    return Connection(conf['host'], user=conf['binddn'], password=conf['bindpw'])


class Connection(ldap3.Connection):
    '''
    An object-oriented wrapper around an LDAP connection.
    Used to make pyldap's LDAPObject even easier to use.
    To automatically create a binding use auto_bind() instead.
    '''

    def __init__(self, host, user=None, password=None, authentication=ldap3.SIMPLE):
        self.server = ldap3.Server(host, get_info=ldap3.ALL)
        if user is None:
            # anonymous bind
            super().__init__(self.server)
        else:
            super().__init__(self.server, user=user, password=password, authentication=authentication)
        # TODO negotiate TLS before binding in all cases,
        # only cleartext in case of user override
        self.bind()


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


    def search_ldif():
        #TODO needs implementation
        pass


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
        Return given user as a dict. Searches entire directory if no base search
        dn given.
        '''
        if basedn is None:
            basedn = self.base_dn()

        return self.search_list('({}={})'.format(index, user), search_base=basedn)[0]


    def get_group(self, group, basedn=None, index='cn'):
        '''
        Return a given group. Searches entire directory if no base search dn given.
        '''
        return self.get_user(group, basedn=basedn, index=index)


    def ldif_add(self, ldif):
        """
        Perform an add operation using an LDIF object.
        """
        for entry in ldif:
            entry_cp = copy.deepcopy(entry)
            dn = entry_cp.pop('dn')
            objectclass = entry_cp.pop('objectClass')
            self.add(dn=dn, object_class=objectclass, attributes=entry_cp)


    def ldif_modify(self, ldif):
        """
        Perform an LDIF modify operation from an LDIF object.
        """
        for entry in ldif:
            modlist = _create_modify_modlist(entry)
            self.modify(dn, modlist)


    def modify_replace(self, dn, attrib, value):
        '''
        Change a single attribute on an object.
        '''
        self.modify(dn, {attrib: [(ldap3.MODIFY_REPLACE, [value] )] })


    def modify_add(self, dn, attrib, value):
        '''
        Add a single attribute to an object.
        '''
        self.modify(dn, {attrib: [(ldap3.MODIFY_ADD, [value] )] })


    def modify_delete(self, dn, attrib, value=None):
        '''
        Delete a single attribute from an object.
        If value is None, deletes all attributes of that name.
        '''
        self.modify(dn, {attrib: [(ldap3.MODIFY_DELETE, [value] )] })


    def add_group(self, groupname, conf=None,
        ldif_path='~/.ezldap/ldap-add-group.ldif', **kwargs):
        """
        Adds a group from an LDIF template.
        """
        replace = {'groupname': groupname, 'gid': self.next_gidn()}

        if conf is None:
            conf = config()

        replace.update(conf)
        replace.update(kwargs)

        ldif = read_ldif(ldif_path, replace)
        self.ldif_add(ldif)


    def add_to_group(self, username, groupname, conf=None,
        ldif_path='~/.ezldap/ldap-add-user-to-group.ldif', **kwargs):
        """
        Adds a user to a group.
        The user and group in question must already exist.
        """
        replace = {'username': username, 'groupname': groupname}

        if conf is None:
            conf = config()

        replace.update(conf)
        replace.update(kwargs)

        ldif = read_ldif(ldif_path, replace)
        self.ldif_modify(ldif)


    def add_user(self, username, groupname, password, conf=None,
        ldif_path='~/.ezldap/ldap-add-user.ldif', **kwargs):
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

        ldif = read_ldif(ldif_path, replace)
        self.ldif_add(ldif)
