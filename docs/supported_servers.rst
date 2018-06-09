Supported servers
===========================

Though the underlying ldap3 API that ezldap is built on
`supports virtually all vendors <https://ldap3.readthedocs.io/features.html>`_,
ezldap is currently only tested against OpenLDAP.
Most ezldap operations will likely work against all LDAP server implementations,
though this has not been tested!

What happens if an operation fails?
In all likelihood, nothing -
the server will refuse to perform the operation and ezldap will raise an error.
That said, there are bound to be bugs until ezldap has test cases targeting other
LDAP server implementations.

If you encounter a bug,
please raise an issue on the issue tracker on `Github <https://github.com/jstaf/ezldap/issues>`_.

The current list of LDAP servers I intend to add compatibility for is as follows:

* OpenLDAP (done)
* 389 Directory Server / FreeIPA
* Active Directory
