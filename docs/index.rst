.. toctree::
   :maxdepth: 2
   :caption: Contents:

==================================
ezldap - LDAP, but easier.
==================================

ezldap is designed to do two things well:

* Provide a high-level Python API that makes scripting LDAP-related operations realllllyyy easy.

* Provide a command-line interface that offers the same functionality as the Python API. No one should need to know Python/Perl/etc. to be able to work with an LDAP directory to its fullest extent.

Installation
================================

ezldap has no dependencies aside from any currently supported version of Python 3.
ezldap is tested against all current versions of Python 3 (3.4, 3.5, and 3.6).
To install ezldap, just use pip:

::

  pip install ezldap
  ezldap config

To install the development version from Github.
It is *highly* suggested to run the tests if you will be working with the development version.

::

  # install github release
  pip install git+https://github.com/jstaf/ezldap.git
  ezldap config

  # to run tests
  pip install pytest pytest-docker pytest-cov docker-compose
  pytest

Recipes
=================================================

These are a set of "recipes" designed to demonstrate common use cases of this package:

* :ref:`Bash recipes`
* :ref:`Python recipes`
