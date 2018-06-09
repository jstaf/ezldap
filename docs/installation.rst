Installation
===============================================

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
