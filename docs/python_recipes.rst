==============================
Python recipes
==============================

This is a "recipe book" of things that can be done using the ezldap Python API.
These examples all assume that you've imported the `ezldap` package like so:

::

  import ezldap

You *must* run ``ezldap config`` on the command-line before the package will work.

Bind to a directory
============================

Anonymous bind
----------------------------

::

  connection = ezldap.Connection('ldap:///')

Bind using your credentials in ``~/.ezldap``
------------------------------------------------

::

  connection = ezldap.auto_bind()

Bind manually
-------------------------------------

::

  connection = ezldap.Connection('ldap:///', user='cn=someuser,dc=example,dc=com',
      password='password')

Unbind from a directory
-----------------------------

::

  connection.unbind()

Recommended workflow
------------------------------

Though it is possible to define a connection and later unbind.
It is often easier to just use the ``with`` keyword, that will unbind for you.

::

  with ezldap.auto_bind() as con:
      # do something with the "con" connection

(More documentation is on its way here, taking a break for now...)
