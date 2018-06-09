Configuration
=========================

Configure ezldap before use
---------------------------------------

Both the Python API and the command line client use a set of config values and
LDIF templates stored in ``~/.ezldap/``. To create these configs, run the
following command:

::

  ezldap config

Sample output (default values are in brackets, just press ``Enter`` to accept
the defaults and move to the next option):

::

  LDAP host [ldap:///]:
  Bind DN (leave blank for anonymous bind) [cn=Manager,dc=ezldap,dc=io]:
  Bind password (leave blank to prompt for password) [password]:
  User base dn [ou=People,dc=ezldap,dc=io]:
  Group base dn [ou=Group,dc=ezldap,dc=io]:
  Host base dn [ou=Hosts,dc=ezldap,dc=io]:
  Default home directory for new users [/home]:

Delete your ezldap configuration
-------------------------------------

To delete an ezldap configuration and start from a clean slate, it's as easy as:

::

  rm -r ~/.ezldap
