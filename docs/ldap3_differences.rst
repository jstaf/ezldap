ldap3 and ezldap compatibility
=================================

At its heart, ezldap is is an extension to the
`ldap3 <https://ldap3.readthedocs.io/>`_ package,
specifically the `ldap3.Connection <https://ldap3.readthedocs.io/connection.html>`_
class. The ezldap Connection class extends ldap3.Connection with additional
convenience methods and streamlines working with an active LDAP connection.
ezldap is 100% compatible with the ldap3 API with a few notable exceptions:

Differences in search
-----------------------------------

The ``search_list()``, ``search_list_t()``, and ``search_df()`` methods
provide differently formatted output than ldap3's ``search()``
(which is still available for use).
``search_list()`` treats returned entries as a list of dicts,
one for each entry, with each attribute/objectClass/DN as a list in the dict.
ldap3's ``search()`` returns a list of nested dictionaries,
with DNs, objectClasses, and attributes handled separately.
This simplification was made for convenience -
ldap3's deep nesting of search results and inconsistent output format was
inconvenient to parse and prone to error.

LDIF parser
-----------------------------------

The ezldap LDIF parsing and writing functions work in the same manner as
the search functionality and produce identical output.
As such, the LDIF writing tools and ldapadd/ldapchange functionality will only
work when used with the corresponding ezldap functions.
