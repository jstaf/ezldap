==================================
ezldap - LDAP, but easier.
==================================

ezldap is an object-oriented Python LDAP API and command-line LDAP client to
make working with your directory server as fast and easy as possible.

Although several very comprehensive LDAP API's currently exist (notably
python-ldap and ldap3), neither are particularly easy to use and generally focus
more on the specifics of communicating via LDAP rather than exposing an easy to
use high-level API. This package is designed to do that. The target audience of
this package is system administrators and support staff who are on a timeline
and just need to add a user or write a quick script in a portable manner.

So how is ezldap different? It is a wrapper around the ldap3 API that gives
access to easily perform a number of high-level tasks like searching an LDAP
directory, adding a user and sending them an email, or resetting someone's
password securely. This process is streamlined by a configuration script that
autodetects as many LDAP configuration values as possible and automates future
connections to the directory server. Additionally, additions to an LDAP
directory are performed using a set of configurable LDIF templates, making it
very quick to customize the behavior of certain actions (like adding a group).
Finally, for most tasks, a command-line interface is provided, for users who
just want to get started doing stuff.

Python example:

::

  import ezldap

  with ezldap.auto_bind() as con:
      con.add_user('username', 'groupname', 'password')

Command-line example:

::

  # a password will be automatically generated
  ezldap add_user username groupname

For a quick tour of what ezldap can do, why not check out the package `walkthrough </tutorial.html>`_?

.. toctree::
   :maxdepth: 3
   :hidden:
   :Caption: Getting started

   installation
   configuration
   tutorial

.. toctree::
   :maxdepth: 3
   :hidden:
   :Caption: API documentation

   bash_recipes
   python_recipes
   python_api
   ldap3_differences

.. toctree::
   :maxdepth: 3
   :hidden:
   :Caption: Other topics

   security
   supported_servers
