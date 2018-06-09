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

  connection = ezldap.Connection('ldap://localhost')

Bind using your credentials in ``~/.ezldap``

::

  connection = ezldap.auto_bind()
